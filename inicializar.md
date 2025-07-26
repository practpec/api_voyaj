Crear el entorno virtual:

python -m venv venv

Activar el entorno virtual:

.\venv\Scripts\activate


Instalar dependencias:

pip install -r requirements.txt


uvicorn src.main:app --reload