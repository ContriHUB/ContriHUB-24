#!/bin/bash
# Setup script for ContriHUB-24 Django project

echo "🚀 Setting up ContriHUB-24 Django Project..."

# Step 1: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Step 2: Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Step 3: Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install Django==4.1
pip install python-decouple
pip install dj-database-url
pip install django-crispy-forms
pip install social-auth-app-django
pip install requests
pip install whitenoise

# Step 4: Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration file..."
    cat > .env << 'EOF'
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
EOF
fi

# Step 5: Run migrations
echo "🗄️ Setting up database..."
python manage.py migrate

# Step 6: Check if everything is working
echo "🔍 Checking Django configuration..."
python manage.py check

echo "✅ Setup complete!"
echo ""
echo "🎉 Your ContriHUB-24 project is ready!"
echo ""
echo "To start the development server, run:"
echo "   python manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000/"
echo "Projects page: http://127.0.0.1:8000/project/"
echo ""
echo "📝 To customize project list, edit PROJECT_NAMES in .env file"