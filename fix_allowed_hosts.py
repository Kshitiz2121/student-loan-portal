#!/usr/bin/env python3
"""
Quick fix for ALLOWED_HOSTS issue
"""

import socket

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.7"  # Fallback

def update_allowed_hosts():
    """Update ALLOWED_HOSTS in settings.py"""
    ip = get_local_ip()
    
    # Read current settings
    with open('loan_app/settings.py', 'r') as f:
        content = f.read()
    
    # Replace ALLOWED_HOSTS line
    old_line = "ALLOWED_HOSTS = []"
    new_line = f"ALLOWED_HOSTS = ['localhost', '127.0.0.1', '{ip}', '*']"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Write back to file
        with open('loan_app/settings.py', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated ALLOWED_HOSTS with IP: {ip}")
        print("🔄 Please restart your Django server:")
        print("   1. Press Ctrl+C to stop current server")
        print("   2. Run: python manage.py runserver 0.0.0.0:8000")
        return True
    else:
        print("⚠️  ALLOWED_HOSTS line not found or already updated")
        return False

def main():
    """Main function"""
    print("🔧 Fixing ALLOWED_HOSTS issue...")
    update_allowed_hosts()
    
    ip = get_local_ip()
    print(f"\n🌐 Your testing URL: http://{ip}:8000")
    print("👥 Test credentials:")
    print("   Student: student1@test.com / testpass123")
    print("   Financier: financier@test.com / testpass123")
    print("   Admin: admin@test.com / admin123")

if __name__ == "__main__":
    main()







