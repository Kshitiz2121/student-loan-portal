# Student Loan Portal

A comprehensive Django web application for managing student loan applications, approvals, and repayments. Built with modern web technologies and designed for educational institutions.

## 🚀 Features

### User System
- **Custom Student User Model**: Extended Django User model with student-specific fields
- **Student Registration & Authentication**: Secure user registration with email-based login
- **Profile Management**: Students can update their personal information and view loan history
- **GPA-based Eligibility**: Automatic loan eligibility check based on GPA (≥6.0)

### Loan Application System
- **Smart Loan Applications**: Students can apply for loans ranging from ₹500 to ₹5,000 INR
- **Auto-approval System**: Instant approval for eligible students (GPA ≥6.0, no active loans)
- **Business Rules**: One active loan per student, comprehensive validation
- **Loan Calculator**: Built-in calculator showing interest and monthly payments

### Repayment Tracking
- **Flexible Payment Recording**: Multiple payment methods (UPI, Bank Transfer, Cash, etc.)
- **Progress Tracking**: Visual progress bars and repayment history
- **Overdue Management**: Automatic overdue detection and notifications
- **Payment Validation**: Prevents overpayment and ensures data integrity

### Admin Panel
- **Comprehensive Dashboard**: Overview of all loans, repayments, and statistics
- **Loan Management**: Approve/reject applications, manage loan statuses
- **Repayment Oversight**: Track all payments and manage overdue loans
- **Advanced Filtering**: Search and filter by various criteria

### Frontend
- **Modern UI/UX**: Built with Bootstrap 5 and custom CSS
- **Responsive Design**: Mobile-friendly interface for all devices
- **Interactive Elements**: Real-time calculators, progress bars, and notifications
- **Professional Styling**: Clean, modern design with intuitive navigation

### API System
- **RESTful APIs**: Django REST Framework with JWT authentication
- **Secure Endpoints**: Protected API routes for loan and repayment management
- **AJAX Integration**: Dynamic updates without page refreshes

## 🛠️ Technology Stack

- **Backend**: Django 5.0.6
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **API**: Django REST Framework, JWT Authentication
- **Deployment**: Gunicorn, WhiteNoise, Heroku/Render ready

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd student-loan-portal
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run the Application
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## 🗄️ Database Models

### StudentUser
- Extended Django User model
- Student-specific fields: student_id, university, GPA, phone, address
- GPA validation and loan eligibility methods

### LoanApplication
- Loan details: amount, reason, status, interest rate
- Automatic approval logic for eligible students
- Repayment due date management
- Overdue detection

### Repayment
- Payment tracking: amount, method, transaction ID
- Status management (Paid, Pending, Failed)
- Integration with loan applications

## 🔐 Authentication & Security

- **JWT Authentication**: Secure API access with JSON Web Tokens
- **Session Authentication**: Traditional Django session-based auth
- **Password Validation**: Django's built-in password strength requirements
- **CSRF Protection**: Cross-site request forgery protection
- **Secure Headers**: CORS configuration for API access

## 📱 API Endpoints

### Authentication
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Users
- `GET /api/users/profile/` - Get user profile
- `GET /api/users/loan-status/<id>/` - Get loan status
- `GET /api/users/repayment-summary/` - Get repayment summary

### Loans
- `POST /api/loans/approve/<id>/` - Approve loan (admin)
- `POST /api/loans/reject/<id>/` - Reject loan (admin)

### Repayments
- `POST /api/repayments/mark-paid/<id>/` - Mark repayment as paid
- `POST /api/repayments/mark-failed/<id>/` - Mark repayment as failed

## 🎨 Customization

### Styling
- Modify `templates/base.html` for global styling changes
- Update CSS in `static/css/` directory
- Customize Bootstrap variables in `static/css/custom.css`

### Business Logic
- Adjust GPA requirements in `users/models.py`
- Modify loan limits in `loans/models.py`
- Update interest rates and repayment periods

### Templates
- All templates are in the `templates/` directory
- Organized by app: `users/`, `loans/`, `repayments/`
- Base template provides consistent layout

## 🚀 Deployment

### Heroku
1. Install Heroku CLI
2. Create Heroku app
3. Set environment variables
4. Deploy with Git

### Render
1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy automatically

### Railway
1. Connect GitHub repository
2. Configure environment
3. Deploy with automatic builds

### Environment Variables for Production
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 📊 Admin Features

### Loan Management
- View all loan applications
- Approve/reject applications
- Set repayment due dates
- Monitor overdue loans

### User Management
- Manage student accounts
- View student profiles
- Monitor loan eligibility

### Repayment Tracking
- Track all payments
- Manage payment statuses
- Generate reports

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add docstrings to functions and classes

### Adding New Features
1. Create models in appropriate app
2. Add views and forms
3. Create templates
4. Update URLs
5. Add tests

## 📁 Project Structure

```
student-loan-portal/
├── loan_app/                 # Main Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── users/                    # User management app
│   ├── models.py            # StudentUser model
│   ├── views.py             # User views
│   ├── forms.py             # User forms
│   └── urls.py              # User URLs
├── loans/                    # Loan management app
│   ├── models.py            # LoanApplication model
│   ├── views.py             # Loan views
│   ├── forms.py             # Loan forms
│   └── urls.py              # Loan URLs
├── repayments/               # Repayment tracking app
│   ├── models.py            # Repayment model
│   ├── views.py             # Repayment views
│   ├── forms.py             # Repayment forms
│   └── urls.py              # Repayment URLs
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── users/               # User templates
│   ├── loans/               # Loan templates
│   └── repayments/          # Repayment templates
├── static/                   # Static files
├── media/                    # User uploads
├── requirements.txt          # Python dependencies
├── manage.py                # Django management script
└── README.md                # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact: support@studentloanportal.com
- Documentation: [Wiki](link-to-wiki)

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added API endpoints and JWT authentication
- **v1.2.0** - Enhanced admin dashboard and reporting
- **v1.3.0** - Mobile-responsive design and performance improvements

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive CSS framework
- Contributors and testers who helped improve the application

---

**Note**: This application is designed for educational purposes and should be thoroughly tested before use in production environments.
