# Locker Digital

Locker Digital es una aplicación web desarrollada en **Python (Flask)** que permite **gestionar evidencias digitales** de forma segura, garantizando **integridad, autoría y trazabilidad** mediante técnicas criptográficas.

El sistema está diseñado bajo principios de **seguridad por diseño**, separación de roles y auditoría automática.

---

##  Objetivo del proyecto

Permitir a los usuarios **subir archivos como evidencias digitales**, generando automáticamente:

- Hash **SHA-256** (integridad)
- Firma digital **Ed25519** (autoría)
- Registro de auditoría (logs)
- Detección automática de duplicados o similitud

El sistema incluye un **panel de administración** para supervisión, **sin acceso al contenido de los archivos**, manteniendo confidencialidad.

---

##  Roles del sistema

###  Estudiante (Usuario)
- Registrarse e iniciar sesión
- Subir evidencias (PDF, DOCX, ZIP)
- Ver y verificar integridad de archivos
- Detectar duplicados automáticamente
- Eliminar evidencias propias
- Visualizar estado y alertas

###  Administrador
- Supervisar repositorio global (hash, flags, propietario)
- Consultar logs de auditoría
- Ver actividad del sistema
- **No puede ver ni descargar archivos** (principio de seguridad y confidencialidad)

---

##  Credenciales de prueba

Para facilitar la evaluación del proyecto, se incluyen las siguientes cuentas:

### Estudiante
- **Correo:** `estudiante@correo.com`
- **Contraseña:** `hola123`

### Administrador
- **Correo:** `admin@correo.com`
- **Contraseña:** `adios123`

---

##  Tecnologías utilizadas

- **Python 3.9+**
- **Flask**
- **Flask-Login**
- **SQLite**
- **bcrypt**
- **Criptografía Ed25519**
- **HTML + CSS (frontend )**
- **IA básica para detección de duplicados**

---

## Instalación y ejecución

### 1. Ubicarse en la carpeta del proyecto

**```bash 
cd locker-digital


## 2. Crear y activar entorno virtual

python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows

## 3. Instalar Dependencias
pip install -r requirements.txt

## Ejecutar App
python app.py

## Entrar al link desde la terminal, ahi esta la app
http://127.0.0.1:5000 **
=======
# secure-digital-locker
Secure web application built with Flask for managing digital evidence using cryptographic techniques such as SHA-256 hashing and Ed25519 digital signatures to ensure integrity, authorship and traceability.

