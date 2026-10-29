from __future__ import annotations

import base64
import csv
import hashlib
import hmac
import io
import json
import math
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_SECRET = os.getenv("NEUROLAB_SECRET", "local-dev-secret-change-before-deploy")
DEMO_USERS = {
    "admin@neurolab.local": {"password": "NeuroLab2026!", "name": "Administrador", "role": "Administrador"},
    "analista@neurolab.local": {"password": "Analista2026!", "name": "Analista de IA", "role": "Analista"},
}

app = FastAPI(title="NeuroLab Enterprise API", version="1.1.0", description="API funcional de autenticación, proyectos, validación y experimentación neuronal.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

projects: dict[str, dict] = {}
architectures: dict[str, dict] = {}
jobs: dict[str, dict] = {}

class LoginInput(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=200)

class ProjectInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1000)
    family: Literal["Feedforward", "RNN", "CNN", "GAN"] = "Feedforward"

class ArchitectureInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    family: Literal["Feedforward", "RNN", "CNN", "GAN"]
    input_units: int = Field(gt=0, le=100000)
    hidden_layers: int = Field(ge=1, le=12)
    units_per_layer: int = Field(gt=0, le=4096)
    output_units: int = Field(gt=0, le=10000)
    activation: Literal["relu", "sigmoid", "softmax", "tanh", "linear"] = "relu"

class TrainingInput(BaseModel):
    epochs: int = Field(ge=1, le=500)
    learning_rate: float = Field(gt=0, le=1)
    seed: int = Field(default=42, ge=0, le=1000000)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def _issue_token(email: str) -> str:
    payload = {"sub": email, "exp": int((datetime.now(timezone.utc) + timedelta(hours=8)).timestamp()), "nonce": secrets.token_hex(8)}
    raw = _b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = _b64(hmac.new(APP_SECRET.encode(), raw.encode(), hashlib.sha256).digest())
    return f"{raw}.{sig}"

def _user_from_token(token: str) -> dict:
    try:
        raw, signature = token.split(".", 1)
        expected = _b64(hmac.new(APP_SECRET.encode(), raw.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
        if payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("expired")
        user = DEMO_USERS[payload["sub"]]
        return {"email": payload["sub"], "name": user["name"], "role": user["role"]}
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Sesión inválida o vencida. Inicia sesión nuevamente.") from exc

def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Debes iniciar sesión para acceder a este recurso.")
    return _user_from_token(authorization.split(" ", 1)[1].strip())

@app.get("/health")
def health():
    return {"status": "ok", "service": "neurolab-api", "version": app.version, "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/v1/auth/login")
def login(payload: LoginInput):
    email = payload.email.strip().lower()
    user = DEMO_USERS.get(email)
    if not user or not hmac.compare_digest(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    return {"access_token": _issue_token(email), "token_type": "bearer", "expires_in": 28800, "user": {"email": email, "name": user["name"], "role": user["role"]}}

@app.get("/api/v1/auth/me")
def me(user: dict = Depends(current_user)):
    return user

@app.get("/api/v1/projects")
def list_projects(user: dict = Depends(current_user)):
    items = sorted(projects.values(), key=lambda x: x["created_at"], reverse=True)
    return {"items": items, "total": len(items)}

@app.post("/api/v1/projects", status_code=201)
def create_project(payload: ProjectInput, user: dict = Depends(current_user)):
    now = datetime.now(timezone.utc).isoformat()
    item = {"id": str(uuid4()), **payload.model_dump(), "status": "En diseño", "owner": user["email"], "created_at": now, "updated_at": now}
    projects[item["id"]] = item
    return item

@app.post("/api/v1/architectures/validate")
def validate_architecture(payload: ArchitectureInput, user: dict = Depends(current_user)):
    # Validation is performed on the server, not in the React preview.
    if payload.family == "CNN" and payload.input_units < 4:
        raise HTTPException(status_code=422, detail="Para CNN se requiere una entrada de al menos 4 unidades o dimensiones de imagen.")
    if payload.family == "GAN" and payload.output_units != payload.input_units:
        raise HTTPException(status_code=422, detail="En esta versión, la salida GAN debe coincidir con la dimensión de entrada.")
    params = payload.input_units * payload.units_per_layer + max(0, payload.hidden_layers - 1) * payload.units_per_layer**2 + payload.units_per_layer * payload.output_units
    item = {"id": str(uuid4()), **payload.model_dump(), "parameter_estimate": params, "status": "validated", "validated_by": user["email"], "validated_at": datetime.now(timezone.utc).isoformat()}
    architectures[item["id"]] = item
    return {"valid": True, "message": "Configuración validada por la API.", "architecture": item, "checks": ["Rangos numéricos correctos", "Familia reconocida", "Parámetros dentro de límites", "Validaciones específicas de familia superadas"]}

@app.post("/api/v1/datasets/inspect")
async def inspect_dataset(file: UploadFile = File(...), user: dict = Depends(current_user)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="Sube un archivo .csv para inspeccionarlo.")
    content = await file.read(5_000_001)
    if len(content) > 5_000_000:
        raise HTTPException(status_code=413, detail="El archivo supera el límite de 5 MB.")
    try:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        columns = reader.fieldnames or []
        if not columns:
            raise ValueError("missing header")
        rows = list(reader)
        if not rows:
            raise ValueError("empty")
    except Exception as exc:
        raise HTTPException(status_code=422, detail="No se pudo leer el CSV. Verifica que tenga encabezados y al menos una fila.") from exc
    numeric = []
    for col in columns:
        values = [r.get(col, "").strip() for r in rows]
        present = [v for v in values if v]
        if present and all(_is_number(v) for v in present):
            numeric.append(col)
    missing = sum(1 for row in rows for col in columns if not (row.get(col) or "").strip())
    return {"filename": file.filename, "rows": len(rows), "columns": len(columns), "column_names": columns, "numeric_columns": numeric, "missing_cells": missing, "size_bytes": len(content), "valid": True, "message": "CSV leído correctamente por la API. El archivo no se guarda permanentemente."}

def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

@app.post("/api/v1/training-jobs")
def train_demo(payload: TrainingInput, user: dict = Depends(current_user)):
    # Train a small real feedforward network using TensorFlow/Keras when available.
    # If TensorFlow is not installed, use a transparent NumPy gradient-descent fallback.
    import random
    random.seed(payload.seed)
    try:
        import numpy as np
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Instala NumPy con: pip install numpy") from exc
    rng = np.random.default_rng(payload.seed)
    X = rng.normal(size=(240, 2)).astype("float32")
    y = ((X[:, 0] * 0.8 + X[:, 1] * 0.6) > 0).astype("float32").reshape(-1, 1)
    engine = "NumPy (red feedforward didáctica)"
    losses = []
    accuracies = []
    try:
        import tensorflow as tf
        tf.random.set_seed(payload.seed)
        model = tf.keras.Sequential([tf.keras.layers.Input(shape=(2,)), tf.keras.layers.Dense(8, activation="relu"), tf.keras.layers.Dense(1, activation="sigmoid")])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=payload.learning_rate), loss="binary_crossentropy", metrics=["accuracy"])
        hist = model.fit(X, y, epochs=payload.epochs, batch_size=24, verbose=0)
        losses = [round(float(v), 5) for v in hist.history["loss"]]
        accuracies = [round(float(v), 5) for v in hist.history["accuracy"]]
        engine = "TensorFlow/Keras"
    except ImportError:
        # Small one-hidden-layer MLP, trained with backpropagation; not a simulated progress bar.
        W1 = rng.normal(0, 0.4, (2, 8)).astype("float32"); b1 = np.zeros((1, 8), dtype="float32")
        W2 = rng.normal(0, 0.4, (8, 1)).astype("float32"); b2 = np.zeros((1, 1), dtype="float32")
        lr = payload.learning_rate
        for _ in range(payload.epochs):
            z1 = X @ W1 + b1; h = np.maximum(z1, 0); z2 = h @ W2 + b2
            pred = 1 / (1 + np.exp(-np.clip(z2, -30, 30)))
            loss = -np.mean(y*np.log(pred+1e-7)+(1-y)*np.log(1-pred+1e-7))
            dz2 = (pred-y)/len(X); dW2 = h.T @ dz2; db2 = dz2.sum(axis=0, keepdims=True)
            dh = dz2 @ W2.T; dz1 = dh * (z1 > 0); dW1 = X.T @ dz1; db1 = dz1.sum(axis=0, keepdims=True)
            W1 -= lr*dW1; b1 -= lr*db1; W2 -= lr*dW2; b2 -= lr*db2
            losses.append(round(float(loss), 5)); accuracies.append(round(float(np.mean((pred >= .5) == y)), 5))
    job = {"id": str(uuid4()), "status": "COMPLETED", "engine": engine, "epochs": payload.epochs, "loss": losses[-1], "accuracy": accuracies[-1], "history": [{"epoch": i+1, "loss": losses[i], "accuracy": accuracies[i]} for i in range(len(losses))], "dataset": "Dataset sintético reproducible (240 filas, 2 características)", "message": "Entrenamiento completado. Métricas calculadas a partir de la ejecución del modelo.", "created_at": datetime.now(timezone.utc).isoformat(), "created_by": user["email"]}
    jobs[job["id"]] = job
    return job

@app.get("/api/v1/training-jobs")
def list_jobs(user: dict = Depends(current_user)):
    items = sorted(jobs.values(), key=lambda x: x["created_at"], reverse=True)
    return {"items": items, "total": len(items)}

@app.get("/api/v1/training-jobs/{job_id}")
def get_job(job_id: str, user: dict = Depends(current_user)):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    return jobs[job_id]
