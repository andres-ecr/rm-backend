# ⚡ Deploy Rápido en Coolify - Desde GitHub

Ya tienes Coolify en https://coolify.alchlab.com/ ✅

## 🚀 Proceso Super Simple (5 minutos)

### 1. Asegurar Dockerfile en GitHub

```bash
cd rm-backend
git add Dockerfile
git commit -m "Add Dockerfile for Coolify"
git push origin main
```

### 2. En Coolify Dashboard

1. **Click "+ New Resource"** o **"Add Application"**
2. **Selecciona "From GitHub"** o **"Import from GitHub"**
3. **Conecta GitHub** (si es primera vez):
   - Click "Connect GitHub" / "Authorize GitHub"
   - Autoriza permisos
4. **Selecciona tu repositorio** con el backend
5. **Coolify detectará automáticamente:**
   - ✅ Dockerfile
   - ✅ Puerto 8000
   - ✅ Configuración Django

### 3. Configurar Variables de Entorno

En la app creada, ve a **Environment Variables**:

```bash
DJANGO_SECRET_KEY=genera-uno-seguro
DEBUG=false
ALLOWED_HOSTS=api.alchlab.com,coolify.alchlab.com
```

**Generar SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Conectar PostgreSQL

1. **Crear DB primero** (si no la tienes):
   - Resources → Add Database → PostgreSQL
   
2. **Conectar a la app:**
   - En tu aplicación → Connections → Add Database
   - Selecciona tu PostgreSQL
   - Coolify agregará `DATABASE_URL` automáticamente

### 5. Agregar Dominio (Opcional)

- Domains → Add Domain
- Ejemplo: `api.alchlab.com`
- SSL se configura automáticamente

### 6. Deploy

- Click **"Deploy"** o **"Save & Deploy"**
- O si configuraste auto-deploy, cada push hará deploy automático

### 7. Verificar

Visita: `https://api.alchlab.com/api/health/`

Debería responder:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "message": "Service is running"
}
```

---

## ✅ ¡Listo!

**Tu backend estará en:**
```
https://api.alchlab.com/api
```

**Para detalles completos, ver:** `COOLIFY_DEPLOY_STEPS.md`

