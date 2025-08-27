# 🚀 Dr. Resume AI - Setup Guide

**Simple step-by-step guide to get the application running**

## ✅ Prerequisites

Before you start, make sure you have:
- **Python 3.8 or higher** installed on your computer
- **pip** (Python package manager) - usually comes with Python
- **Git** (optional, for cloning the repository)

### Check if you have Python:
```bash
python --version
# or
python3 --version
```

## 📥 Installation Steps

### Step 1: Get the Code
```bash
# If you have git:
git clone <repository-url>
cd resume-doctor.ai

# Or download and extract the ZIP file
```

### Step 2: Install Python Dependencies
```bash
# Navigate to the project folder
cd resume-doctor.ai

# Install required packages
pip install -r backend/requirements.txt

# If you get permission errors, try:
pip install --user -r backend/requirements.txt
```

### Step 3: Set Up Environment Variables
Create a file called `.env` in the `backend/` folder:

```bash
# Create the .env file
touch backend/.env
```

Add this content to `backend/.env`:
```env
SECRET_KEY=your-super-secret-key-here-change-this
JWT_SECRET_KEY=your-super-secret-key-here-change-this
DATABASE_URL=sqlite:///database/dr_resume_dev.db
```

**Important**: Change the secret keys to something unique and secure!

### Step 4: Run the Application
```bash
# Option 1: Use the launcher script
python run_app.py

# Option 2: Run directly
python backend/app.py
```

### Step 5: Open in Browser
Open your web browser and go to:
```
http://localhost:5000
```

## 🎉 You're Done!

You should see the Dr. Resume AI homepage. You can now:
1. **Register** a new account
2. **Login** with your credentials
3. **Upload** a resume (PDF or DOCX)
4. **Add** a job description
5. **Generate** AI suggestions

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "Module not found" errors
```bash
# Make sure you're in the right directory
cd resume-doctor.ai

# Reinstall dependencies
pip install -r backend/requirements.txt
```

#### "Permission denied" errors
```bash
# Try installing with user flag
pip install --user -r backend/requirements.txt

# Or use python -m pip
python -m pip install -r backend/requirements.txt
```

#### "Port already in use" error
```bash
# Kill any existing Python processes
# On Windows: Ctrl+C in the terminal
# On Mac/Linux: Ctrl+C or kill the process

# Or change the port in backend/app.py:
# app.run(host='0.0.0.0', port=5001, debug=True)
```

#### Database errors
```bash
# Delete the database file and restart
rm database/dr_resume_dev.db
python backend/app.py
```

#### File upload not working
- Make sure the `uploads/` folder exists
- Check file size (must be under 16MB)
- Only PDF and DOCX files are supported

## 🔍 Verifying Installation

### Test the API endpoints:
1. **Open browser**: Go to `http://localhost:5000`
2. **Register**: Create a new account
3. **Login**: Use your credentials
4. **Upload test**: Try uploading a small PDF or DOCX file
5. **Check logs**: Look at the terminal for any error messages

### Expected behavior:
- ✅ Homepage loads without errors
- ✅ Registration creates new account
- ✅ Login redirects to dashboard
- ✅ File upload shows success message
- ✅ Suggestions generate when clicked

## 📁 Project Structure After Setup

```
resume-doctor.ai/
├── backend/
│   ├── app.py                 # ← Main application file
│   ├── .env                   # ← Your environment variables
│   └── ...
├── database/
│   └── dr_resume_dev.db       # ← Created automatically
├── uploads/                   # ← User files stored here
└── frontend/                  # ← Web interface files
```

## 🎯 Next Steps

Once everything is working:

1. **Explore the interface**: Try all the features
2. **Upload real resumes**: Test with your actual resume
3. **Try different job descriptions**: See how suggestions change
4. **Check the documentation**: Read `PROJECT_OVERVIEW.md` for more details
5. **Customize**: Modify the code to fit your needs

## 🆘 Getting Help

If you're still having issues:

1. **Check the logs**: Look at the terminal output for error messages
2. **Verify Python version**: Make sure you have Python 3.8+
3. **Check file permissions**: Make sure you can read/write in the project folder
4. **Try a fresh install**: Delete everything and start over
5. **Check dependencies**: Make sure all packages installed correctly

## 🔄 Restarting the Application

To stop the application:
- Press `Ctrl+C` in the terminal

To start it again:
```bash
python backend/app.py
```

## 🌐 Accessing from Other Devices

To access from other devices on your network:
1. Find your computer's IP address
2. Change the app.py run command to:
   ```python
   app.run(host='0.0.0.0', port=5000, debug=True)
   ```
3. Access from other devices using: `http://YOUR_IP_ADDRESS:5000`

## 🔒 Security Notes

For development:
- The default settings are fine for local testing
- Don't use this setup for production without additional security

For production:
- Use strong, unique secret keys
- Use a proper database (PostgreSQL)
- Set up HTTPS
- Configure proper CORS settings
- Use environment variables for all secrets

---

**Happy coding! 🎉**

If you need more detailed information, check out:
- `PROJECT_OVERVIEW.md` - Complete project documentation
- `FILE_EXPLANATIONS.md` - Detailed code explanations
- `docs/` folder - Technical documentation
