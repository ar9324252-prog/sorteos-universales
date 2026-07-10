# 🌌 Sorteos Universales — Flask + SQLite

Plataforma completa de rifas con Flask, SQLAlchemy, SQLite y almacén de uploads.

## 📁 Estructura del Proyecto

```
sorteos_universales/
├── app.py                  ← Servidor Flask principal
├── database.py             ← Instancia SQLAlchemy
├── models.py               ← Modelos de BD (User, Event, Ticket, etc.)
├── requirements.txt        ← Dependencias Python
├── static/
│   ├── css/main.css        ← Estilos completos
│   ├── js/main.js          ← Lógica cliente
│   └── uploads/            ← Almacén de archivos subidos
│       ├── events/         ← Imágenes de eventos
│       ├── prizes/         ← Imágenes de premios
│       ├── qr/             ← Códigos QR de pago
│       ├── gallery/        ← Galería de contacto
│       └── videos/         ← Videos institucionales
└── templates/
    ├── base.html
    ├── index.html
    ├── eventos.html
    ├── evento_detalle.html
    ├── login.html
    ├── registro.html
    ├── nosotros.html
    ├── contacto.html
    └── admin/
        ├── base_admin.html
        ├── dashboard.html
        ├── eventos.html
        ├── evento_form.html
        ├── compradores.html
        ├── usuarios.html
        ├── contacto.html
        └── uploads.html
```

## 🚀 Instalación y Ejecución

### 1. Requisitos
- Python 3.10 o superior
- pip

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servidor
```bash
python app.py
```

### 4. Abrir en el navegador
```
http://localhost:5000
```

## 🔐 Credenciales por Defecto

| Rol           | Correo                | Contraseña |
|---------------|-----------------------|------------|
| Administrador | admin@sorteos.com     | admin123   |
| Usuario       | usuario@test.com      | user123    |

## 🗄 Base de Datos

Se crea automáticamente en `sorteos.db` (SQLite) al ejecutar por primera vez.
Incluye datos semilla: 2 eventos activos + usuario admin + contacto de prueba.

## 📤 Uploads

Los archivos subidos se guardan en `static/uploads/` organizados por carpeta:
- `events/`  → imágenes de eventos
- `prizes/`  → imágenes de premios
- `qr/`      → códigos QR de pago (admin sube su propio QR)
- `gallery/` → galería de la página de contacto
- `videos/`  → videos institucionales

Máximo permitido: **50 MB por archivo**.

## 🌐 Publicar en Internet (Opciones)

### Railway (Recomendado — gratis)
1. Crea cuenta en https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Sube el proyecto a GitHub primero
4. Railway detecta Flask automáticamente

### Render
1. https://render.com → "New Web Service"
2. Conecta tu repositorio GitHub
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`

### PythonAnywhere (opción gratis)
1. https://pythonanywhere.com
2. Sube los archivos via "Files"
3. Crea una app web Flask apuntando a `app.py`
