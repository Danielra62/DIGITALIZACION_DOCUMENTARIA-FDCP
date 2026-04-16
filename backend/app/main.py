from fastapi import FastAPI
from app.routers import auth, alumnos, documentos, usuarios, historial, escuelas
from app.models import escuela # Importar el modelo de escuela

app = FastAPI()

app.include_router(auth.router)
app.include_router(alumnos.router)
app.include_router(documentos.router)
app.include_router(usuarios.router)
app.include_router(historial.router)
app.include_router(escuelas.router)


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"], # Origen de tu Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"] 
)