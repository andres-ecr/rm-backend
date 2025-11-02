# ⚡ PythonAnywhere Quick Start - 5 Minutes

## Super Quick Version

1. **Sign up:** https://www.pythonanywhere.com → Beginner ($5/month)

2. **Upload code:**
   - **Files** tab → Upload ZIP or clone from GitHub
   - Location: `~/route-monitor-backend/`

3. **Install packages:**
   ```bash
   # In Bash console
   cd ~/route-monitor-backend
   python3.12 -m venv venv
   source venv/bin/activate
   pip install --user -r requirements.txt
   ```

4. **Create database:**
   - **Databases** tab → PostgreSQL (add-on $2) OR MySQL (free)

5. **Create web app:**
   - **Web** tab → Add web app
   - Framework: Django
   - Python path: `/home/yourusername/route-monitor-backend`

6. **Edit WSGI file:**
   - Replace with code from `PYTHONANYWHERE_DEPLOY.md` Step 9
   - Set environment variables there

7. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

8. **Reload web app:**
   - **Web** tab → Click **Reload** button

9. **Test:**
   - Visit: `https://yourusername.pythonanywhere.com/api/health/`

**Done!** 🎉

For detailed steps, see `PYTHONANYWHERE_DEPLOY.md`

