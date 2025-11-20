from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .forms import StudentUserCreationForm, StudentProfileForm
from .models import StudentUser
from loans.models import LoanApplication
from repayments.models import Repayment


class StudentRegistrationView(CreateView):
    """View for student registration"""
    model = StudentUser
    form_class = StudentUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        
        # Auto-login after registration
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, email=email, password=password)
        
        if user:
            login(self.request, user)
            messages.success(
                self.request, 
                f'Welcome {user.get_full_name()}! Your account has been created successfully.'
            )
            return redirect('users:dashboard')
        
        messages.success(
            self.request, 
            'Account created successfully! Please log in with your credentials.'
        )
        return response


class StudentLoginView(LoginView):
    """Custom login view for students"""
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('users:dashboard')
    
    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        return reverse_lazy('users:dashboard')


class StudentProfileView(LoginRequiredMixin, DetailView):
    """View for displaying student profile"""
    model = StudentUser
    template_name = 'users/profile.html'
    context_object_name = 'student'
    
    def get_object(self):
        """Return the current user"""
        return self.request.user
    
    def get_context_data(self, **kwargs):
        """Add loan and repayment data to context"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's loan applications
        context['loan_applications'] = LoanApplication.objects.filter(
            student=user
        ).order_by('-created_at')
        
        # Get user's repayments
        context['repayments'] = Repayment.objects.filter(
            loan__student=user
        ).order_by('-payment_date')
        
        # Calculate loan statistics
        context['total_loans'] = context['loan_applications'].count()
        context['approved_loans'] = context['loan_applications'].filter(status='Approved').count()
        context['pending_loans'] = context['loan_applications'].filter(status='Pending').count()
        context['rejected_loans'] = context['loan_applications'].filter(status='Rejected').count()
        
        # Calculate repayment statistics
        total_paid = sum(
            repayment.amount_paid 
            for repayment in context['repayments'].filter(status='Paid')
        )
        context['total_paid'] = total_paid
        
        # Check for payment defaults (overdue loans with unpaid amounts)
        payment_defaults = []
        for loan in context['loan_applications'].filter(status='Approved'):
            # Calculate remaining amount for this loan
            loan_total_paid = sum(
                r.amount_paid for r in loan.repayments.filter(status='Paid')
            )
            remaining_amount = loan.total_amount_due - loan_total_paid
            
            # Check if loan is overdue and has unpaid amount
            if loan.is_overdue and remaining_amount > 0:
                payment_defaults.append({
                    'loan': loan,
                    'remaining_amount': remaining_amount,
                    'days_overdue': loan.days_overdue,
                    'due_date': loan.repayment_due_date,
                })
        
        context['payment_defaults'] = payment_defaults
        context['has_payment_default'] = len(payment_defaults) > 0
        context['default_count'] = len(payment_defaults)
        
        return context


class StudentProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating student profile"""
    model = StudentUser
    form_class = StudentProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        """Return the current user"""
        return self.request.user
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


@login_required
def dashboard(request):
    """Student dashboard view"""
    user = request.user
    
    # Get user's loan applications
    loan_applications = LoanApplication.objects.filter(
        student=user
    ).order_by('-created_at')
    
    # Get user's repayments
    repayments = Repayment.objects.filter(
        loan__student=user
    ).order_by('-payment_date')
    
    # Get active loan (if any)
    active_loan = loan_applications.filter(status='Approved').first()
    
    # Calculate statistics
    total_loans = loan_applications.count()
    approved_loans = loan_applications.filter(status='Approved').count()
    pending_loans = loan_applications.filter(status='Pending').count()
    rejected_loans = loan_applications.filter(status='Rejected').count()
    
    total_paid = sum(
        repayment.amount_paid 
        for repayment in repayments.filter(status='Paid')
    )
    
    # Calculate reminder information
    overdue_loans = []
    upcoming_due_loans = []
    total_remaining = 0
    
    for loan in loan_applications.filter(status='Approved'):
        # Calculate remaining amount
        loan_total_paid = sum(
            r.amount_paid for r in loan.repayments.filter(status='Paid')
        )
        remaining_amount = loan.total_amount_due - loan_total_paid
        
        # Skip if fully paid
        if remaining_amount <= 0:
            continue
        
        total_remaining += remaining_amount
        
        # Check if overdue
        if loan.is_overdue:
            overdue_loans.append({
                'loan': loan,
                'remaining_amount': remaining_amount,
                'days_overdue': loan.days_overdue,
            })
        # Check if due soon (within 7 days)
        elif loan.days_until_due is not None and loan.days_until_due <= 7:
            upcoming_due_loans.append({
                'loan': loan,
                'remaining_amount': remaining_amount,
                'days_until_due': loan.days_until_due,
            })
    
    context = {
        'user': user,
        'loan_applications': loan_applications[:5],  # Show only recent 5
        'repayments': repayments[:5],  # Show only recent 5
        'active_loan': active_loan,
        'total_loans': total_loans,
        'approved_loans': approved_loans,
        'pending_loans': pending_loans,
        'rejected_loans': rejected_loans,
        'total_paid': total_paid,
        'overdue_loans': overdue_loans,
        'upcoming_due_loans': upcoming_due_loans,
        'total_remaining': total_remaining,
        'has_reminders': len(overdue_loans) > 0 or len(upcoming_due_loans) > 0,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def loan_history(request):
    """View for displaying complete loan history"""
    user = request.user
    loan_applications = LoanApplication.objects.filter(
        student=user
    ).order_by('-created_at')
    
    context = {
        'loan_applications': loan_applications,
        'user': user,
    }
    
    return render(request, 'users/loan_history.html', context)


@login_required
def repayment_history(request):
    """View for displaying complete repayment history"""
    user = request.user
    repayments = Repayment.objects.filter(
        loan__student=user
    ).order_by('-payment_date')
    
    context = {
        'repayments': repayments,
        'user': user,
    }
    
    return render(request, 'users/repayment_history.html', context)


# API Views for AJAX requests
@login_required
@require_http_methods(["GET"])
def get_loan_status(request, loan_id):
    """API endpoint to get loan status"""
    try:
        loan = get_object_or_404(LoanApplication, id=loan_id, student=request.user)
        data = {
            'id': loan.id,
            'amount': loan.amount,
            'status': loan.status,
            'created_at': loan.created_at.strftime('%B %d, %Y'),
            'repayment_due_date': loan.repayment_due_date.strftime('%B %d, %Y') if loan.repayment_due_date else None,
            'is_overdue': loan.is_overdue,
            'total_amount_due': float(loan.total_amount_due),
            'days_until_due': loan.days_until_due,
        }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
def get_repayment_summary(request):
    """API endpoint to get repayment summary"""
    try:
        user = request.user
        active_loan = LoanApplication.objects.filter(
            student=user, status='Approved'
        ).first()
        
        if not active_loan:
            return JsonResponse({
                'success': True, 
                'data': {'has_active_loan': False}
            })
        
        total_paid = sum(
            repayment.amount_paid 
            for repayment in active_loan.repayments.filter(status='Paid')
        )
        
        remaining_amount = active_loan.total_amount_due - total_paid
        
        data = {
            'has_active_loan': True,
            'loan_id': active_loan.id,
            'total_amount_due': float(active_loan.total_amount_due),
            'total_paid': float(total_paid),
            'remaining_amount': float(remaining_amount),
            'is_overdue': active_loan.is_overdue,
            'days_until_due': active_loan.days_until_due,
        }
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
