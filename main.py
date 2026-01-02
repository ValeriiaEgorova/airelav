import io
import os
from typing import Any

import pandas as pd
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, desc, select

from auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from core import generate_and_run
from database import create_db_and_tables, engine, get_session
from models import Conversation, GenerationTask, User

app = FastAPI(title="SynthGen AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.post("/auth/register")
def register(
    email: str, password: str, session: Session = Depends(get_session)
) -> dict[str, Any]:
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=email, hashed_password=get_password_hash(password))
    session.add(new_user)
    session.commit()
    return {"message": "User created successfully"}


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    return session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.created_at))
    ).all()


@app.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    chat = session.get(Conversation, conversation_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    tasks = session.exec(
        select(GenerationTask)
        .where(GenerationTask.conversation_id == conversation_id)
        .order_by(GenerationTask.created_at)
    ).all()
    return tasks


@app.delete("/history/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    chat = session.get(Conversation, conversation_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    tasks = session.exec(
        select(GenerationTask).where(GenerationTask.conversation_id == conversation_id)
    ).all()
    for task in tasks:
        if task.file_path and os.path.exists(task.file_path):
            try:
                os.remove(task.file_path)
            except OSError:
                pass

    session.delete(chat)
    session.commit()
    return {"message": "Conversation deleted"}


@app.post("/generate")
async def start_generation(
    prompt: str,
    background_tasks: BackgroundTasks,
    conversation_id: int | None = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    previous_code = None

    if not conversation_id:
        title = prompt[:40] + "..." if len(prompt) > 40 else prompt
        new_chat = Conversation(title=title, user_id=current_user.id)
        session.add(new_chat)
        session.commit()
        session.refresh(new_chat)
        conversation_id = new_chat.id
    else:
        chat = session.get(Conversation, conversation_id)
        if not chat or chat.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        last_task = session.exec(
            select(GenerationTask)
            .where(GenerationTask.conversation_id == conversation_id)
            .where(GenerationTask.status == "completed")
            .order_by(desc(GenerationTask.created_at))
        ).first()

        if last_task:
            previous_code = last_task.generated_code

    task = GenerationTask(
        prompt=prompt,
        file_format="pkl",
        user_id=current_user.id,
        conversation_id=conversation_id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    if task.id is None:
        raise HTTPException(status_code=500, detail="Database error: Task ID missing")

    background_tasks.add_task(run_generation_wrapper, task.id, previous_code)

    return {
        "task_id": task.id,
        "conversation_id": conversation_id,
        "message": "Генерация запущена",
    }


# @app.get("/history")
# async def get_history(
#     current_user: User = Depends(get_current_user),
#     session: Session = Depends(get_session),
# ) -> Any:
#     tasks = session.exec(
#         select(GenerationTask)
#         .where(GenerationTask.user_id == current_user.id)
#         .order_by(desc(GenerationTask.created_at))
#     ).all()
#     return tasks


@app.get("/download/{task_id}")
async def download_file(
    task_id: int, format: str = "csv", session: Session = Depends(get_session)
) -> StreamingResponse:
    task = session.get(GenerationTask, task_id)
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Файл данных не найден")

    try:
        df = pd.read_pickle(task.file_path)

        stream = io.BytesIO()

        if format == "csv":
            df.to_csv(stream, index=False, encoding="utf-8-sig")
            media_type = "text/csv"
            filename = f"dataset_{task_id}.csv"
        elif format == "json":
            df.to_json(stream, orient="records", force_ascii=False, indent=4)
            media_type = "application/json"
            filename = f"dataset_{task_id}.json"
        elif format == "xlsx":
            df.to_excel(stream, index=False)
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename = f"dataset_{task_id}.xlsx"
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка конвертации: {str(e)}"
        ) from e


def run_generation_wrapper(task_id: int, previous_code: str | None = None) -> None:
    with Session(engine) as session:
        task = session.get(GenerationTask, task_id)
        if not task:
            return

        def update_progress(msg: str, percent: int) -> None:
            task.status_message = msg
            task.progress = percent
            session.add(task)
            session.commit()

        try:
            task.status = "processing"
            session.add(task)
            session.commit()

            result = generate_and_run(
                user_query=task.prompt,
                task_id=task_id,
                previous_code=previous_code,
                on_progress=update_progress,
            )

            if result["status"] == "success":
                task.status = "completed"
                task.file_path = result["file"]
                task.generated_code = result["code"]
                task.preview_data = result.get("preview")
                task.file_size = result.get("file_size")
                task.row_count = result.get("row_count")
                task.progress = 100
            else:
                task.status = "failed"
                task.error_log = result["message"]

            session.add(task)
            session.commit()

        except Exception as e:
            session.rollback()
            task = session.get(GenerationTask, task_id)
            if task:
                task.status = "failed"
                task.error_log = f"Critical Error: {str(e)}"
                session.add(task)
                session.commit()
