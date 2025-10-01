# PowerShell Setup Script for ContriHUB-24 Django Project

Write-Host "🚀 Setting up ContriHUB-24 Django Project..." -ForegroundColor Green

# Step 1: Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Step 2: Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Step 3: Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install Django==4.1
pip install python-decouple
pip install dj-database-url
pip install django-crispy-forms
pip install social-auth-app-django
pip install requests
pip install whitenoise

# Step 4: Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "⚙️ Creating .env configuration file..." -ForegroundColor Yellow
    @"
# Django Configuration
SECRET_KEY=django-insecure-development-key-change-in-production
DEBUG=True
BASE_URL=

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Project Configuration
PROJECT_NAMES=ContriHUB-24,CodeSangam,MovieScreen,EyeProtection

# GitHub API Configuration
GITHUB_ORG_NAME=ContriHUB
GITHUB_API_TOKEN=

# Optional GitHub OAuth (for login functionality)
SOCIAL_AUTH_GITHUB_KEY=
SOCIAL_AUTH_GITHUB_SECRET=

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Labels Configuration
LABEL_MENTOR=mentor
LABEL_LEVEL=level
LABEL_POINTS=points
LABEL_RESTRICTED=restricted
DEPENDABOT_LOGIN=dependabot[bot]

# Issue and Points Configuration
MAX_SIMULTANEOUS_ISSUE=2
DAYS_PER_ISSUE_FREE=1
DAYS_PER_ISSUE_VERY_EASY=1
DAYS_PER_ISSUE_EASY=1
DAYS_PER_ISSUE_MEDIUM=2
DAYS_PER_ISSUE_HARD=3
DEFAULT_FREE_POINTS=0
DEFAULT_VERY_EASY_POINTS=2
DEFAULT_EASY_POINTS=10
DEFAULT_MEDIUM_POINTS=20
DEFAULT_HARD_POINTS=30
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

# Step 5: Run migrations
Write-Host "🗄️ Setting up database..." -ForegroundColor Yellow
python manage.py migrate

# Step 6: Check if everything is working
Write-Host "🔍 Checking Django configuration..." -ForegroundColor Yellow
python manage.py check

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Your ContriHUB-24 project is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the development server, run:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Then visit: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "Projects page: http://127.0.0.1:8000/project/" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 To customize project list, edit PROJECT_NAMES in .env file" -ForegroundColor Yellow