# Portfolio Website

A clean portfolio website built with Flask to showcase projects, skills, and achievements.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root (copy from `env.example`):
```bash
cp env.example .env
```

Edit `.env` and set your values:
```
SECRET_KEY=your-random-secret-key
ADMIN_PASSWORD=your-secure-password
FLASK_ENV=development
PORT=5001
```

**Important**: The `.env` file is gitignored and won't be committed to GitHub.

### 3. Run the Application
```bash
python app.py
```

### 4. Access Your Site
- **Portfolio**: http://localhost:5001
- **Admin Panel**: http://localhost:5001/admin/login

## Features

- 📸 Profile photo upload
- 🏆 Certificates & awards gallery
- 💻 Projects showcase
- 🛠️ Skills management
- ⭐ Professional qualities
- 📧 Contact information
- 📝 Blog posts (Medium integration)
- 🔐 Password-protected admin panel

## Project Structure

```
├── app.py              # Main Flask application
├── portfolio.db        # SQLite database (auto-created)
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/             # CSS and images
└── uploads/            # Uploaded files
```

## Deployment to Render

1. **Push to GitHub**: Commit and push your code to a GitHub repository

2. **Create Render Account**: Sign up at [render.com](https://render.com)

3. **New Web Service**: 
   - Connect your GitHub repository
   - Select "Web Service"
   - Render will auto-detect Python/Flask

4. **Environment Variables** (in Render Dashboard):
   ```
   SECRET_KEY=your-random-secret-key-here
   ADMIN_PASSWORD=your-secure-password
   FLASK_ENV=production
   ```

5. **Build Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

6. **Auto-Deploy**: Enable "Auto-Deploy" (enabled by default)
   - This automatically deploys when you push to GitHub

7. **Deploy**: Click "Create Web Service"

Your site will be live at `https://your-app-name.onrender.com`

## Updating Your Website After Deployment

1. **Make changes locally** in your code
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Your update description"
   git push
   ```
3. **Render automatically detects** the push and redeploys your site
4. **Wait 2-5 minutes** for the deployment to complete
5. **Your changes are live!** 🎉

**Note**: Render uses ephemeral filesystem. Uploads will be lost on restart. Consider using cloud storage (S3) for production.

## Customization

**Change Admin Password (Local):**  
Set `ADMIN_PASSWORD` environment variable or edit default in `app.py`

**Change Port (Local):**  
Set `PORT` environment variable or edit default in `app.py`

## Technologies

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS
- **Styling**: Pastel color scheme

---

Built with Flask | Simple, Clean, Professional
