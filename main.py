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
from models import GenerationTask, User

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
    """Регистрация нового пользователя"""
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
    """Вход в систему (получение JWT токена)"""
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/generate")
async def start_generation(
    prompt: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Запуск генерации данных"""
    task = GenerationTask(prompt=prompt, file_format="pkl", user_id=current_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    if task.id is None:
        raise HTTPException(status_code=500, detail="Database error: Task ID missing")

    background_tasks.add_task(run_generation_wrapper, task.id)

    return {"task_id": task.id, "message": "Генерация запущена"}


@app.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """Получение истории задач текущего пользователя"""
    tasks = session.exec(
        select(GenerationTask)
        .where(GenerationTask.user_id == current_user.id)
        .order_by(desc(GenerationTask.created_at))
    ).all()
    return tasks


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


def run_generation_wrapper(task_id: int) -> None:
    """Функция-обертка для запуска ядра в фоновом режиме"""
    with Session(engine) as session:
        task = session.get(GenerationTask, task_id)
        if not task:
            return

        def update_progress(msg, percent):
            task.status_message = msg
            task.progress = percent
            session.add(task)
            session.commit()

        try:
            task.status = "processing"
            session.add(task)
            session.commit()

            result = generate_and_run(
                user_query=task.prompt, task_id=task_id, on_progress=update_progress
            )

            if result["status"] == "success":
                task.status = "completed"
                task.file_path = result["file"]
                task.generated_code = result["code"]
                task.preview_data = result.get("preview")
                task.progress = 100
            else:
                task.status = "failed"
                task.error_log = result["message"]

            session.add(task)
            session.commit()

        except Exception as e:
            task.status = "failed"
            task.error_log = str(e)
            session.add(task)
            session.commit()
