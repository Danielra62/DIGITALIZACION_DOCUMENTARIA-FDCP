import os

STORAGE_PATH = "storage"

def guardar_archivo(alumno_id, file, tipo):
    folder = f"{STORAGE_PATH}/documentos/{alumno_id}"
    os.makedirs(folder, exist_ok=True)

    filepath = f"{folder}/{tipo}.pdf"

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return filepath