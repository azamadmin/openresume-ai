# 📁 File-by-File Code Explanation

This document explains what each file does and how the code works in simple terms.

## 🏗️ Backend Files

### 📄 `backend/app.py` - Main Application
**Purpose**: The heart of the application - starts the web server and connects everything together.

**What it does**:
- Creates the Flask web server
- Sets up database connections
- Configures security (JWT tokens)
- Registers all the API routes
- Handles CORS (allows frontend to talk to backend)

**Key Code Sections**:
```python
def create_app():
    # Creates the main Flask application
    app = Flask(__name__)
    
    # Security configuration
    app.config['SECRET_KEY'] = secret_key
    app.config['JWT_SECRET_KEY'] = jwt_secret_key
    
    # Register all the route blueprints
    app.register_blueprint(auth_bp)      # Login/register routes
    app.register_blueprint(upload_bp)    # File upload routes
    # ... more blueprints
```

### 📄 `backend/models.py` - Database Structure
**Purpose**: Defines how data is stored in the database (like creating tables).

**What it does**:
- Defines User table (stores user accounts)
- Defines Resume table (stores uploaded resumes)
- Defines JobDescription table (stores job postings)
- Defines MatchScore table (stores calculated scores)
- Defines Suggestion table (stores AI suggestions)

**Key Code Sections**:
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # This creates a "users" table in the database
```

### 📄 `backend/routes/us05_auth_routes.py` - Login/Register
**Purpose**: Handles user login and registration.

**What it does**:
- `/api/login` - Checks email/password and gives back a token
- `/api/register` - Creates new user accounts
- `/api/refresh` - Refreshes expired tokens

**Key Code Sections**:
```python
@auth_bp.route('/login', methods=['POST'])
def login():
    # Get email and password from request
    email = request.json.get('email')
    password = request.json.get('password')
    
    # Check if user exists and password is correct
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        # Create a token for the user
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'success': True, 'access_token': access_token})
```

### 📄 `backend/routes/us05_upload_routes.py` - File Upload
**Purpose**: Handles resume file uploads (PDF/DOCX).

**What it does**:
- Receives uploaded files from frontend
- Validates file type and size
- Extracts text from PDF/DOCX files
- Saves file information to database
- Extracts keywords automatically

**Key Code Sections**:
```python
@upload_bp.route('/upload_resume', methods=['POST'])
def upload_resume():
    # Get the uploaded file
    file = request.files['resume']
    
    # Save the file
    filename = secure_filename(file.filename)
    file.save(os.path.join(upload_folder, filename))
    
    # Extract text from the file
    extracted_text = file_parser.extract_text(file_path)
    
    # Save to database
    resume = Resume(user_id=user_id, filename=filename, extracted_text=extracted_text)
    db.session.add(resume)
    db.session.commit()
```

### 📄 `backend/routes/us07_suggestions_routes.py` - AI Suggestions
**Purpose**: Generates improvement suggestions for resumes.

**What it does**:
- `/api/basic_suggestions` - Creates basic improvement suggestions
- `/api/premium_suggestions` - Creates advanced AI suggestions
- Compares resume keywords with job description keywords
- Identifies missing skills and suggests improvements

**Key Code Sections**:
```python
@suggestions_bp.route('/basic_suggestions', methods=['POST'])
def generate_basic_suggestions():
    # Get resume and job description IDs
    resume_id = request.json.get('resume_id')
    job_description_id = request.json.get('job_description_id')
    
    # Generate suggestions using AI service
    suggestions_result = dynamic_suggestions_service.generate_basic_suggestions(
        resume_id=resume_id,
        job_description_id=job_description_id,
        user_id=user.id
    )
    
    return jsonify({
        'success': True,
        'suggestions': suggestions_result['suggestions']
    })
```

### 📄 `backend/services/file_parser.py` - Text Extraction
**Purpose**: Extracts text from PDF and DOCX files.

**What it does**:
- Reads PDF files and converts to text
- Reads DOCX files and extracts text content
- Handles different file formats
- Cleans up extracted text

**Key Code Sections**:
```python
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text
```

### 📄 `backend/services/keyword_parser.py` - Keyword Extraction
**Purpose**: Finds important keywords in resumes and job descriptions.

**What it does**:
- Identifies technical skills (Python, Java, etc.)
- Finds soft skills (leadership, communication, etc.)
- Extracts industry-specific terms
- Categorizes keywords by type

**Key Code Sections**:
```python
def extract_keywords(text):
    # Convert text to lowercase for analysis
    text_lower = text.lower()
    
    # Find technical skills
    technical_skills = []
    for skill in TECHNICAL_SKILLS_LIST:
        if skill.lower() in text_lower:
            technical_skills.append(skill)
    
    # Find soft skills
    soft_skills = []
    for skill in SOFT_SKILLS_LIST:
        if skill.lower() in text_lower:
            soft_skills.append(skill)
    
    return {
        'technical': technical_skills,
        'soft_skills': soft_skills
    }
```

### 📄 `backend/services/matching_service.py` - Score Calculation
**Purpose**: Calculates how well a resume matches a job description.

**What it does**:
- Compares resume keywords with job keywords
- Calculates percentage match scores
- Provides detailed breakdown by category
- Stores match results in database

**Key Code Sections**:
```python
def calculate_match_score(resume_keywords, job_keywords):
    # Calculate technical skills match
    technical_match = len(set(resume_keywords['technical']) & 
                         set(job_keywords['technical']))
    technical_total = len(job_keywords['technical'])
    technical_score = (technical_match / technical_total) * 100 if technical_total > 0 else 0
    
    # Calculate overall score
    overall_score = (technical_score + soft_skills_score + other_score) / 3
    
    return {
        'overall_score': overall_score,
        'technical_score': technical_score,
        'soft_skills_score': soft_skills_score
    }
```

### 📄 `backend/services/dynamic_suggestions_service.py` - AI Suggestions
**Purpose**: Creates intelligent suggestions for resume improvement.

**What it does**:
- Analyzes gaps between resume and job requirements
- Generates specific, actionable suggestions
- Prioritizes suggestions by importance
- Creates both basic and premium suggestion types

**Key Code Sections**:
```python
def generate_basic_suggestions(self, resume_id, job_description_id, user_id):
    # Analyze keyword gaps
    missing_keywords = self.find_missing_keywords(resume, job_description)
    
    suggestions = []
    
    # Create suggestions for missing technical skills
    for keyword in missing_keywords['technical']:
        suggestions.append({
            "type": "technical_skills",
            "priority": "high",
            "title": f"Add {keyword.title()} Experience",
            "description": f"Required skill mentioned in job description",
            "action": f"Add {keyword} to your Skills section and describe a project where you used it."
        })
    
    return {'success': True, 'suggestions': suggestions}
```

## 🎨 Frontend Files

### 📄 `frontend/us10_dashboard.html` - Main Dashboard
**Purpose**: The main page where users interact with the application.

**What it contains**:
- Resume upload section
- Job description input area
- Suggestions display area
- Navigation menu
- Match score display

**Key HTML Sections**:
```html
<!-- Resume Upload Section -->
<div class="upload-section">
    <input type="file" id="resume-upload" accept=".pdf,.docx">
    <button onclick="uploadResume()">Upload Resume</button>
</div>

<!-- Suggestions Section -->
<div class="suggestions-section" id="suggestions-section">
    <button onclick="generateBasicSuggestions()">Generate Basic Suggestions</button>
    <button onclick="generatePremiumSuggestions()">Generate Premium Suggestions</button>
    <div id="suggestions-list"></div>
</div>
```

### 📄 `frontend/static/js/us10_dashboard.js` - Dashboard Logic
**Purpose**: Makes the dashboard interactive and communicates with the backend.

**What it does**:
- Handles file uploads
- Sends requests to backend API
- Displays suggestions on the page
- Manages user interface updates
- Handles authentication tokens

**Key JavaScript Functions**:
```javascript
function uploadResume() {
    // Get the selected file
    const fileInput = document.getElementById('resume-upload');
    const file = fileInput.files[0];
    
    // Create form data for upload
    const formData = new FormData();
    formData.append('resume', file);
    
    // Send to backend
    fetch('/api/upload_resume', {
        method: 'POST',
        headers: {'Authorization': `Bearer ${token}`},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Resume uploaded successfully!');
        }
    });
}

function generateBasicSuggestions() {
    // Get resume and job description IDs
    const resumeId = getCurrentResumeId();
    const jobId = getCurrentJobId();
    
    // Request suggestions from backend
    fetch('/api/basic_suggestions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            resume_id: resumeId,
            job_description_id: jobId
        })
    })
    .then(response => response.json())
    .then(data => {
        // Display suggestions on the page
        displaySuggestions(data.suggestions);
    });
}

function displaySuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestions-list');
    suggestionsList.innerHTML = ''; // Clear existing suggestions
    
    // Create HTML for each suggestion
    suggestions.forEach(suggestion => {
        const suggestionElement = document.createElement('div');
        suggestionElement.className = 'suggestion-item';
        suggestionElement.innerHTML = `
            <h4>${suggestion.title}</h4>
            <p>${suggestion.description}</p>
            <div class="action">${suggestion.action}</div>
        `;
        suggestionsList.appendChild(suggestionElement);
    });
}
```

### 📄 `frontend/static/css/us10_styles.css` - Styling
**Purpose**: Makes the application look good and user-friendly.

**What it does**:
- Defines colors, fonts, and layouts
- Makes the interface responsive (works on mobile)
- Styles buttons, forms, and suggestions
- Creates hover effects and animations

**Key CSS Sections**:
```css
/* Main layout */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Upload section styling */
.upload-section {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Suggestion items */
.suggestion-item {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
}

.suggestion-item:hover {
    border-color: #667eea;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}
```

## 🗄️ Database Files

### 📄 `database/dr_resume_dev.db` - SQLite Database
**Purpose**: Stores all application data.

**What it contains**:
- User accounts and passwords
- Uploaded resume information
- Job descriptions
- Match scores and analysis results
- AI-generated suggestions
- Scan history

**Tables Structure**:
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP
);

-- Resumes table
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255),
    extracted_text TEXT,
    keywords_extracted BOOLEAN,
    created_at TIMESTAMP
);
```

## 🔧 Configuration Files

### 📄 `backend/requirements.txt` - Python Dependencies
**Purpose**: Lists all the Python packages needed to run the application.

**What it contains**:
```
Flask==2.3.3              # Web framework
Flask-SQLAlchemy==3.0.5    # Database ORM
Flask-JWT-Extended==4.5.2  # JWT authentication
Flask-CORS==4.0.0          # Cross-origin requests
python-docx==0.8.11        # DOCX file processing
PyPDF2==3.0.1              # PDF file processing
python-dotenv==1.0.0       # Environment variables
```

### 📄 `run_app.py` - Application Launcher
**Purpose**: Easy way to start the application.

**What it does**:
- Sets up Python paths
- Imports the main application
- Starts the Flask server

```python
# Add directories to Python path
sys.path.insert(0, current_dir)
sys.path.insert(0, backend_dir)

# Import and run the app
from app import main
main()
```

## 🎯 How Everything Works Together

1. **User visits website** → `frontend/us10_dashboard.html` loads
2. **User logs in** → `us05_auth_routes.py` validates credentials
3. **User uploads resume** → `us05_upload_routes.py` processes file
4. **File gets parsed** → `file_parser.py` extracts text
5. **Keywords extracted** → `keyword_parser.py` finds important terms
6. **User adds job description** → `us05_jd_routes.py` saves it
7. **User clicks suggestions** → `us07_suggestions_routes.py` generates recommendations
8. **AI analyzes data** → `dynamic_suggestions_service.py` creates suggestions
9. **Results displayed** → `us10_dashboard.js` shows suggestions on page
10. **Data saved** → `models.py` stores everything in database

This creates a complete workflow from file upload to AI-powered suggestions!

## 🚀 Quick Development Guide

### Adding a New Feature

1. **Backend API** (if needed):
   - Add new route in `backend/routes/`
   - Add database model in `backend/models.py`
   - Add business logic in `backend/services/`

2. **Frontend** (if needed):
   - Add HTML elements to appropriate page
   - Add JavaScript functions in `static/js/`
   - Add CSS styling in `static/css/`

3. **Database** (if needed):
   - Update models in `models.py`
   - Database will auto-update on restart

### Common Tasks

**Add new keyword category**:
- Edit `keyword_parser.py` → Add to keyword lists
- Edit `dynamic_suggestions_service.py` → Add suggestion logic

**Add new page**:
- Create new HTML file in `frontend/`
- Add route in `backend/app.py`
- Add navigation links

**Modify suggestions**:
- Edit `dynamic_suggestions_service.py`
- Modify suggestion templates and logic

### Testing Your Changes

1. **Start the application**: `python backend/app.py`
2. **Open browser**: Go to `http://localhost:5000`
3. **Test the feature**: Use the web interface
4. **Check logs**: Look at terminal output for errors
5. **Check database**: Use SQLite browser to verify data

This modular structure makes it easy to understand and modify any part of the application!
