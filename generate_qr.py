#!/usr/bin/env python3
"""
Generate QR code for easy mobile access to the Student Loan Portal
"""

try:
    import qrcode
    from PIL import Image
    import io
    import base64
    
    def generate_qr_code():
        """Generate QR code for the testing URL"""
        url = "http://192.168.1.7:8000"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        img.save("testing_qr_code.png")
        print("✅ QR code generated: testing_qr_code.png")
        print(f"📱 URL: {url}")
        print("\nShare this QR code with testers for easy mobile access!")
        
        return True
        
    if __name__ == "__main__":
        generate_qr_code()
        
except ImportError:
    print("❌ QR code library not installed")
    print("📦 Install with: pip install qrcode[pil]")
    print("🔗 Or share the URL directly: http://192.168.1.7:8000")

