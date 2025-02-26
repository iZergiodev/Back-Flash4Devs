# Flash4Devs Backend ⚡

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-009688?logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-3.46.1-003B57?logo=sqlite)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.36-326CE5?logo=sqlalchemy)

¡Bienvenido al repositorio de backend de **Flash4Devs**! Este repositorio contiene exclusivamente la lógica y funcionalidades del backend del proyecto, diseñado para soportar nuestra aplicación de flashcards dinámica enfocada en el aprendizaje de programación y la preparación para entrevistas. Aquí utilizamos un stack moderno y eficiente para garantizar rendimiento y escalabilidad.

---

## 🛠️ Tecnologías Utilizadas

El backend de Flash4Devs fue construido con las siguientes tecnologías:

- ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-009688?logo=fastapi) **FastAPI** - Framework web moderno y de alto rendimiento para construir APIs en Python, con soporte para tipado y documentación automática.  
- ![SQLite](https://img.shields.io/badge/SQLite-3.46.1-003B57?logo=sqlite) **SQLite** - Base de datos ligera e integrada, utilizada como nuestra solución de almacenamiento simple y eficiente.  
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.36-326CE5?logo=sqlalchemy) **SQLAlchemy** - ORM (Object-Relational Mapping) poderoso que facilita la interacción entre Python y la base de datos SQLite.

---

## 🚀 Cómo Configurar y Ejecutar

Sigue los pasos a continuación para configurar el entorno y ejecutar el backend localmente:

### 1. Crear Entorno Virtual
Antes de descargar las dependencias, crea un entorno virtual para aislar las bibliotecas del proyecto.

1. **Linux**  
   ```bash
   mkdir myproject
   cd myproject
   python3 -m venv .venv

2. **Windows**
   ```bash
   mkdir myproject
   cd myproject
   py -3 -m venv .venv
   
3. Activar Entorno Virtual en Linux
   ```bash
   pnpm dev

4. Activar Entorno Virtual en Windows
   ```bash
    .venv\Scripts\activate

5. Instalar Dependencias
Con el entorno virtual activo, instala las dependencias listadas en el archivo requirements.txt.
    ```bash
    pip install -r requirements.txt

6. Iniciar FastAPI
Ejecuta el servidor FastAPI con recarga automática para desarrollo.
    ```bash
    uvicorn main:app --reload
Tras esto, el backend estará funcionando en http://localhost:8000. Puedes acceder a la documentación interactiva de la API en http://localhost:8000/docs.

---

## 📅 Estado del Proyecto

¡Estamos en desarrollo activo! Mantente atento a las actualizaciones y nuevas funcionalidades.

*Última actualización: 26 de febrero de 2025*

---

Hecho por YagoCastelao y iZergiodev!
