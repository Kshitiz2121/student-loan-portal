from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Sum
from django.core.paginator import Paginator

from .forms import LoanApplicationForm, LoanApplicationUpdateForm
from .models import LoanApplication
from users.models import StudentUser
from repayments.models import Repayment


class LoanApplicationCreateView(LoginRequiredMixin, CreateView):
    """View for students to apply for loans"""
    model = LoanApplication
    form_class = LoanApplicationForm
    template_name = 'loans/apply.html'
    success_url = reverse_lazy('dashboard')
    
    def get_form_kwargs(self):
        """Pass user to form for validation"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Handle successful form submission"""
        form.instance.student = self.request.user
        
        # Check if user is eligible for loan
        if not self.request.user.is_eligible_for_loan:
            messages.error(
                self.request, 
                'You are not eligible for a loan. Your GPA must be 6.0 or higher.'
            )
            return self.form_invalid(form)
        
        # Check if user already has an active loan
        if self.request.user.has_active_loan:
            messages.error(
                self.request, 
                'You already have an active loan. Please complete repayment before applying for a new one.'
            )
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        
        if form.instance.status == 'Approved':
            messages.success(
                self.request, 
                f'Congratulations! Your loan application for ₹{form.instance.amount} has been auto-approved!'
            )
        else:
            messages.success(
                self.request, 
                f'Your loan application for ₹{form.instance.amount} has been submitted successfully and is pending approval.'
            )
        
        return response


class LoanApplicationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View for displaying loan application details"""
    model = LoanApplication
    template_name = 'loans/detail.html'
    context_object_name = 'loan'
    
    def test_func(self):
        """Check if user can view this loan"""
        loan = self.get_object()
        return self.request.user == loan.student or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        """Add repayment data to context"""
        context = super().get_context_data(**kwargs)
        loan = self.get_object()
        
        # Get repayments for this loan
        context['repayments'] = loan.repayments.all().order_by('-payment_date')
        
        # Calculate repayment statistics
        total_paid = context['repayments'].filter(status='Paid').aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        context['total_paid'] = total_paid
        context['remaining_amount'] = loan.total_amount_due - total_paid
        context['repayment_progress'] = (total_paid / loan.total_amount_due) * 100 if loan.total_amount_due > 0 else 0
        
        return context


class LoanApplicationListView(LoginRequiredMixin, ListView):
    """View for listing loan applications"""
    model = LoanApplication
    template_name = 'loans/list.html'
    context_object_name = 'loans'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter loans based on user role"""
        if self.request.user.is_staff:
            # Admin sees all loans
            return LoanApplication.objects.all().select_related('student').order_by('-created_at')
        else:
            # Students see only their own loans
            return LoanApplication.objects.filter(
                student=self.request.user
            ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add search and filter context"""
        context = super().get_context_data(**kwargs)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        
        queryset = self.get_queryset()
        
        if search_query:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query) |
                Q(student__student_id__icontains=search_query) |
                Q(reason__icontains=search_query)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Pagination
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        context['status_choices'] = LoanApplication.STATUS_CHOICES
        
        return context


@login_required
def apply_loan(request):
    """Function-based view for loan application"""
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.student = request.user
            # Persist chosen university to user if eligible list item
            selected_university = form.cleaned_data.get('university')
            if selected_university and getattr(request.user, 'university', None) != selected_university:
                request.user.university = selected_university
                request.user.save(update_fields=['university'])
            
            # Check eligibility
            if not request.user.is_eligible_for_loan:
                messages.error(
                    request, 
                    'You are not eligible for a loan. Your GPA must be 6.0 or higher.'
                )
                return render(request, 'loans/apply.html', {'form': form})
            
            # Check for active loans
            if request.user.has_active_loan:
                messages.error(
                    request, 
                    'You already have an active loan. Please complete repayment before applying for a new one.'
                )
                return render(request, 'loans/apply.html', {'form': form})
            
            loan.save()
            
            if loan.status == 'Approved':
                messages.success(
                    request, 
                    f'Congratulations! Your loan application for ₹{loan.amount} has been auto-approved!'
                )
            else:
                messages.success(
                    request, 
                    f'Your loan application for ₹{loan.amount} has been submitted successfully and is pending approval.'
                )
            
            return redirect('dashboard')
    else:
        form = LoanApplicationForm(user=request.user)
    
    return render(request, 'loans/apply.html', {'form': form})


@staff_member_required
def admin_loan_management(request):
    """Admin view for managing loan applications"""
    loans = LoanApplication.objects.all().select_related('student').order_by('-created_at')
    
    # Statistics
    total_loans = loans.count()
    pending_loans = loans.filter(status='Pending').count()
    approved_loans = loans.filter(status='Approved').count()
    rejected_loans = loans.filter(status='Rejected').count()
    overdue_loans = sum(1 for loan in loans.filter(status='Approved') if loan.is_overdue)
    
    # Search and filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        loans = loans.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query) |
            Q(reason__icontains=search_query)
        )
    
    if status_filter:
        loans = loans.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(loans, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'loans': page_obj,
        'total_loans': total_loans,
        'pending_loans': pending_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'overdue_loans': overdue_loans,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': LoanApplication.STATUS_CHOICES,
    }
    
    return render(request, 'loans/admin_management.html', context)


@staff_member_required
@require_http_methods(["POST"])
def approve_loan(request, loan_id):
    """API endpoint to approve a loan"""
    try:
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'Approved'
        loan.admin_notes = f"Approved by admin on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        loan.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Loan #{loan.id} approved successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })


@staff_member_required
@require_http_methods(["POST"])
def reject_loan(request, loan_id):
    """API endpoint to reject a loan"""
    try:
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'Rejected'
        loan.admin_notes = f"Rejected by admin on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        loan.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Loan #{loan.id} rejected successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })


@login_required
def loan_statistics(request):
    """View for displaying loan statistics"""
    user = request.user
    
    if user.is_staff:
        # Admin sees all statistics
        total_loans = LoanApplication.objects.count()
        pending_loans = LoanApplication.objects.filter(status='Pending').count()
        approved_loans = LoanApplication.objects.filter(status='Approved').count()
        rejected_loans = LoanApplication.objects.filter(status='Rejected').count()
        overdue_loans = sum(
            1 for loan in LoanApplication.objects.filter(status='Approved') 
            if loan.is_overdue
        )
        
        # Total amount statistics
        total_amount_approved = LoanApplication.objects.filter(
            status='Approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_amount_pending = LoanApplication.objects.filter(
            status='Pending'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
    else:
        # Students see their own statistics
        user_loans = LoanApplication.objects.filter(student=user)
        total_loans = user_loans.count()
        pending_loans = user_loans.filter(status='Pending').count()
        approved_loans = user_loans.filter(status='Approved').count()
        rejected_loans = user_loans.filter(status='Rejected').count()
        overdue_loans = sum(
            1 for loan in user_loans.filter(status='Approved') 
            if loan.is_overdue
        )
        
        # Total amount statistics
        total_amount_approved = user_loans.filter(
            status='Approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_amount_pending = user_loans.filter(
            status='Pending'
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'total_loans': total_loans,
        'pending_loans': pending_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'overdue_loans': overdue_loans,
        'total_amount_approved': total_amount_approved,
        'total_amount_pending': total_amount_pending,
        'user': user,
    }
    
    return render(request, 'loans/statistics.html', context)
