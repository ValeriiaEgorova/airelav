import os
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session, engine
from models import GenerationTask
from core import generate_and_run

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
@app.post("/generate")
async def start_generation(
    prompt: str, 
    file_format: str, 
    background_tasks: BackgroundTasks, 
    session: Session = Depends(get_session)
):
    task = GenerationTask(prompt=prompt, file_format=file_format)
    session.add(task)
    session.commit()
    session.refresh(task)

    background_tasks.add_task(run_generation_wrapper, task.id)
    
    return {"task_id": task.id, "message": "Генерация запущена"}
@app.get("/history")
async def get_history(session: Session = Depends(get_session)):
    tasks = session.exec(select(GenerationTask).order_by(GenerationTask.created_at.desc())).all()
    return tasks
@app.get("/download/{task_id}")
async def download_file(task_id: int, session: Session = Depends(get_session)):
    task = session.get(GenerationTask, task_id)
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(task.file_path, filename=os.path.basename(task.file_path))
def run_generation_wrapper(task_id: int):
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