import os

STORAGE_PATH = "storage"

def guardar_archivo(alumno, file, tipo, nombre_archivo):
    carpeta = f"storage/documentos/{alumno.id}"
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, nombre_archivo)

    # 🧹 eliminar si existe
    if os.path.exists(ruta):
        os.remove(ruta)

    # 🔥 IMPORTANTE: resetear puntero
    file.file.seek(0)

    # Guardar archivo
    with open(ruta, "wb") as buffer:
        buffer.write(file.file.read())

    return ruta