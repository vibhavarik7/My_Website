"""
Portfolio Website - Simplified Flask Application
Author: Vibhavari Kotekar

This is a beginner-friendly portfolio website with an admin panel.
Each section has detailed comments to help you understand how Flask works.
"""

# ============================================================================
# STEP 1: Import Required Libraries
# ============================================================================

# Flask: The web framework that handles routes and requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory

# Security: For handling file uploads safely
from werkzeug.utils import secure_filename

# Database: SQLite for storing portfolio data
import sqlite3

# File handling: For managing uploaded files
import os
from datetime import datetime

# Environment variables: Load .env file for local development
from dotenv import load_dotenv
load_dotenv()  # This loads variables from .env file if it exists

# Image processing: For adjusting and saving profile photos
from PIL import Image
import io



# ============================================================================
# STEP 2: Initialize Flask App and Configuration
# ============================================================================

# Create Flask application instance
app = Flask(__name__)

# Secret key for session management (load from environment variable)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production-dev-key-only')

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/certificates'  # Where to save uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'gif'}  # Allowed file types
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16MB

# Admin password (load from environment variable - REQUIRED for production!)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable is required! Create a .env file or set it in your environment.")

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================================
# STEP 3: Database Helper Functions
# ============================================================================

def get_db():
    """
    Connect to the SQLite database.
    SQLite is a simple, file-based database - perfect for learning!
    """
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_db():
    """
    Create database tables and add sample data.
    This runs once when you first start the app.
    """
    conn = get_db()
    c = conn.cursor()
    
    # Table 1: Certificates (your achievements!)
    c.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            project_link TEXT,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 2: Projects (your coding projects)
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            technologies TEXT NOT NULL,
            project_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 3: Skills (your technical skills)
    c.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 4: Qualities (your professional qualities)
    c.execute('''
        CREATE TABLE IF NOT EXISTS qualities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 5: Contact Info (your contact details)
    c.execute('''
        CREATE TABLE IF NOT EXISTS contact (
            id INTEGER PRIMARY KEY,
            email TEXT,
            linkedin TEXT,
            github TEXT
        )
    ''')
    
    # Table 6: Blogs (your Medium blog posts)
    c.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            blog_link TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add default contact info if table is empty
    c.execute('SELECT COUNT(*) FROM contact')
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO contact (id, email, linkedin, github) 
            VALUES (1, 'vibhavarikotekar7@gmail.com', 
                    'https://www.linkedin.com/in/vibhavari-kotekar/', 
                    'https://github.com/vibhavarik7/')
        ''')
    
    # Add sample projects if table is empty
    c.execute('SELECT COUNT(*) FROM projects')
    if c.fetchone()[0] == 0:
        sample_projects = [
            ('E-Commerce Platform', 'Built a scalable e-commerce platform', 'Python, Flask, PostgreSQL, React', 'https://github.com/example/ecommerce'),
            ('Analytics Dashboard', 'Real-time data analytics dashboard', 'Python, Django, Redis, D3.js', 'https://github.com/example/analytics'),
            ('AI Chatbot', 'Intelligent chatbot using NLP', 'Python, TensorFlow, Flask, MongoDB', 'https://github.com/example/chatbot')
        ]
        c.executemany('INSERT INTO projects (title, description, technologies, project_link) VALUES (?, ?, ?, ?)', sample_projects)
    
    # Add sample skills if table is empty
    c.execute('SELECT COUNT(*) FROM skills')
    if c.fetchone()[0] == 0:
        sample_skills = [
            ('Python', 'work_with'),
            ('JavaScript', 'work_with'),
            ('Flask', 'work_with'),
            ('React', 'work_with'),
            ('Docker', 'work_with'),
            ('AWS', 'know'),
            ('Machine Learning', 'know'),
            ('PostgreSQL', 'work_with'),
        ]
        c.executemany('INSERT INTO skills (name, category) VALUES (?, ?)', sample_skills)
    
    # Add sample qualities if table is empty
    c.execute('SELECT COUNT(*) FROM qualities')
    if c.fetchone()[0] == 0:
        sample_qualities = [
            'Strong problem-solving skills with passion for efficient solutions.',
            'Excellent team player with leadership experience.',
            'Dedicated to continuous learning and staying updated.',
            'Detail-oriented with commitment to clean, maintainable code.'
        ]
        c.executemany('INSERT INTO qualities (content) VALUES (?)', [(q,) for q in sample_qualities])
    
    conn.commit()
    conn.close()


def check_file_allowed(filename):
    """
    Check if uploaded file type is allowed.
    Returns True if file extension is in ALLOWED_EXTENSIONS.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================================
# STEP 4: Main Routes (Public Pages)
# ============================================================================

@app.route('/')
def index():
    """
    Home page - Shows your portfolio to visitors.
    This is what everyone sees when they visit your website!
    """
    # Connect to database
    conn = get_db()
    
    # Get all data from database tables
    certificates = conn.execute('SELECT * FROM certificates ORDER BY created_at DESC').fetchall()
    projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    blogs = conn.execute('SELECT * FROM blogs ORDER BY created_at DESC').fetchall()
    skills_work = conn.execute('SELECT * FROM skills WHERE category = "work_with" ORDER BY name').fetchall()
    skills_know = conn.execute('SELECT * FROM skills WHERE category = "know" ORDER BY name').fetchall()
    qualities = conn.execute('SELECT * FROM qualities ORDER BY created_at').fetchall()
    contact = conn.execute('SELECT * FROM contact WHERE id = 1').fetchone()
    
    conn.close()
    
    # Render the HTML template with all the data
    return render_template('index.html',
                         certificates=certificates,
                         projects=projects,
                         blogs=blogs,
                         skills_work=skills_work,
                         skills_know=skills_know,
                         qualities=qualities,
                         contact=contact)


@app.route('/uploads/certificates/<filename>')
def serve_certificate(filename):
    """
    Serve uploaded certificate files.
    When someone clicks on a certificate, this sends the file to their browser.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================================================
# STEP 5: Admin Authentication Routes
# ============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin login page.
    GET: Show the login form
    POST: Check password and log in
    """
    if request.method == 'POST':
        # User submitted the login form
        password = request.form.get('password')
        
        if password == ADMIN_PASSWORD:
            # Password correct! Save login status in session
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            # Password wrong
            flash('Invalid password. Please try again.', 'error')
    
    # Show login form
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """
    Log out of admin panel.
    Removes the login status from session.
    """
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/admin')
def admin_panel():
    """
    Admin panel - Where you manage your portfolio content.
    Only accessible if logged in!
    """
    # Check if user is logged in
    if not session.get('admin_logged_in'):
        flash('Please login to access the admin panel.', 'error')
        return redirect(url_for('admin_login'))
    
    # Get all data to display in admin panel
    conn = get_db()
    certificates = conn.execute('SELECT * FROM certificates ORDER BY created_at DESC').fetchall()
    projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    blogs = conn.execute('SELECT * FROM blogs ORDER BY created_at DESC').fetchall()
    skills_work = conn.execute('SELECT * FROM skills WHERE category = "work_with" ORDER BY name').fetchall()
    skills_know = conn.execute('SELECT * FROM skills WHERE category = "know" ORDER BY name').fetchall()
    qualities = conn.execute('SELECT * FROM qualities ORDER BY created_at').fetchall()
    contact = conn.execute('SELECT * FROM contact WHERE id = 1').fetchone()
    conn.close()
    
    return render_template('admin_panel.html',
                         certificates=certificates,
                         projects=projects,
                         blogs=blogs,
                         skills_work=skills_work,
                         skills_know=skills_know,
                         qualities=qualities,
                         contact=contact)


# ============================================================================
# STEP 6: Certificate Management Routes
# ============================================================================

@app.route('/admin/certificate/add', methods=['POST'])
def add_certificate():
    """Add a new certificate (HTML form submission)."""
    # Check if logged in
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('admin_panel'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Validate file type
    if file and check_file_allowed(file.filename):
        # Make filename safe
        filename = secure_filename(file.filename)
        
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Save file to upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get file type (extension)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        project_link = request.form.get('project_link')
        
        # Save to database
        conn = get_db()
        conn.execute('''
            INSERT INTO certificates (title, description, project_link, file_path, file_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, project_link, filename, file_type))
        conn.commit()
        conn.close()
        
        flash('Certificate added successfully!', 'success')
        return redirect(url_for('admin_panel'))
    
    flash('Invalid file type. Please upload JPG, PNG, GIF, or PDF only.', 'error')
    return redirect(url_for('admin_panel'))


@app.route('/uploads/certificates/<filename>')
def uploaded_file(filename):
    """Serve uploaded certificate files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/admin/certificate/delete/<int:cert_id>', methods=['POST'])
def delete_certificate(cert_id):
    """Delete a certificate (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    certificate = conn.execute('SELECT * FROM certificates WHERE id = ?', (cert_id,)).fetchone()
    
    if certificate:
        # Delete the actual file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], certificate['file_path'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        conn.execute('DELETE FROM certificates WHERE id = ?', (cert_id,))
        conn.commit()
        flash('Certificate deleted successfully!', 'success')
    else:
        flash('Certificate not found.', 'error')
    
    conn.close()
    return redirect(url_for('admin_panel'))


# ============================================================================
# STEP 7: Project Management Routes
# ============================================================================

@app.route('/admin/project/add', methods=['POST'])
def add_project():
    """Add a new project (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    # Get form data
    title = request.form.get('title')
    description = request.form.get('description')
    technologies = request.form.get('technologies')
    project_link = request.form.get('project_link')
    
    # Validate required fields
    if not title or not description or not technologies:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Save to database
    conn = get_db()
    conn.execute('''
        INSERT INTO projects (title, description, technologies, project_link)
        VALUES (?, ?, ?, ?)
    ''', (title, description, technologies, project_link))
    conn.commit()
    conn.close()
    
    flash('Project added successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/project/edit/<int:project_id>', methods=['POST'])
def edit_project(project_id):
    """Edit an existing project (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    # Get form data
    title = request.form.get('title')
    description = request.form.get('description')
    technologies = request.form.get('technologies')
    project_link = request.form.get('project_link')
    
    # Update in database
    conn = get_db()
    conn.execute('''
        UPDATE projects 
        SET title = ?, description = ?, technologies = ?, project_link = ?
        WHERE id = ?
    ''', (title, description, technologies, project_link, project_id))
    conn.commit()
    conn.close()
    
    flash('Project updated successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/project/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    """Delete a project (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))


# ============================================================================
# STEP 7B: Blog Management Routes
# ============================================================================

@app.route('/admin/blog/add', methods=['POST'])
def add_blog():
    """Add a new blog post (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    # Get form data
    title = request.form.get('title')
    description = request.form.get('description')
    blog_link = request.form.get('blog_link')
    
    # Validate required fields
    if not title or not blog_link:
        flash('Title and Blog Link are required.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Save to database
    conn = get_db()
    conn.execute('''
        INSERT INTO blogs (title, description, blog_link)
        VALUES (?, ?, ?)
    ''', (title, description, blog_link))
    conn.commit()
    conn.close()
    
    flash('Blog added successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/blog/edit/<int:blog_id>', methods=['POST'])
def edit_blog(blog_id):
    """Edit an existing blog post (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    # Get form data
    title = request.form.get('title')
    description = request.form.get('description')
    blog_link = request.form.get('blog_link')
    
    # Update in database
    conn = get_db()
    conn.execute('''
        UPDATE blogs 
        SET title = ?, description = ?, blog_link = ?
        WHERE id = ?
    ''', (title, description, blog_link, blog_id))
    conn.commit()
    conn.close()
    
    flash('Blog updated successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/blog/delete/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    """Delete a blog post (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    conn.execute('DELETE FROM blogs WHERE id = ?', (blog_id,))
    conn.commit()
    conn.close()
    
    flash('Blog deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))


# ============================================================================
# STEP 8: Skill Management Routes
# ============================================================================

@app.route('/admin/skill/add', methods=['POST'])
def add_skill():
    """Add a new skill (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    name = request.form.get('name')
    category = request.form.get('category')
    
    if not name or not category:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = get_db()
    conn.execute('INSERT INTO skills (name, category) VALUES (?, ?)', (name, category))
    conn.commit()
    conn.close()
    
    flash('Skill added successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/skill/delete/<int:skill_id>', methods=['POST'])
def delete_skill(skill_id):
    """Delete a skill (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    conn.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
    conn.commit()
    conn.close()
    
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))


# ============================================================================
# STEP 9: Quality Management Routes
# ============================================================================

@app.route('/admin/quality/add', methods=['POST'])
def add_quality():
    """Add a new professional quality (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    content = request.form.get('content')
    
    if not content:
        flash('Content is required.', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = get_db()
    conn.execute('INSERT INTO qualities (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()
    
    flash('Quality added successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/quality/edit/<int:quality_id>', methods=['POST'])
def edit_quality(quality_id):
    """Edit an existing quality (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    content = request.form.get('content')
    
    conn = get_db()
    conn.execute('UPDATE qualities SET content = ? WHERE id = ?', (content, quality_id))
    conn.commit()
    conn.close()
    
    flash('Quality updated successfully!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/quality/delete/<int:quality_id>', methods=['POST'])
def delete_quality(quality_id):
    """Delete a quality (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    conn.execute('DELETE FROM qualities WHERE id = ?', (quality_id,))
    conn.commit()
    conn.close()
    
    flash('Quality deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))


# ============================================================================
# STEP 10: Contact Information Routes
# ============================================================================

@app.route('/admin/contact/update', methods=['POST'])
def update_contact():
    """Update contact information (HTML form submission)."""
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin_login'))
    
    email = request.form.get('email')
    linkedin = request.form.get('linkedin')
    github = request.form.get('github')
    
    conn = get_db()
    conn.execute('''
        UPDATE contact 
        SET email = ?, linkedin = ?, github = ? 
        WHERE id = 1
    ''', (email, linkedin, github))
    conn.commit()
    conn.close()
    
    flash('Contact information updated successfully!', 'success')
    return redirect(url_for('admin_panel'))


# ============================================================================
# STEP 11: Profile Photo Route (Optional)
# ============================================================================

@app.route('/admin/profile-photo/upload', methods=['POST'])
def upload_profile_photo():
    """Upload profile photo with zoom and position adjustments."""
    # Check if user is logged in
    if not session.get('admin_logged_in'):
        flash('Please login to upload photos.', 'error')
        return redirect(url_for('admin_login'))
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file uploaded. Please select a file.', 'error')
        return redirect(url_for('admin_panel'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected. Please choose a file.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Validate file
    if file and check_file_allowed(file.filename):
        try:
            # Get zoom and position values from sliders
            zoom = float(request.form.get('zoom', 100)) / 100  # 0.8 to 2.0
            position = int(request.form.get('position', 0))  # -50 to +50
            
            # Open the image
            img = Image.open(file.stream)
            
            # Convert to RGB (handle PNG transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (245, 230, 211))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Output size
            output_size = 600
            
            # Step 1: Scale image to fit in output_size (like object-fit: contain)
            width, height = img.size
            aspect = width / height
            
            # Calculate size to fit (contain behavior)
            if aspect > 1:
                # Wider - fit to width
                fit_width = output_size
                fit_height = int(output_size / aspect)
            else:
                # Taller or square - fit to height
                fit_height = output_size
                fit_width = int(output_size * aspect)
            
            # Step 2: Apply zoom
            final_width = int(fit_width * zoom)
            final_height = int(fit_height * zoom)
            
            # Resize
            img_resized = img.resize((final_width, final_height), Image.Resampling.LANCZOS)
            
            # Step 3: Create canvas
            canvas = Image.new('RGB', (output_size, output_size), (245, 230, 211))
            
            # Step 4: Calculate position (exactly like CSS transform)
            # Center position
            paste_x = (output_size - final_width) // 2
            paste_y = (output_size - final_height) // 2
            
            # Apply vertical offset from position slider
            # position is -50 to +50, apply as percentage of output_size
            y_offset = int(position * output_size / 100)
            paste_y += y_offset
            
            # Paste image
            canvas.paste(img_resized, (paste_x, paste_y))
            
            # Save as PNG
            images_dir = os.path.join('static', 'images')
            os.makedirs(images_dir, exist_ok=True)
            file_path = os.path.join(images_dir, 'profile.png')
            canvas.save(file_path, 'PNG', quality=95, optimize=True)
            
            flash('Profile photo saved with your adjustments! 🎉', 'success')
            return redirect(url_for('admin_panel'))
            
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'error')
            return redirect(url_for('admin_panel'))
    
    flash('Invalid file type. Please upload JPG, PNG, or GIF only.', 'error')
    return redirect(url_for('admin_panel'))


# ============================================================================
# STEP 12: Start the Application
# ============================================================================

if __name__ == '__main__':
    # Initialize database (create tables and sample data)
    init_db()
    
    # Get port from environment variable (Render provides PORT, default to 5001 for local)
    port = int(os.environ.get('PORT', 5001))
    
    # Debug mode only in development (not in production)
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Print welcome message
    print("\n" + "="*60)
    print("🚀 Portfolio Website Starting...")
    print("="*60)
    print(f"\n📍 Access your portfolio at: http://localhost:{port}")
    print(f"🔐 Admin panel at: http://localhost:{port}/admin/login")
    if not debug:
        print("🌐 Running in production mode")
    print("\n" + "="*60 + "\n")
    
    # Start Flask server
    # host='0.0.0.0': Makes it accessible (required for Render)
    # port: From environment variable (Render) or default 5001
    # debug: Only True in development environment
    app.run(debug=debug, host='0.0.0.0', port=port)
