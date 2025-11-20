#!/usr/bin/env python3
"""
Quick Deployment Script for Student Loan Portal

This script helps deploy the application to various platforms.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        'python': 'python --version',
        'pip': 'pip --version',
        'git': 'git --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        if not run_command(command, f"Checking {tool}"):
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        return False
    
    print("✅ All requirements met")
    return True

def prepare_deployment():
    """Prepare the application for deployment"""
    print("🚀 Preparing for deployment...")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        return False
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        return False
    
    print("✅ Deployment preparation completed")
    return True

def deploy_heroku():
    """Deploy to Heroku"""
    print("🚀 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    if not run_command("heroku --version", "Checking Heroku CLI"):
        print("❌ Heroku CLI not found. Please install it from https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    if app_name:
        create_cmd = f"heroku create {app_name}"
    else:
        create_cmd = "heroku create"
    
    if not run_command(create_cmd, "Creating Heroku app"):
        return False
    
    # Set environment variables
    env_vars = {
        'SECRET_KEY': 'your-secret-key-here',
        'DEBUG': 'False',
        'ALLOWED_HOSTS': 'your-app-name.herokuapp.com'
    }
    
    for key, value in env_vars.items():
        if not run_command(f"heroku config:set {key}={value}", f"Setting {key}"):
            return False
    
    # Deploy
    if not run_command("git add .", "Adding files to git"):
        return False
    
    if not run_command("git commit -m 'Deploy to Heroku'", "Committing changes"):
        return False
    
    if not run_command("git push heroku main", "Pushing to Heroku"):
        return False
    
    print("✅ Deployment to Heroku completed!")
    print("🌐 Your app should be available at: https://your-app-name.herokuapp.com")
    return True

def deploy_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    if not run_command("railway --version", "Checking Railway CLI"):
        print("❌ Railway CLI not found. Please install it from https://docs.railway.app/develop/cli")
        return False
    
    # Login to Railway
    if not run_command("railway login", "Logging into Railway"):
        return False
    
    # Initialize Railway project
    if not run_command("railway init", "Initializing Railway project"):
        return False
    
    # Deploy
    if not run_command("railway up", "Deploying to Railway"):
        return False
    
    print("✅ Deployment to Railway completed!")
    return True

def main():
    """Main deployment function"""
    print("🎯 Student Loan Portal Deployment Script")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    if not prepare_deployment():
        sys.exit(1)
    
    print("\n📋 Deployment Options:")
    print("1. Heroku (Recommended for beginners)")
    print("2. Railway (Modern platform)")
    print("3. Manual deployment instructions")
    
    choice = input("\nSelect deployment option (1-3): ").strip()
    
    if choice == "1":
        deploy_heroku()
    elif choice == "2":
        deploy_railway()
    elif choice == "3":
        print_manual_instructions()
    else:
        print("❌ Invalid choice")
        sys.exit(1)

def print_manual_instructions():
    """Print manual deployment instructions"""
    print("\n📖 Manual Deployment Instructions:")
    print("=" * 50)
    
    print("\n🌐 For Heroku:")
    print("1. Install Heroku CLI")
    print("2. Run: heroku create your-app-name")
    print("3. Run: git push heroku main")
    print("4. Set environment variables in Heroku dashboard")
    
    print("\n🌐 For Railway:")
    print("1. Install Railway CLI")
    print("2. Run: railway login")
    print("3. Run: railway init")
    print("4. Run: railway up")
    
    print("\n🌐 For VPS:")
    print("1. Set up Ubuntu/CentOS server")
    print("2. Install Python, PostgreSQL, Nginx")
    print("3. Clone your repository")
    print("4. Install dependencies and run migrations")
    print("5. Configure Nginx and SSL")
    
    print("\n🔧 Environment Variables to Set:")
    print("- SECRET_KEY")
    print("- DEBUG=False")
    print("- ALLOWED_HOSTS")
    print("- DATABASE_URL")
    print("- EMAIL settings")
    print("- Payment gateway credentials")

if __name__ == "__main__":
    main()
