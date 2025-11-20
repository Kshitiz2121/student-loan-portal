#!/usr/bin/env python3
"""
Quick Testing Setup Script
Run this to immediately set up your Student Loan Portal for user testing
"""

import os
import sys
import subprocess
import socket

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def setup_testing_environment():
    """Set up the testing environment"""
    print("🧪 Setting up Student Loan Portal for Testing")
    print("="*50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        return False
    
    # Create test users
    if not run_command("python create_test_users.py", "Creating test users"):
        return False
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        return False
    
    return True

def start_testing_server():
    """Start the testing server"""
    print("\n🚀 Starting Testing Server")
    print("="*30)
    
    local_ip = get_local_ip()
    
    print(f"📱 Local Access: http://localhost:8000")
    print(f"🌐 Network Access: http://{local_ip}:8000")
    print(f"📧 Share this URL with testers: http://{local_ip}:8000")
    
    print("\n👥 Test Credentials:")
    print("Student: test_student1 / testpass123")
    print("Financier: test_financier1 / testpass123")
    print("Admin: admin / admin123")
    
    print("\n🎯 Testing Features:")
    print("✅ User Registration & Login")
    print("✅ Loan Applications")
    print("✅ Payment Processing")
    print("✅ Withdrawal Requests")
    print("✅ Mobile Responsive Design")
    print("✅ Multi-language Support")
    
    print(f"\n🔥 Starting server on {local_ip}:8000...")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    try:
        subprocess.run(["python", "manage.py", "runserver", f"{local_ip}:8000"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

def main():
    """Main function"""
    print("🎯 Student Loan Portal - Quick Testing Setup")
    print("="*50)
    
    # Setup testing environment
    if not setup_testing_environment():
        print("\n❌ Setup failed. Please check the errors above.")
        return
    
    print("\n✅ Testing environment ready!")
    
    # Ask user if they want to start the server
    response = input("\n🚀 Start the testing server now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        start_testing_server()
    else:
        print("\n📋 Manual Start Instructions:")
        print("Run this command to start the testing server:")
        print(f"python manage.py runserver 0.0.0.0:8000")
        print(f"\nThen share this URL with testers: http://{get_local_ip()}:8000")

if __name__ == "__main__":
    main()
