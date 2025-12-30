import os
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session, engine
from models import GenerationTask, User
from core import generate_and_run
from auth import get_password_hash, verify_password, create_access_token, get_current_user

app = FastAPI(title="SynthGen AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/auth/register")
def register(email: str, password: str, session: Session = Depends(get_session)):
    """Регистрация нового пользователя"""
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(email=email, hashed_password=get_password_hash(password))
    session.add(new_user)
    session.commit()
    return {"message": "User created successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
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
def start_generation(
    prompt: str, 
    file_format: str, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Запуск генерации данных"""
    task = GenerationTask(
        prompt=prompt, 
        file_format=file_format, 
        user_id=current_user.id 
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    background_tasks.add_task(run_generation_wrapper, task.id)
    
    return {"task_id": task.id, "message": "Генерация запущена"}

@app.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Получение истории задач текущего пользователя"""
    tasks = session.exec(
        select(GenerationTask)
        .where(GenerationTask.user_id == current_user.id)
        .order_by(GenerationTask.created_at.desc())
    ).all()
    return tasks

@app.get("/download/{task_id}")
async def download_file(
    task_id: int, 
    session: Session = Depends(get_session)
):
    """Скачивание готового файла"""
    task = session.get(GenerationTask, task_id)
    
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(task.file_path, filename=os.path.basename(task.file_path))


def run_generation_wrapper(task_id: int):
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
                user_query=task.prompt, 
                file_format=task.file_format, 
                task_id=task.id,
                on_progress=update_progress
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