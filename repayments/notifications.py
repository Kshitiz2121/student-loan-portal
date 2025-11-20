"""
Email notification system for the Student Loan Portal

This module handles sending email notifications for various events
like loan approvals, payment confirmations, withdrawal requests, etc.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def send_loan_approval_notification(loan_application):
    """Send email notification when a loan is approved"""
    try:
        student = loan_application.student
        subject = f"Loan Application Approved - Loan #{loan_application.id}"
        
        # Create email content
        context = {
            'student': student,
            'loan': loan_application,
            'total_amount': loan_application.total_amount_due,
            'monthly_payment': loan_application.monthly_payment,
            'due_date': loan_application.repayment_due_date,
        }
        
        # Render HTML email
        html_content = render_to_string('emails/loan_approval.html', context)
        text_content = render_to_string('emails/loan_approval.txt', context)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending loan approval notification: {e}")
        return False


def send_payment_confirmation_notification(repayment):
    """Send email notification when a payment is confirmed"""
    try:
        student = repayment.loan.student
        subject = f"Payment Confirmed - ₹{repayment.amount_paid}"
        
        # Create email content
        context = {
            'student': student,
            'repayment': repayment,
            'loan': repayment.loan,
            'payment_date': repayment.payment_date,
            'remaining_amount': repayment.loan.total_amount_due - sum(
                r.amount_paid for r in repayment.loan.repayments.filter(status='Paid')
            ),
        }
        
        # Render HTML email
        html_content = render_to_string('emails/payment_confirmation.html', context)
        text_content = render_to_string('emails/payment_confirmation.txt', context)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending payment confirmation notification: {e}")
        return False


def send_withdrawal_request_notification(withdrawal):
    """Send email notification when a withdrawal is requested"""
    try:
        financier = withdrawal.financier.user
        subject = f"Withdrawal Request Submitted - ₹{withdrawal.amount}"
        
        # Create email content
        context = {
            'financier': financier,
            'withdrawal': withdrawal,
            'request_date': withdrawal.created_at,
        }
        
        # Render HTML email
        html_content = render_to_string('emails/withdrawal_request.html', context)
        text_content = render_to_string('emails/withdrawal_request.txt', context)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[financier.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending withdrawal request notification: {e}")
        return False


def send_withdrawal_processed_notification(withdrawal):
    """Send email notification when a withdrawal is processed"""
    try:
        financier = withdrawal.financier.user
        subject = f"Withdrawal Processed - ₹{withdrawal.amount}"
        
        # Create email content
        context = {
            'financier': financier,
            'withdrawal': withdrawal,
            'processed_date': withdrawal.processed_at,
            'processed_by': withdrawal.processed_by,
        }
        
        # Render HTML email
        html_content = render_to_string('emails/withdrawal_processed.html', context)
        text_content = render_to_string('emails/withdrawal_processed.txt', context)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[financier.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending withdrawal processed notification: {e}")
        return False


def send_overdue_notification(loan_application):
    """Send email notification for overdue loans"""
    try:
        student = loan_application.student
        subject = f"Payment Overdue - Loan #{loan_application.id}"
        
        # Create email content
        context = {
            'student': student,
            'loan': loan_application,
            'overdue_days': loan_application.days_overdue,
            'total_amount': loan_application.total_amount_due,
            'due_date': loan_application.repayment_due_date,
        }
        
        # Render HTML email
        html_content = render_to_string('emails/loan_overdue.html', context)
        text_content = render_to_string('emails/loan_overdue.txt', context)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending overdue notification: {e}")
        return False


def send_welcome_notification(user):
    """Send welcome email to new users"""
    try:
        subject = "Welcome to Student Loan Portal"
        
        # Create email content
        context = {
            'user': user,
            'login_url': f"{settings.BASE_URL}/login/",
        }
        
        # Render HTML email
        html_content = render_to_string('emails/welcome.html', context)
        text_content = render_to_string('emails/welcome.txt', context)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending welcome notification: {e}")
        return False


def send_admin_notification(subject, message, admin_emails=None):
    """Send notification to admin users"""
    try:
        if not admin_emails:
            admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        
        if admin_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails),
                fail_silently=False,
            )
        
        return True
    except Exception as e:
        print(f"Error sending admin notification: {e}")
        return False
