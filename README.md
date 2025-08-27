# 🎯 Dr. Resume AI

**AI-powered resume optimization and job matching platform**

## 🚀 Quick Start

1. **Install Python 3.8+** and pip
2. **Install dependencies**: `pip install -r backend/requirements.txt`
3. **Create environment file**: Add `.env` file in `backend/` folder with your secret keys
4. **Run the app**: `python backend/app.py`
5. **Open browser**: Go to `http://localhost:5000`

## 📚 Documentation

- **📖 [Complete Project Overview](PROJECT_OVERVIEW.md)** - Detailed project documentation
- **📁 [File-by-File Explanations](FILE_EXPLANATIONS.md)** - Code explanations for beginners
- **🚀 [Setup Guide](SETUP_GUIDE.md)** - Step-by-step installation instructions

## 🌟 Features

- Resume upload and analysis (PDF/DOCX)
- Job description processing
- AI-powered keyword matching
- Smart improvement suggestions
- Match score calculation
- Scan history tracking
- User authentication & accounts

## 📁 Project Structure

```
resume-doctor.ai/
├── 📁 backend/                    # Backend Flask Application
│   ├── 📄 app.py                 # Main Flask application
│   ├── 📄 models.py              # Database models
│   ├── 📄 requirements.txt       # Python dependencies
│   ├── 📁 routes/                # API endpoints
│   ├── 📁 services/              # Business logic
│   └── 📁 middleware/            # Authentication middleware
├── 📁 frontend/                  # Frontend Web Interface
│   ├── 📄 us10_dashboard.html    # Main dashboard
│   ├── 📄 us10_login.html        # Login page
│   ├── 📄 us10_register.html     # Registration page
│   └── 📁 static/                # CSS, JS, assets
├── 📁 database/                  # Database files
├── 📁 uploads/                   # User uploaded files
├── 📁 docs/                      # Technical documentation
├── 📄 run_app.py                 # Application launcher
└── 📄 start_app.bat              # Windows startup script
```

## 🔧 Technology Stack

- **Backend**: Flask (Python), SQLite, JWT Authentication
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **File Processing**: PyPDF2, python-docx
- **AI/NLP**: Custom keyword extraction algorithms

## 🎯 How It Works

1. **Upload Resume** → System extracts text and keywords
2. **Add Job Description** → System analyzes requirements
3. **Generate Suggestions** → AI compares and creates recommendations
4. **View Results** → See match scores and improvement suggestions
5. **Track Progress** → Monitor your optimization journey

## 🔐 Security Features

- JWT token authentication
- User data isolation
- File validation and sanitization
- SQL injection protection
- CORS configuration

## 🚀 Deployment

The application can be deployed on:
- Local development server
- Heroku, AWS, DigitalOcean
- Any platform supporting Python/Flask

## 📈 Future Enhancements

- OpenAI GPT integration
- Resume templates
- Job board integration
- Mobile application
- Advanced analytics

---

**For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

## 🛠️ Development

### Running the Application
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set up environment variables in backend/.env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-secret-key

# Run the application
python backend/app.py
```

### Project Status
✅ **Fully Functional** - All core features working
✅ **Authentication** - Login/register system
✅ **File Upload** - PDF/DOCX resume processing
✅ **AI Suggestions** - Basic and premium recommendations
✅ **Match Scoring** - Resume-job compatibility analysis
✅ **User Dashboard** - Complete user interface
✅ **Data Persistence** - SQLite database storage

## 📞 Support

For questions or issues:
1. Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation help
2. Review [FILE_EXPLANATIONS.md](FILE_EXPLANATIONS.md) for code understanding
3. See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for complete documentation

---

**Built with ❤️ for job seekers worldwide**
