# 🚀 Deploy con Coolify en VPS - Guía Completa

## ¿Qué es Coolify?

**Coolify** es una plataforma open-source (gratis) que te permite auto-desplegar aplicaciones como Heroku/Fly.io, pero en tu propio VPS. Es como tener tu propio PaaS.

**Ventajas:**
- ✅ **Gratis** (solo pagas el VPS)
- ✅ **Control total** sobre tu servidor
- ✅ **Auto-deploy** desde GitHub
- ✅ **Soporte para Django + PostgreSQL**
- ✅ **SSL automático** con Let's Encrypt
- ✅ **One-click deployments**

---

## 💰 Costo

**Opción más barata:**
- **Hetzner CPX11: €4.75/month** (~$5/month) ⭐
- **DigitalOcean Droplet: $6/month**
- **Vultr: $6/month**

**Total: ~$5-6/month** (vs $10-15 de Fly.io o $5-7 de PythonAnywhere)

**Pero con:**
- ✅ Control total
- ✅ Múltiples apps en el mismo VPS
- ✅ Sin límites de "free tier"
- ✅ Escalable

---

## 🎯 Comparación Rápida

| Opción | Costo | Control | Dificultad | Mejor Para |
|--------|------|----------|------------|------------|
| **Coolify + VPS** | **$5-6/mes** | ⭐⭐⭐⭐⭐ Total | 🟡 Media | Múltiples apps, control |
| **PythonAnywhere** | $5-7/mes | ⭐⭐ Limitado | 🟢 Fácil | Una app, simple |
| **Fly.io** | $10-15/mes | ⭐⭐⭐ Alto | 🟡 Media | Producción, rápido |

---

## 📋 Requisitos Previos

- VPS con:
  - **Ubuntu 22.04** (recomendado) o 20.04
  - **Mínimo 2GB RAM** (4GB recomendado)
  - **Mínimo 40GB SSD**
  - **IP pública**
- Dominio (opcional, pero recomendado para SSL)
- Conocimientos básicos de Linux (o seguir la guía paso a paso)

---

## Paso 1: Elegir y Configurar VPS

### Opción A: Hetzner (Más Barato - €4.75/month)

1. **Crear cuenta:** https://www.hetzner.com
2. **Cloud Console** → **New Project**
3. **Add Server:**
   - **Image:** Ubuntu 22.04
   - **Type:** CPX11 (2GB RAM, 1 vCPU, 40GB SSD) - €4.75/month
   - **Location:** Nuremberg, Germany (o más cercano a ti)
   - **SSH Key:** Agregar tu clave SSH (o usar password)
4. **Create & Buy**

### Opción B: DigitalOcean ($6/month)

1. **Crear cuenta:** https://www.digitalocean.com
2. **Create Droplet:**
   - **Image:** Ubuntu 22.04
   - **Plan:** Basic - $6/month (1GB RAM, 1 vCPU)
   - **Datacenter:** Más cercano a ti
   - **Authentication:** SSH Key
3. **Create Droplet**

### Opción C: Vultr ($6/month)

Similar a DigitalOcean, pero con más opciones de ubicación.

---

## Paso 2: Conectar al VPS

### Windows (PowerShell o PuTTY):

```powershell
# Si tienes SSH instalado
ssh root@TU_IP_DEL_VPS

# O usar PuTTY:
# 1. Descargar PuTTY
# 2. Conectar a: root@TU_IP_DEL_VPS
# 3. Port: 22
```

### macOS/Linux:

```bash
ssh root@TU_IP_DEL_VPS
```

**Reemplaza `TU_IP_DEL_VPS` con la IP que te dio Hetzner/DigitalOcean**

---

## Paso 3: Instalar Coolify

Una vez conectado al VPS, ejecuta:

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

Esto instalará:
- Docker
- Docker Compose
- Coolify

**Tiempo: 5-10 minutos**

---

## Paso 4: Acceder a Coolify

1. Abre tu navegador
2. Ve a: `http://TU_IP_DEL_VPS:8000`
3. Verás la pantalla de setup de Coolify

### Configuración Inicial:

1. **Create Admin Account:**
   - Email
   - Password
   - Confirm Password

2. **Configure Domain (Opcional):**
   - Si tienes dominio: `app.tudominio.com`
   - Si no: Usa la IP directamente

3. **SSL:**
   - Si tienes dominio: Let's Encrypt (automático)
   - Si no: Puedes usar más tarde

---

## Paso 5: Crear Base de Datos PostgreSQL

1. En Coolify dashboard:
2. **Resources** → **Database** → **PostgreSQL**
3. **Create Database:**
   - **Name:** `route_monitor_db`
   - **Database:** `route_monitor`
   - **User:** `routemonitor`
   - **Password:** (genera uno seguro)
   - **Version:** PostgreSQL 15 (o última)
4. **Create**

Coolify creará automáticamente:
- Contenedor PostgreSQL
- Volumen para datos persistentes
- Variables de entorno con credenciales

---

## Paso 6: Preparar Tu Proyecto para Coolify

### Opción A: Deploy desde GitHub (Recomendado)

**1. Asegúrate que tu código esté en GitHub:**

```bash
# En tu máquina local
cd rm-backend
git add .
git commit -m "Prepare for Coolify deployment"
git push origin main
```

**2. Crear archivos necesarios:**

Crea `Dockerfile` (si no existe):

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD python check_db_and_migrate.py && gunicorn route_monitor.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

Crea `coolify.yml` (opcional, para configuración avanzada):

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
    volumes:
      - staticfiles:/app/staticfiles
```

### Opción B: Deploy desde Dockerfile directamente

Coolify puede construir automáticamente desde Dockerfile.

---

## Paso 7: Crear Aplicación en Coolify

1. En Coolify dashboard:
2. **Applications** → **+ New Resource**
3. **Create New Application**

### Configuración:

**General:**
- **Name:** `route-monitor-backend`
- **Build Pack:** Docker
- **Dockerfile Location:** `/Dockerfile` (si está en raíz)

**Source:**
- **Git Repository:** `https://github.com/tu-usuario/tu-repo.git`
- **Branch:** `main`
- **Build Command:** (dejar vacío, Coolify usa Dockerfile)

**Environment Variables:**
- `DJANGO_SECRET_KEY` = (genera uno)
- `DEBUG` = `false`
- `ALLOWED_HOSTS` = `tudominio.com,www.tudominio.com` (o IP del VPS)
- `DATABASE_URL` = (Coolify lo llena automáticamente si conectas la DB)

**Database:**
- Selecciona la base de datos PostgreSQL que creaste

**Ports:**
- **Port:** `8000`
- **Public:** `Yes` (si quieres acceso directo)

**Auto Deploy:**
- **Enable:** `Yes` (deploy automático en cada push)

4. **Create**

---

## Paso 8: Conectar Base de Datos

1. En la página de tu aplicación
2. **Connections** → **Add Database**
3. Selecciona tu base de datos PostgreSQL
4. Coolify automáticamente:
   - Agrega `DATABASE_URL` a variables de entorno
   - Conecta los servicios

---

## Paso 9: Deploy

1. Si conectaste GitHub: **Deploy** se iniciará automáticamente
2. Si no: Click **Deploy** button
3. Coolify:
   - Clona tu repo
   - Construye Docker image
   - Ejecuta migraciones (si las configuras)
   - Inicia tu aplicación

**Monitorea los logs:**
- Click en tu aplicación → **Logs**
- Verás el proceso en tiempo real

---

## Paso 10: Configurar Dominio y SSL

### Si tienes dominio:

1. **Settings** → **Domains**
2. **Add Domain:**
   - `api.tudominio.com` (o el que prefieras)
3. **SSL:**
   - Coolify automáticamente obtiene certificado Let's Encrypt
   - Se renueva automáticamente

### Si no tienes dominio:

Puedes acceder directamente con la IP:
- `http://TU_IP:8000`
- O configurar dominio después

---

## Paso 11: Ejecutar Migraciones

Coolify puede ejecutar migraciones automáticamente, pero si necesitas hacerlo manualmente:

1. En tu aplicación → **Logs**
2. O usar **Execute Command**:
   ```bash
   python manage.py migrate
   ```

O modifica tu `Dockerfile` para ejecutar migraciones al iniciar (ya está en el CMD).

---

## Paso 12: Configurar Variables de Entorno

En tu aplicación → **Environment Variables**:

```bash
DJANGO_SECRET_KEY=tu-secret-key-aqui
DEBUG=false
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,TU_IP_DEL_VPS
DATABASE_URL=postgresql://user:pass@postgres:5432/dbname
```

**Nota:** `DATABASE_URL` se llena automáticamente si conectaste la base de datos.

---

## Paso 13: Verificar Deployment

1. **Abre tu aplicación:**
   - `https://tudominio.com/api/health/`
   - O `http://TU_IP:8000/api/health/`

2. **Debería responder:**
   ```json
   {
     "status": "healthy",
     "timestamp": "...",
     "message": "Service is running"
   }
   ```

---

## 🔧 Troubleshooting

### Problema: "Cannot connect to database"

**Solución:**
1. Verifica que la base de datos esté corriendo
2. Revisa `DATABASE_URL` en variables de entorno
3. Verifica que la aplicación y DB estén en la misma red de Coolify

### Problema: "Build failed"

**Solución:**
1. Revisa logs en Coolify
2. Verifica que `Dockerfile` esté correcto
3. Verifica que `requirements.txt` tenga todas las dependencias

### Problema: "Static files not loading"

**Solución:**
1. Verifica que `collectstatic` se ejecute en Dockerfile
2. Configura volumen para static files si es necesario

### Problema: "Port already in use"

**Solución:**
1. Cambia el puerto en configuración de aplicación
2. O detén la aplicación que usa ese puerto

---

## 📊 Ventajas vs Desventajas

### ✅ Ventajas:

- **Muy barato** ($5-6/month)
- **Control total**
- **Auto-deploy desde GitHub**
- **SSL automático**
- **Múltiples apps en mismo VPS**
- **Escalable** (puedes agregar más VPS)
- **Open source** (gratis)

### ❌ Desventajas:

- **Requiere conocimiento básico de Linux/VPS**
- **Tú manejas el servidor** (backups, updates, etc.)
- **Setup inicial toma más tiempo** (1-2 horas)
- **Necesitas configurar dominio** para SSL (o usar IP)

---

## 🎯 Comparación Final

| Feature | Coolify + VPS | PythonAnywhere | Fly.io |
|---------|---------------|----------------|---------|
| **Costo** | $5-6/mes | $5-7/mes | $10-15/mes |
| **Control** | ⭐⭐⭐⭐⭐ Total | ⭐⭐ Limitado | ⭐⭐⭐ Alto |
| **Auto-deploy** | ✅ GitHub | ❌ Manual | ✅ GitHub |
| **SSL** | ✅ Automático | ✅ Incluido | ✅ Automático |
| **Setup** | 🟡 Medio (1-2h) | 🟢 Fácil (30min) | 🟡 Medio (1h) |
| **Múltiples apps** | ✅ Ilimitadas | ❌ Limitado | ✅ Sí |
| **Escalabilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐ Limitada | ⭐⭐⭐⭐ |

---

## ✅ Checklist de Deployment

- [ ] VPS creado y configurado
- [ ] Coolify instalado y funcionando
- [ ] PostgreSQL database creada en Coolify
- [ ] Proyecto subido a GitHub (o Dockerfile listo)
- [ ] Aplicación creada en Coolify
- [ ] Base de datos conectada
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso
- [ ] Migraciones ejecutadas
- [ ] Health endpoint funciona
- [ ] SSL configurado (si tienes dominio)
- [ ] Frontend actualizado con nueva API URL

---

## 🚀 Próximos Pasos

1. **Backup automático:**
   - Configurar backups de base de datos
   - Coolify puede hacerlo automáticamente

2. **Monitoreo:**
   - Agregar monitoring (Coolify tiene algunos built-in)
   - O usar servicios externos

3. **CDN (Opcional):**
   - Para static files
   - Cloudflare (gratis) o similar

4. **Escalar:**
   - Si creces, puedes agregar más VPS
   - Coolify puede manejar múltiples servidores

---

## 💡 Mi Recomendación

**Coolify + VPS es EXCELENTE si:**
- ✅ Quieres control total
- ✅ Planeas tener múltiples aplicaciones
- ✅ Tienes 1-2 horas para setup inicial
- ✅ Quieres ahorrar dinero ($5/mes vs $15)

**PythonAnywhere es mejor si:**
- ✅ Quieres la solución más simple
- ✅ Solo tienes una aplicación
- ✅ Prefieres no manejar servidor

---

**Tu app estará en:**
```
https://tudominio.com
```
O
```
http://TU_IP_DEL_VPS:8000
```

**API Base URL:**
```
https://tudominio.com/api
```

¡Mucho más barato y con control total! 🎉

