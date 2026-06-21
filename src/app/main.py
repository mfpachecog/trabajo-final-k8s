"""
Task Manager API
================
Microservicio REST sencillo para la gestión de tareas (to-do list).

Construido con FastAPI. Expone operaciones CRUD sobre tareas almacenadas
en memoria. Está pensado para demostrar un flujo cloud-native completo:
Docker -> Helm -> Kubernetes -> ArgoCD -> CI/CD.

El microservicio lee la variable de entorno APP_ENV para identificar el
entorno en el que se está ejecutando (p. ej. "Desarrollo" o "Producción"),
lo que permite verificar visualmente que los overrides de Helm funcionan.
"""

import os
from datetime import datetime, timezone
from itertools import count
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------

# Entorno de ejecución. Se inyecta desde Kubernetes/Helm mediante una variable
# de entorno. Si no existe, asumimos "Local" para ejecución fuera del clúster.
APP_ENV = os.getenv("APP_ENV", "Local")
APP_VERSION = "1.0.0"

app = FastAPI(
    title="Task Manager API",
    description="Microservicio de gestión de tareas para despliegue en Kubernetes con GitOps.",
    version=APP_VERSION,
)

# ---------------------------------------------------------------------------
# Modelos de datos (esquemas de entrada/salida)
# ---------------------------------------------------------------------------


class TaskCreate(BaseModel):
    """Datos requeridos para crear una tarea."""

    title: str = Field(..., min_length=1, max_length=120, description="Título de la tarea")
    description: Optional[str] = Field(None, max_length=500, description="Detalle opcional")


class Task(TaskCreate):
    """Representación completa de una tarea almacenada."""

    id: int
    completed: bool = False
    created_at: str


# ---------------------------------------------------------------------------
# "Base de datos" en memoria
# ---------------------------------------------------------------------------
# Para mantener el microservicio simple y autocontenido usamos un diccionario
# en memoria. En un caso real esto sería una base de datos externa.

_tasks: dict[int, Task] = {}
_id_sequence = count(start=1)


# ---------------------------------------------------------------------------
# Endpoints de salud y metadatos (usados por Kubernetes)
# ---------------------------------------------------------------------------


@app.get("/", tags=["meta"])
def root() -> dict:
    """Información general del servicio y entorno actual."""
    return {
        "service": "Task Manager API",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "message": f"Servicio en línea ejecutándose en entorno: {APP_ENV}",
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Liveness/readiness probe para Kubernetes."""
    return {"status": "ok", "environment": APP_ENV, "timestamp": datetime.now(timezone.utc).isoformat()}


# ---------------------------------------------------------------------------
# Endpoints CRUD de tareas
# ---------------------------------------------------------------------------


@app.get("/api/v1/tasks", response_model=list[Task], tags=["tasks"])
def list_tasks() -> list[Task]:
    """Devuelve todas las tareas registradas."""
    return list(_tasks.values())


@app.post("/api/v1/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> Task:
    """Crea una nueva tarea."""
    task = Task(
        id=next(_id_sequence),
        title=payload.title,
        description=payload.description,
        completed=False,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _tasks[task.id] = task
    return task


@app.get("/api/v1/tasks/{task_id}", response_model=Task, tags=["tasks"])
def get_task(task_id: int) -> Task:
    """Obtiene una tarea por su identificador."""
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return task


@app.put("/api/v1/tasks/{task_id}/complete", response_model=Task, tags=["tasks"])
def complete_task(task_id: int) -> Task:
    """Marca una tarea como completada."""
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    task.completed = True
    _tasks[task_id] = task
    return task


@app.delete("/api/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int) -> None:
    """Elimina una tarea."""
    if task_id not in _tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    del _tasks[task_id]
