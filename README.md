### Crear entorno virtual antes de descargar dependencias

LINUX

mkdir myproject
cd myproject
python3 -m venv .venv

WINDOWS

mkdir myproject
cd myproject
py -3 -m venv .venv

### Activar entorno virtual

LINUX

. .venv/bin/activate

WINDOWS

.venv\Scripts\activate

( Si quieres desactivar el environment usa: deactivate )


### Instalar dependencias

pip install -r requirements.txt

### Iniciar fastAPI

uvicorn main:app --reload

