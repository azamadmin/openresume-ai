# 🎯 Dr. Resume AI - Complete Project Documentation

**AI-powered resume optimization and job matching platform**

## 📖 About This Project

Dr. Resume AI is a comprehensive web application that helps job seekers optimize their resumes by analyzing them against job descriptions, extracting keywords, calculating match scores, and providing AI-powered suggestions for improvement.

### 🌟 Key Features

- **Resume Upload & Analysis**: Upload resumes in PDF/DOCX format with automatic text extraction
- **Job Description Processing**: Add job descriptions and extract relevant keywords  
- **Smart Keyword Matching**: Advanced NLP-based keyword extraction and matching
- **AI-Powered Suggestions**: Get basic and premium AI suggestions for resume improvement
- **Match Score Calculation**: Detailed scoring based on technical skills, soft skills, and other keywords
- **Scan History Dashboard**: Track your resume optimization progress over time
- **User Authentication**: Secure login/register system with JWT tokens
- **Account Management**: Manage your profile and view scan history

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-doctor.ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the `backend/` directory:
   ```env
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   DATABASE_URL=sqlite:///database/dr_resume_dev.db
   ```

4. **Run the application**
   ```bash
   python run_app.py
   ```
   Or directly:
   ```bash
   python backend/app.py
   ```

5. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## 📁 Project Structure

```
resume-doctor.ai/
├── 📁 backend/                    # Backend Flask Application
│   ├── 📄 app.py                 # Main Flask application entry point
│   ├── 📄 models.py              # Database models (User, Resume, JobDescription, etc.)
│   ├── 📄 requirements.txt       # Python dependencies
│   ├── 📁 routes/                # API route handlers
│   │   ├── 📄 us05_auth_routes.py      # Authentication (login/register)
│   │   ├── 📄 us05_upload_routes.py    # Resume upload handling
│   │   ├── 📄 us05_jd_routes.py        # Job description management
│   │   ├── 📄 us06_matching_routes.py  # Resume-job matching
│   │   ├── 📄 us07_suggestions_routes.py # AI suggestions
│   │   ├── 📄 us10_history_routes.py   # Scan history
│   │   └── 📄 us10_account_routes.py   # Account management
│   ├── 📁 services/              # Business logic services
│   │   ├── 📄 file_parser.py           # PDF/DOCX text extraction
│   │   ├── 📄 keyword_parser.py        # Keyword extraction
│   │   ├── 📄 advanced_keyword_extractor.py # Advanced NLP processing
│   │   ├── 📄 matching_service.py      # Score calculation
│   │   └── 📄 dynamic_suggestions_service.py # AI suggestions
│   ├── 📁 middleware/            # Custom middleware
│   │   └── 📄 auth_middleware.py       # Authentication middleware
│   └── 📁 uploads/               # Temporary file storage
├── 📁 frontend/                  # Frontend Web Interface
│   ├── 📄 index.html            # Landing page
│   ├── 📄 us10_login.html       # Login page
│   ├── 📄 us10_register.html    # Registration page
│   ├── 📄 us10_dashboard.html   # Main dashboard
│   ├── 📄 us10_account.html     # Account settings
│   └── 📁 static/               # Static assets
│       ├── 📁 css/              # Stylesheets
│       │   ├── 📄 us10_styles.css     # Main application styles
│       │   ├── 📄 auth_styles.css     # Authentication page styles
│       │   └── 📄 landing.css         # Landing page styles
│       └── 📁 js/               # JavaScript files
│           └── 📄 us10_dashboard.js   # Main dashboard functionality
├── 📁 database/                 # Database files
│   └── 📄 dr_resume_dev.db     # SQLite database
├── 📁 uploads/                  # User uploaded files
├── 📁 docs/                     # Documentation
│   ├── 📄 API.md               # API documentation
│   ├── 📄 BACKEND.md           # Backend documentation
│   ├── 📄 FRONTEND.md          # Frontend documentation
│   └── 📄 DATABASE.md          # Database schema
├── 📄 run_app.py               # Application launcher script
├── 📄 start_app.bat            # Windows batch file to start app
└── 📄 README.md                # Original project documentation
```

## 🔧 Technology Stack

### Backend
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **File Processing**: python-docx, PyPDF2
- **NLP**: Custom keyword extraction algorithms
- **API**: RESTful API design

### Frontend
- **Languages**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with responsive design
- **AJAX**: Fetch API for backend communication
- **UI/UX**: Modern, clean interface design

### Infrastructure
- **Development**: Local development server
- **Database**: SQLite (development), PostgreSQL (production ready)
- **File Storage**: Local filesystem
- **CORS**: Configured for cross-origin requests

## 🎯 How It Works

### User Workflow
1. **Register/Login**: Create account or login with existing credentials
2. **Upload Resume**: Upload PDF or DOCX resume file
3. **Add Job Description**: Paste or upload job description
4. **Keyword Extraction**: System automatically extracts keywords from both documents
5. **Generate Suggestions**: Click to generate basic or premium AI suggestions
6. **View Results**: See match scores, missing keywords, and improvement suggestions
7. **Track Progress**: View scan history and track improvements over time

### Technical Workflow
1. **File Upload**: Files are uploaded and stored securely
2. **Text Extraction**: PDF/DOCX files are parsed to extract text content
3. **Keyword Analysis**: Advanced NLP algorithms extract relevant keywords
4. **Matching Algorithm**: Sophisticated scoring system compares resume vs job requirements
5. **AI Suggestions**: Dynamic suggestion engine provides personalized recommendations
6. **Data Storage**: All data is stored securely with user isolation

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **User Isolation**: Each user can only access their own data
- **File Validation**: Uploaded files are validated for type and size
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Properly configured cross-origin resource sharing
- **Input Sanitization**: All user inputs are properly sanitized

## 📊 Database Schema

### Core Tables
- **Users**: User accounts and authentication
- **Resumes**: Uploaded resume files and metadata
- **JobDescriptions**: Job postings and requirements
- **MatchScores**: Calculated match scores between resumes and jobs
- **Suggestions**: AI-generated improvement suggestions
- **ScanHistory**: Historical record of all scans and analyses

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret-key"

# Run the application
python backend/app.py
```

### Production Deployment
The application is designed to be deployed on platforms like:
- **Heroku**: With PostgreSQL addon
- **AWS**: Using EC2 + RDS
- **DigitalOcean**: App Platform
- **Render**: Web service + PostgreSQL

## 🛠️ Development

### Adding New Features
1. **Backend**: Add new routes in `backend/routes/`
2. **Frontend**: Add new pages or update existing ones
3. **Database**: Update models in `backend/models.py`
4. **Services**: Add business logic in `backend/services/`

### Testing
- Manual testing through the web interface
- API testing using tools like Postman
- Database testing through SQLite browser

## 📝 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - User registration
- `POST /api/refresh` - Refresh JWT token

### Resume Management
- `POST /api/upload_resume` - Upload resume file
- `GET /api/resumes` - Get user's resumes
- `DELETE /api/resumes/{id}` - Delete resume

### Job Descriptions
- `POST /api/job_descriptions` - Add job description
- `GET /api/job_descriptions` - Get user's job descriptions
- `PUT /api/job_descriptions/{id}` - Update job description

### Analysis & Suggestions
- `POST /api/calculate_match` - Calculate match score
- `POST /api/basic_suggestions` - Generate basic suggestions
- `POST /api/premium_suggestions` - Generate premium suggestions
- `GET /api/latest_suggestions` - Get latest suggestions

### History & Account
- `GET /api/recent_activity` - Get scan history
- `GET /api/dashboard_stats` - Get dashboard statistics
- `PUT /api/account/profile` - Update user profile

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Interface**: Clean, professional design
- **Real-time Feedback**: Loading states and progress indicators
- **Error Handling**: User-friendly error messages
- **Accessibility**: Keyboard navigation and screen reader support

## 🔍 Troubleshooting

### Common Issues
1. **JWT Token Errors**: Ensure SECRET_KEY and JWT_SECRET_KEY match
2. **File Upload Issues**: Check file size limits and format support
3. **Database Errors**: Verify database file permissions
4. **CORS Issues**: Check frontend-backend URL configuration

### Debug Mode
Run with debug mode enabled:
```bash
export FLASK_DEBUG=1
python backend/app.py
```

## 📈 Future Enhancements

- **AI Integration**: OpenAI GPT integration for advanced suggestions
- **Resume Templates**: Pre-built resume templates
- **Job Board Integration**: Direct job search integration
- **Analytics Dashboard**: Advanced analytics and insights
- **Mobile App**: Native mobile application
- **Collaboration**: Team features for HR professionals

---

**Built with ❤️ for job seekers worldwide**
