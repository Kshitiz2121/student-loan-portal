#!/usr/bin/env python3
"""
Quick script to display sharing information for the Student Loan Portal
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

def display_sharing_info():
    """Display all sharing information"""
    ip = get_local_ip()
    url = f"http://{ip}:8000"
    
    print("=" * 60)
    print("STUDENT LOAN PORTAL - SHARING INFORMATION")
    print("=" * 60)
    
    print(f"\n🌐 TESTING URL:")
    print(f"   {url}")
    
    print(f"\n👥 TEST CREDENTIALS:")
    print(f"   Student 1: student1@test.com / testpass123")
    print(f"   Student 2: student2@test.com / testpass123")
    print(f"   Financier: financier@test.com / testpass123")
    print(f"   Admin: admin@test.com / admin123")
    
    print(f"\n📱 MOBILE ACCESS:")
    print(f"   • Connect to same WiFi network")
    print(f"   • Open browser on phone")
    print(f"   • Go to: {url}")
    
    print(f"\n💬 QUICK MESSAGE TO SHARE:")
    print("-" * 40)
    print(f"🧪 Testing my Student Loan Portal!")
    print(f"🌐 URL: {url}")
    print(f"👥 Login: student1@test.com / testpass123")
    print(f"📱 Test on mobile too!")
    print(f"💬 Share your feedback please!")
    print("-" * 40)
    
    print(f"\n📋 WHAT TO TEST:")
    print("   • Login with different user types")
    print("   • Apply for loans (as student)")
    print("   • Make repayments (try UPI)")
    print("   • Request withdrawals (as financier)")
    print("   • Manage loans (as admin)")
    print("   • Mobile responsiveness")
    
    print(f"\n🎯 FEEDBACK NEEDED:")
    print("   • How easy was it to use? (1-10)")
    print("   • What features did you like?")
    print("   • What was confusing?")
    print("   • How was mobile experience?")
    print("   • Any suggestions?")
    
    print(f"\n⚠️  IMPORTANT NOTES:")
    print("   • This is a TEST environment")
    print("   • No real money involved")
    print("   • Make sure testers are on same WiFi")
    print("   • Contact you if they have issues")
    
    print("\n" + "=" * 60)
    print("Ready to share! Copy the information above.")
    print("=" * 60)

def main():
    """Main function"""
    display_sharing_info()
    
    print("\n🚀 QUICK ACTIONS:")
    print("1. Copy the URL and credentials above")
    print("2. Share via WhatsApp, email, or social media")
    print("3. Ask testers to try both computer and mobile")
    print("4. Collect feedback and improve!")
    
    print("\n📁 Files created for sharing:")
    print("• SHARE_WITH_TESTERS.md - Detailed guide")
    print("• TESTER_INVITATION.txt - Simple text version")
    print("• SHARING_TEMPLATES.md - Templates for different platforms")

if __name__ == "__main__":
    main()

