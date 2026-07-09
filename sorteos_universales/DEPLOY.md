# 🌌 Sorteos Universales — Guía de Despliegue a Internet

## Opción 1: Render (Recomendado — Gratis)

### Pasos:

1. **Crea una cuenta en Render:**
   - Ve a https://render.com
   - Regístrate con GitHub o email

2. **Sube el proyecto a GitHub:**
   ```bash
   cd sorteos_universales
   git init
   git add .
   git commit -m "Sorteos Universales v1"
   git remote add origin https://github.com/TU_USUARIO/sorteos-universales.git
   git push -u origin main
   ```

3. **Conecta tu repositorio a Render:**
   - En Render, click en "New +" → "Web Service"
   - Selecciona "Deploy from GitHub"
   - Elige tu repositorio `sorteos-universales`
   - **Name:** sorteos-universales
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - Click en "Create Web Service"

4. **Configura la base de datos:**
   - Render usará SQLite que se guarda en la instancia
   - Primera carga: automáticamente crea la BD con datos semilla

5. **¡Listo!** Tu sitio estará en `https://sorteos-universales-xxxx.onrender.com`

---

## Opción 2: Railway

### Pasos:

1. **Ve a https://railway.app**
2. **Login con GitHub**
3. **Nuevo Proyecto** → **Deploy from GitHub repo**
4. **Selecciona** `sorteos-universales`
5. Railway detecta automáticamente que es Flask
6. **Deploy** — Se levanta en 2-3 minutos
7. Tu URL estará en Railway Dashboard

---

## Opción 3: PythonAnywhere (Para no usar Git)

### Pasos:

1. Ve a https://www.pythonanywhere.com
2. Crea cuenta gratis
3. Sube archivos manualmente:
   - **Files** → arrastra carpeta `sorteos_universales`
4. Crea una aplicación web:
   - **Web** → **Add a new web app**
   - Python 3.11
   - Flask
   - Source code: `/home/TUUSUARIO/sorteos_universales`
5. Reinicia la aplicación

---

## Checklist antes de desplegar

- ✅ `Procfile` creado con `web: gunicorn app:app`
- ✅ `requirements.txt` con gunicorn incluido
- ✅ `.gitignore` creado para excluir archivos innecesarios
- ✅ Admin privado y oculto del público
- ✅ Tests pasados ✓

---

## Variables de entorno (Opcional)

Si quieres cambiar la secret key en producción, añade en tu plataforma:

```
SECRET_KEY=tu-super-secret-key-aqui
```

En `app.py` ya lee de `os.environ.get('SECRET_KEY', '...')`.

---

## Datos de Admin por Defecto

- **Email:** admin@sorteos.com
- **Contraseña:** admin123

**Cambia esto después de deployar** en el panel de Administración.

---

## Dominio Personalizado

Después de deployar, puedes conectar tu dominio propio:

### En Render:
- Settings → Custom Domain
- Apunta el DNS de tu dominio a Render

### En Railway:
- Settings → Domains
- Agrega tu dominio

---

## Soporte

Si algo falla:
1. Revisa los **Logs** en la plataforma
2. Asegúrate que `Procfile` y `requirements.txt` sean correctos
3. Verifica que todas las plantillas HTML existan
4. Comprueba que no haya archivos `.pyc` sin limpiar

---

**¡Listo!** Tu plataforma de sorteos ya estará en vivo 🚀
