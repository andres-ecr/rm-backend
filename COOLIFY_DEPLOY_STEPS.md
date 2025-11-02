# 🚀 Deploy Backend en Coolify - Guía Paso a Paso

Ya tienes Coolify funcionando en **https://coolify.alchlab.com/** 🎉

Ahora vamos a desplegar tu backend Django.

---

## 📋 Pre-requisitos

- ✅ Coolify funcionando en https://coolify.alchlab.com/
- ✅ Código en GitHub (o listo para subir)
- ✅ Dockerfile creado (ya lo creamos)

---

## Paso 1: Crear Base de Datos PostgreSQL

1. **Accede a Coolify:**
   - Ve a https://coolify.alchlab.com/
   - Inicia sesión

2. **Crear Base de Datos:**
   - En el dashboard, busca **"Resources"** o **"Databases"**
   - Click **"+ New Resource"** o **"Add Database"**
   - Selecciona **PostgreSQL**

3. **Configurar:**
   - **Name:** `route-monitor-db` (o el que prefieras)
   - **Database Name:** `route_monitor`
   - **User:** `routemonitor` (o el que prefieras)
   - **Password:** Genera una contraseña segura (guárdala)
   - **Version:** PostgreSQL 15 (o la más reciente)
   - **Public Port:** Puedes dejarlo en blanco (solo acceso interno) o habilitarlo si necesitas acceso externo

4. **Create/Deploy**

**Guarda estas credenciales** - las necesitarás después.

---

## Paso 2: Asegurar que Dockerfile esté en GitHub

**Importante:** Antes de importar, asegúrate que el `Dockerfile` esté en tu repositorio GitHub:

```bash
# En tu máquina local, en la carpeta rm-backend
cd rm-backend

# Verifica que Dockerfile existe (ya lo creamos)
ls Dockerfile

# Agregar y commitear
git add Dockerfile
git add requirements.txt  # Por si acaso corregimos algo
git commit -m "Add Dockerfile for Coolify deployment"

# Push a GitHub
git push origin main
```

**Nota:** Tu repositorio puede ser **público** o **privado** (necesitarás conectar GitHub a Coolify si es privado).

---

## Paso 3: Importar desde GitHub en Coolify

**✅ MÉTODO SIMPLE - Importar directamente desde GitHub:**

1. **En Coolify Dashboard (https://coolify.alchlab.com/):**
   - Click **"+ New Resource"** o **"Add Application"**
   - Busca opción **"From GitHub"** o **"Import from GitHub"**

2. **Si es primera vez conectando GitHub:**
   - Click **"Connect GitHub"** o **"Authorize GitHub"**
   - Te pedirá permisos, autoriza
   - Esto permite a Coolify acceder a tus repositorios

3. **Seleccionar Repositorio:**
   - Coolify mostrará tus repositorios
   - Busca y selecciona el repositorio que contiene `rm-backend`
   - O el repositorio donde está tu backend Django

4. **Coolify detectará automáticamente:**
   - ✅ Tipo de aplicación (Docker/Django)
   - ✅ Dockerfile (si está en la raíz)
   - ✅ Configuración básica

5. **Configuración Automática (Coolify sugerirá):**
   - **Name:** `route-monitor-backend` (puedes cambiarlo)
   - **Build Pack:** Docker (detectado automáticamente)
   - **Dockerfile Location:** `/Dockerfile` (detectado)
   - **Port:** `8000` (detectado del Dockerfile)

6. **Ajustar si es necesario:**
   - **Branch:** Selecciona `main` o `master`
   - **Port:** `8000` (ya está bien)
   - **Public Port:** Puedes dejarlo igual o cambiarlo
   - **Domain:** Puedes configurar después
     - Ejemplo: `api.alchlab.com`

---

## Paso 4: Revisar Configuración y Ajustar

Después de importar, Coolify te mostrará la configuración detectada:

- ✅ Dockerfile detectado
- ✅ Puerto configurado
- ✅ Variables de entorno básicas

**Puedes ajustar ahora o después:**
- Cambiar nombre de aplicación
- Agregar dominio
- Configurar variables de entorno

---

## Paso 5: Configurar Variables de Entorno

Antes de hacer deploy, configura las variables de entorno:

1. En la configuración de tu aplicación, busca **"Environment Variables"** o **"Env"**

2. **Agregar las siguientes variables:**

```bash
# Django Settings
DJANGO_SECRET_KEY=tu-secret-key-aqui-genera-uno-seguro
DEBUG=false
ALLOWED_HOSTS=api.alchlab.com,backend.alchlab.com,coolify.alchlab.com

# Database (se configurará automáticamente si conectas la DB)
# DATABASE_URL se agregará automáticamente cuando conectes PostgreSQL
```

**Para generar SECRET_KEY:**
```bash
# En tu máquina local
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Importante:** Reemplaza los dominios en `ALLOWED_HOSTS` con los que vas a usar.

---

## Paso 6: Conectar Base de Datos

1. En la página de tu aplicación (después de crearla)
2. Busca **"Connections"** o **"Services"** o **"Databases"**
3. Click **"Add Connection"** o **"Connect Database"**
4. Selecciona la base de datos PostgreSQL que creaste (`route-monitor-db`)
5. Coolify automáticamente:
   - Agregará `DATABASE_URL` a las variables de entorno
   - Conectará los servicios en la misma red

**El formato de DATABASE_URL será:**
```
postgresql://usuario:password@route-monitor-db:5432/route_monitor
```

---

## Paso 7: Configurar Dominio (Opcional pero Recomendado)

1. En la configuración de tu aplicación
2. **Domains** o **Domain Settings**
3. **Add Domain:**
   - `api.alchlab.com` (ejemplo)
   - O `backend.alchlab.com`
   - O el subdominio que prefieras

4. **DNS Configuration:**
   - Necesitas agregar un registro en tu DNS de `alchlab.com`:
     - **Tipo:** A
     - **Nombre:** `api` (o el subdominio que elijas)
     - **Valor:** IP de tu VPS (donde está Coolify)
   - O si usas Cloudflare/proxy, apunta al dominio de Coolify

5. **SSL:**
   - Coolify automáticamente obtendrá certificado Let's Encrypt
   - Se renovará automáticamente

---

## Paso 8: Deploy

Una vez que importaste desde GitHub, Coolify puede:
- **Opción A:** Hacer deploy automático inmediatamente
- **Opción B:** Esperar a que hagas click en **"Deploy"** o **"Save & Deploy"**

1. Si conectaste GitHub y configuraste Auto-Deploy:
   - Cada push hará deploy automático
   - Puedes hacer push ahora para trigger el primer deploy

2. Si no tienes Auto-Deploy:
   - En la página de tu aplicación
   - Click **"Deploy"** o **"Redeploy"**

3. **Monitorear el proceso:**
   - Ve a **"Logs"** de tu aplicación
   - Verás el proceso de build en tiempo real
   - Busca errores si los hay

**El proceso incluye:**
- Clonar repositorio
- Construir Docker image
- Ejecutar `collectstatic`
- Ejecutar migraciones (via `check_db_and_migrate.py`)
- Iniciar Gunicorn

---

## Paso 9: Verificar Deployment

### Opción 1: Por dominio (si configuraste)
```
https://api.alchlab.com/api/health/
```

### Opción 2: Por IP y puerto
```
http://TU_IP_DEL_VPS:8000/api/health/
```

### Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "message": "Service is running"
}
```

### Otros endpoints para probar:
- `https://api.alchlab.com/api/` - Root API
- `https://api.alchlab.com/admin/` - Django Admin (si configuraste)

---

## Paso 10: Crear Superusuario (Opcional)

Si necesitas acceso al Django Admin:

1. En Coolify, ve a tu aplicación
2. Busca **"Execute Command"** o **"Shell"** o **"Terminal"**
3. Ejecuta:
   ```bash
   python manage.py createsuperuser
   ```
4. Sigue las instrucciones para crear usuario admin

---

## Paso 11: Actualizar Frontend

Actualiza tu frontend para que apunte al nuevo backend:

### En tu frontend (si usas Vercel/Netlify/etc):

**Agregar variable de entorno:**
- Key: `API_URL`
- Value: `https://api.alchlab.com/api` (o el dominio que configuraste)

### O actualizar `next.config.js`:
```javascript
module.exports = {
  assetPrefix: '/',
  output: 'export',
  images: {
    unoptimized: true,
  },
  env: {
    API_URL: process.env.API_URL || 'https://api.alchlab.com/api',
  },
};
```

---

## 🔧 Troubleshooting

### Problema: "Build failed"

**Solución:**
1. Ve a **Logs** de tu aplicación en Coolify
2. Revisa el error específico
3. Verifica que:
   - Dockerfile existe y está en la raíz
   - requirements.txt no tiene errores
   - Tu código está en GitHub y la rama es correcta

### Problema: "Cannot connect to database"

**Solución:**
1. Verifica que PostgreSQL esté corriendo (Status: Running)
2. Revisa `DATABASE_URL` en Environment Variables
3. Asegúrate de que conectaste la base de datos en "Connections"
4. Verifica que la aplicación y DB estén en el mismo proyecto/network

### Problema: "500 Internal Server Error"

**Solución:**
1. Revisa logs en Coolify
2. Verifica variables de entorno (especialmente `DJANGO_SECRET_KEY`)
3. Verifica `ALLOWED_HOSTS` incluye tu dominio
4. Ejecuta migraciones manualmente si es necesario

### Problema: "Static files not loading"

**Solución:**
1. Verifica que `collectstatic` se ejecutó (ver logs de build)
2. Si usas WhiteNoise, está configurado en settings.py
3. Puedes ejecutar manualmente: `python manage.py collectstatic`

### Problema: "Port already in use"

**Solución:**
1. Cambia el puerto en configuración de aplicación
2. O detén otras aplicaciones que usen el puerto 8000

---

## 📝 Checklist de Deployment

- [ ] PostgreSQL database creada en Coolify
- [ ] Código en GitHub
- [ ] Dockerfile creado y en la raíz del proyecto
- [ ] Aplicación creada en Coolify
- [ ] Variables de entorno configuradas:
  - [ ] `DJANGO_SECRET_KEY`
  - [ ] `DEBUG=false`
  - [ ] `ALLOWED_HOSTS` con tu dominio
- [ ] Base de datos conectada a la aplicación
- [ ] Dominio configurado (opcional pero recomendado)
- [ ] Deploy exitoso
- [ ] Health endpoint funciona (`/api/health/`)
- [ ] Migraciones ejecutadas (automático via `check_db_and_migrate.py`)
- [ ] Frontend actualizado con nueva API URL

---

## 🎯 URLs Finales

**Backend API:**
```
https://api.alchlab.com/api
```

**Health Check:**
```
https://api.alchlab.com/api/health/
```

**Admin Panel:**
```
https://api.alchlab.com/admin/
```

**API Root:**
```
https://api.alchlab.com/api/
```

---

## 🚀 Próximos Pasos

1. **Monitoreo:**
   - Coolify tiene logs built-in
   - Puedes agregar monitoring externo si quieres

2. **Backups:**
   - Configurar backups automáticos de PostgreSQL
   - Coolify puede hacerlo automáticamente

3. **Escalar:**
   - Si necesitas más recursos, puedes escalar en Coolify
   - O agregar más instancias

4. **Actualizaciones:**
   - Cada push a GitHub = deploy automático (si configuraste)
   - O manual desde Coolify dashboard

---

## ✅ ¡Listo!

Tu backend debería estar funcionando en:
**https://api.alchlab.com/api/** 🎉

**¿Necesitas ayuda con algún paso específico?** Avísame y te guío.

