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
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator

from .forms import RepaymentForm, RepaymentUpdateForm, WithdrawalForm, WithdrawalUpdateForm
from .models import Repayment, Withdrawal
from .payment_gateway import process_payment, verify_payment
from .notifications import (
    send_payment_confirmation_notification,
    send_withdrawal_request_notification,
    send_withdrawal_processed_notification
)
from loans.models import LoanApplication
from users.models import StudentUser, FinancierUser


class RepaymentCreateView(LoginRequiredMixin, CreateView):
    """View for students to record repayments"""
    model = Repayment
    form_class = RepaymentForm
    template_name = 'repayments/create.html'
    success_url = reverse_lazy('dashboard')
    
    def get_form_kwargs(self):
        """Pass loan to form for validation"""
        kwargs = super().get_form_kwargs()
        loan_id = self.kwargs.get('loan_id')
        if loan_id:
            kwargs['loan'] = get_object_or_404(LoanApplication, id=loan_id, student=self.request.user)
        return kwargs
    
    def form_valid(self, form):
        """Handle successful form submission"""
        loan_id = self.kwargs.get('loan_id')
        loan = get_object_or_404(LoanApplication, id=loan_id, student=self.request.user)
        
        # Check if loan is approved
        if loan.status != 'Approved':
            messages.error(
                self.request, 
                'You can only make repayments for approved loans.'
            )
            return self.form_invalid(form)
        
        form.instance.loan = loan
        
        # Check if payment amount exceeds remaining loan amount
        total_paid = loan.repayments.filter(status='Paid').aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        remaining_amount = loan.total_amount_due - total_paid
        
        if form.instance.amount_paid > remaining_amount:
            messages.error(
                self.request, 
                f'Payment amount cannot exceed remaining loan amount (₹{remaining_amount:.2f}).'
            )
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        
        # Send payment confirmation email
        try:
            send_payment_confirmation_notification(form.instance)
        except Exception as e:
            print(f"Error sending payment confirmation email: {e}")
        
        messages.success(
            self.request, 
            f'Repayment of ₹{form.instance.amount_paid} recorded successfully!'
        )
        
        return response
    
    def get_context_data(self, **kwargs):
        """Add loan information to context"""
        context = super().get_context_data(**kwargs)
        loan_id = self.kwargs.get('loan_id')
        if loan_id:
            loan = get_object_or_404(LoanApplication, id=loan_id, student=self.request.user)
            context['loan'] = loan
            
            # Calculate remaining amount
            total_paid = loan.repayments.filter(status='Paid').aggregate(
                total=Sum('amount_paid')
            )['total'] or 0
            context['remaining_amount'] = loan.total_amount_due - total_paid
        
        return context


class RepaymentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View for displaying repayment details"""
    model = Repayment
    template_name = 'repayments/detail.html'
    context_object_name = 'repayment'
    
    def test_func(self):
        """Check if user can view this repayment"""
        repayment = self.get_object()
        return self.request.user == repayment.loan.student or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        """Add loan information to context"""
        context = super().get_context_data(**kwargs)
        repayment = self.get_object()
        context['loan'] = repayment.loan
        return context


class RepaymentListView(LoginRequiredMixin, ListView):
    """View for listing repayments"""
    model = Repayment
    template_name = 'repayments/list.html'
    context_object_name = 'repayments'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter repayments based on user role"""
        if self.request.user.is_staff:
            # Admin sees all repayments
            return Repayment.objects.all().select_related('loan__student').order_by('-payment_date')
        else:
            # Students see only their own repayments
            return Repayment.objects.filter(
                loan__student=self.request.user
            ).select_related('loan').order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        """Add search and filter context"""
        context = super().get_context_data(**kwargs)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        payment_method_filter = self.request.GET.get('payment_method', '')
        
        queryset = self.get_queryset()
        
        if search_query:
            queryset = queryset.filter(
                Q(loan__student__first_name__icontains=search_query) |
                Q(loan__student__last_name__icontains=search_query) |
                Q(loan__student__student_id__icontains=search_query) |
                Q(transaction_id__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if payment_method_filter:
            queryset = queryset.filter(payment_method=payment_method_filter)
        
        # Pagination
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Add reminder information for students
        overdue_loans = []
        upcoming_due_loans = []
        total_remaining = 0
        
        if not self.request.user.is_staff:
            # Get all approved loans for the student
            student_loans = LoanApplication.objects.filter(
                student=self.request.user,
                status='Approved'
            ).select_related('student')
            
            for loan in student_loans:
                # Calculate remaining amount
                total_paid = loan.repayments.filter(status='Paid').aggregate(
                    total=Sum('amount_paid')
                )['total'] or 0
                remaining_amount = loan.total_amount_due - total_paid
                
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
                        'due_date': loan.repayment_due_date,
                    })
                # Check if due soon (within 7 days)
                elif loan.days_until_due is not None and loan.days_until_due <= 7:
                    upcoming_due_loans.append({
                        'loan': loan,
                        'remaining_amount': remaining_amount,
                        'days_until_due': loan.days_until_due,
                        'due_date': loan.repayment_due_date,
                    })
        
        context['page_obj'] = page_obj
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        context['payment_method_filter'] = payment_method_filter
        context['status_choices'] = Repayment.STATUS_CHOICES
        context['payment_method_choices'] = [
            ('Manual Entry', 'Manual Entry'),
            ('UPI', 'UPI'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Cash', 'Cash'),
            ('Cheque', 'Cheque'),
            ('Credit Card', 'Credit Card'),
            ('Debit Card', 'Debit Card'),
        ]
        context['overdue_loans'] = overdue_loans
        context['upcoming_due_loans'] = upcoming_due_loans
        context['total_remaining'] = total_remaining
        context['has_reminders'] = len(overdue_loans) > 0 or len(upcoming_due_loans) > 0
        
        return context


@login_required
def record_repayment(request, loan_id):
    """Function-based view for recording repayments"""
    loan = get_object_or_404(LoanApplication, id=loan_id, student=request.user)
    
    # Check if loan is approved
    if loan.status != 'Approved':
        messages.error(request, 'You can only make repayments for approved loans.')
        return redirect('loans:detail', pk=loan_id)
    
    if request.method == 'POST':
        form = RepaymentForm(request.POST, loan=loan)
        if form.is_valid():
            repayment = form.save(commit=False)
            repayment.loan = loan
            
            # Check if payment amount exceeds remaining loan amount
            total_paid = loan.repayments.filter(status='Paid').aggregate(
                total=Sum('amount_paid')
            )['total'] or 0
            
            remaining_amount = loan.total_amount_due - total_paid
            
            if repayment.amount_paid > remaining_amount:
                messages.error(
                    request, 
                    f'Payment amount cannot exceed remaining loan amount (₹{remaining_amount:.2f}).'
                )
                return render(request, 'repayments/create.html', {'form': form, 'loan': loan})
            
            repayment.save()
            
            messages.success(
                request, 
                f'Repayment of ₹{repayment.amount_paid} recorded successfully!'
            )
            
            return redirect('loans:detail', pk=loan_id)
    else:
        form = RepaymentForm(loan=loan)
    
    # Calculate remaining amount
    total_paid = loan.repayments.filter(status='Paid').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    remaining_amount = loan.total_amount_due - total_paid
    
    context = {
        'form': form,
        'loan': loan,
        'remaining_amount': remaining_amount,
    }
    
    return render(request, 'repayments/create.html', context)


@staff_member_required
def admin_repayment_management(request):
    """Admin view for managing repayments"""
    repayments = Repayment.objects.all().select_related('loan__student').order_by('-payment_date')
    
    # Statistics
    total_repayments = repayments.count()
    paid_repayments = repayments.filter(status='Paid').count()
    pending_repayments = repayments.filter(status='Pending').count()
    failed_repayments = repayments.filter(status='Failed').count()
    
    total_amount_paid = repayments.filter(status='Paid').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    # Search and filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    payment_method_filter = request.GET.get('payment_method', '')
    
    if search_query:
        repayments = repayments.filter(
            Q(loan__student__first_name__icontains=search_query) |
            Q(loan__student__last_name__icontains=search_query) |
            Q(loan__student__student_id__icontains=search_query) |
            Q(transaction_id__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    if status_filter:
        repayments = repayments.filter(status=status_filter)
    
    if payment_method_filter:
        repayments = repayments.filter(payment_method=payment_method_filter)
    
    # Pagination
    paginator = Paginator(repayments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'repayments': page_obj,
        'total_repayments': total_repayments,
        'paid_repayments': paid_repayments,
        'pending_repayments': pending_repayments,
        'failed_repayments': failed_repayments,
        'total_amount_paid': total_amount_paid,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_method_filter': payment_method_filter,
        'status_choices': Repayment.STATUS_CHOICES,
        'payment_method_choices': [
            ('Manual Entry', 'Manual Entry'),
            ('UPI', 'UPI'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Cash', 'Cash'),
            ('Cheque', 'Cheque'),
            ('Credit Card', 'Credit Card'),
            ('Debit Card', 'Debit Card'),
        ],
    }
    
    return render(request, 'repayments/admin_management.html', context)


@staff_member_required
@require_http_methods(["POST"])
def mark_repayment_paid(request, repayment_id):
    """API endpoint to mark a repayment as paid"""
    try:
        repayment = get_object_or_404(Repayment, id=repayment_id)
        repayment.status = 'Paid'
        repayment.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Repayment #{repayment.id} marked as paid successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })


@staff_member_required
@require_http_methods(["POST"])
def mark_repayment_failed(request, repayment_id):
    """API endpoint to mark a repayment as failed"""
    try:
        repayment = get_object_or_404(Repayment, id=repayment_id)
        repayment.status = 'Failed'
        repayment.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Repayment #{repayment.id} marked as failed successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })


@login_required
def repayment_statistics(request):
    """View for displaying repayment statistics"""
    user = request.user
    
    if user.is_staff:
        # Admin sees all statistics
        total_repayments = Repayment.objects.count()
        paid_repayments = Repayment.objects.filter(status='Paid').count()
        pending_repayments = Repayment.objects.filter(status='Pending').count()
        failed_repayments = Repayment.objects.filter(status='Failed').count()
        
        total_amount_paid = Repayment.objects.filter(status='Paid').aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        # Payment method statistics
        payment_method_stats = Repayment.objects.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('amount_paid')
        ).order_by('-count')
        
    else:
        # Students see their own statistics
        user_repayments = Repayment.objects.filter(loan__student=user)
        total_repayments = user_repayments.count()
        paid_repayments = user_repayments.filter(status='Paid').count()
        pending_repayments = user_repayments.filter(status='Pending').count()
        failed_repayments = user_repayments.filter(status='Failed').count()
        
        total_amount_paid = user_repayments.filter(status='Paid').aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        # Payment method statistics
        payment_method_stats = user_repayments.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('amount_paid')
        ).order_by('-count')
    
    context = {
        'total_repayments': total_repayments,
        'paid_repayments': paid_repayments,
        'pending_repayments': pending_repayments,
        'failed_repayments': failed_repayments,
        'total_amount_paid': total_amount_paid,
        'payment_method_stats': payment_method_stats,
        'user': user,
    }
    
    return render(request, 'repayments/statistics.html', context)


@login_required
def repayment_summary(request):
    """API endpoint to get repayment summary for dashboard"""
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
        
        total_paid = active_loan.repayments.filter(status='Paid').aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        remaining_amount = active_loan.total_amount_due - total_paid
        
        data = {
            'has_active_loan': True,
            'loan_id': active_loan.id,
            'total_amount_due': float(active_loan.total_amount_due),
            'total_paid': float(total_paid),
            'remaining_amount': float(remaining_amount),
            'is_overdue': active_loan.is_overdue,
            'days_until_due': active_loan.days_until_due,
            'repayment_progress': (total_paid / active_loan.total_amount_due) * 100 if active_loan.total_amount_due > 0 else 0,
        }
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Withdrawal Views

class WithdrawalCreateView(LoginRequiredMixin, CreateView):
    """View for financiers to request withdrawals"""
    model = Withdrawal
    form_class = WithdrawalForm
    template_name = 'repayments/withdrawal_create.html'
    success_url = reverse_lazy('withdrawal_list')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        # Get financier profile
        try:
            financier = self.request.user.financier_profile
        except FinancierUser.DoesNotExist:
            messages.error(
                self.request, 
                'You must be a registered financier to request withdrawals.'
            )
            return self.form_invalid(form)
        
        # Check available balance
        available_balance = financier.investment_amount  # This should be calculated based on actual earnings
        
        if form.instance.amount > available_balance:
            messages.error(
                self.request, 
                f'Insufficient balance. Available: ₹{available_balance:.2f}'
            )
            return self.form_invalid(form)
        
        form.instance.financier = financier
        response = super().form_valid(form)
        
        # Send withdrawal request notification
        try:
            send_withdrawal_request_notification(form.instance)
        except Exception as e:
            print(f"Error sending withdrawal request notification: {e}")
        
        messages.success(
            self.request, 
            f'Withdrawal request of ₹{form.instance.amount} submitted successfully!'
        )
        
        return response
    
    def get_context_data(self, **kwargs):
        """Add financier information to context"""
        context = super().get_context_data(**kwargs)
        try:
            financier = self.request.user.financier_profile
            context['available_balance'] = financier.investment_amount
        except FinancierUser.DoesNotExist:
            context['available_balance'] = 0
        return context


class WithdrawalListView(LoginRequiredMixin, ListView):
    """View for listing withdrawals"""
    model = Withdrawal
    template_name = 'repayments/withdrawal_list.html'
    context_object_name = 'withdrawals'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter withdrawals based on user role"""
        if self.request.user.is_staff:
            # Admin sees all withdrawals
            return Withdrawal.objects.all().select_related('financier__user').order_by('-created_at')
        else:
            # Financiers see only their own withdrawals
            try:
                financier = self.request.user.financier_profile
                return Withdrawal.objects.filter(
                    financier=financier
                ).select_related('financier__user').order_by('-created_at')
            except FinancierUser.DoesNotExist:
                return Withdrawal.objects.none()


class WithdrawalDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View for displaying withdrawal details"""
    model = Withdrawal
    template_name = 'repayments/withdrawal_detail.html'
    context_object_name = 'withdrawal'
    
    def test_func(self):
        """Check if user can view this withdrawal"""
        withdrawal = self.get_object()
        return (self.request.user == withdrawal.financier.user or 
                self.request.user.is_staff)


@staff_member_required
def admin_withdrawal_management(request):
    """Admin view for managing withdrawals"""
    withdrawals = Withdrawal.objects.all().select_related('financier__user').order_by('-created_at')
    
    # Statistics
    total_withdrawals = withdrawals.count()
    pending_withdrawals = withdrawals.filter(status='Pending').count()
    processing_withdrawals = withdrawals.filter(status='Processing').count()
    completed_withdrawals = withdrawals.filter(status='Completed').count()
    failed_withdrawals = withdrawals.filter(status='Failed').count()
    
    total_amount_requested = withdrawals.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Search and filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    
    if search_query:
        withdrawals = withdrawals.filter(
            Q(financier__user__first_name__icontains=search_query) |
            Q(financier__user__last_name__icontains=search_query) |
            Q(financier__financier_id__icontains=search_query) |
            Q(transaction_id__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    if status_filter:
        withdrawals = withdrawals.filter(status=status_filter)
    
    if method_filter:
        withdrawals = withdrawals.filter(withdrawal_method=method_filter)
    
    # Pagination
    paginator = Paginator(withdrawals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'withdrawals': page_obj,
        'total_withdrawals': total_withdrawals,
        'pending_withdrawals': pending_withdrawals,
        'processing_withdrawals': processing_withdrawals,
        'completed_withdrawals': completed_withdrawals,
        'failed_withdrawals': failed_withdrawals,
        'total_amount_requested': total_amount_requested,
        'search_query': search_query,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'status_choices': Withdrawal.STATUS_CHOICES,
        'method_choices': Withdrawal.WITHDRAWAL_METHOD_CHOICES,
    }
    
    return render(request, 'repayments/admin_withdrawal_management.html', context)


@staff_member_required
@require_http_methods(["POST"])
def approve_withdrawal(request, withdrawal_id):
    """API endpoint to approve a withdrawal"""
    try:
        withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)
        withdrawal.status = 'Processing'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        # Send withdrawal processed notification
        try:
            send_withdrawal_processed_notification(withdrawal)
        except Exception as e:
            print(f"Error sending withdrawal processed notification: {e}")
        
        return JsonResponse({
            'success': True, 
            'message': f'Withdrawal #{withdrawal.id} approved and set to processing'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })


@staff_member_required
@require_http_methods(["POST"])
def complete_withdrawal(request, withdrawal_id):
    """API endpoint to mark a withdrawal as completed"""
    try:
        withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)
        withdrawal.status = 'Completed'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Withdrawal #{withdrawal.id} marked as completed'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })


@staff_member_required
@require_http_methods(["POST"])
def reject_withdrawal(request, withdrawal_id):
    """API endpoint to reject a withdrawal"""
    try:
        withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)
        withdrawal.status = 'Failed'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Withdrawal #{withdrawal.id} rejected'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })


# Payment Gateway Views

@login_required
def initiate_payment(request, repayment_id):
    """Initiate payment through gateway"""
    try:
        repayment = get_object_or_404(Repayment, id=repayment_id, loan__student=request.user)
        
        if repayment.status not in ['Pending', 'Failed']:
            return JsonResponse({
                'success': False,
                'error': 'Payment already processed or in progress'
            })
        
        gateway = request.POST.get('gateway', 'razorpay')
        
        # Process payment through gateway
        result = process_payment(
            repayment,
            gateway_name=gateway,
            currency='INR',
            receipt=f"loan_repayment_{repayment.id}"
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'payment_data': result['payment_data'],
                'gateway': result['gateway']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def payment_success(request):
    """Handle successful payment callback"""
    try:
        # Get payment parameters from callback
        payment_id = request.GET.get('razorpay_payment_id') or request.POST.get('razorpay_payment_id')
        order_id = request.GET.get('razorpay_order_id') or request.POST.get('razorpay_order_id')
        signature = request.GET.get('razorpay_signature') or request.POST.get('razorpay_signature')
        
        if not all([payment_id, order_id, signature]):
            messages.error(request, 'Invalid payment callback parameters')
            return redirect('repayments:list')
        
        # Find repayment by gateway transaction ID
        repayment = Repayment.objects.filter(
            gateway_transaction_id=order_id,
            loan__student=request.user
        ).first()
        
        if not repayment:
            messages.error(request, 'Payment record not found')
            return redirect('repayments:list')
        
        # Verify payment
        result = verify_payment(
            repayment,
            gateway_name='razorpay',
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            razorpay_signature=signature
        )
        
        if result['success'] and result['verified']:
            messages.success(
                request, 
                f'Payment of ₹{repayment.amount_paid} processed successfully!'
            )
        else:
            messages.error(request, 'Payment verification failed')
        
        return redirect('repayments:list')
        
    except Exception as e:
        messages.error(request, f'Payment processing error: {str(e)}')
        return redirect('repayments:list')


@login_required
def payment_failure(request):
    """Handle failed payment callback"""
    try:
        # Get error information
        error_code = request.GET.get('error_code', 'Unknown')
        error_description = request.GET.get('error_description', 'Payment failed')
        
        messages.error(
            request, 
            f'Payment failed: {error_description} (Code: {error_code})'
        )
        
        return redirect('repayments:list')
        
    except Exception as e:
        messages.error(request, f'Error handling payment failure: {str(e)}')
        return redirect('repayments:list')


@login_required
def payment_callback(request):
    """Handle payment gateway callback"""
    try:
        # This is a generic callback handler
        # Different gateways may send different parameters
        
        if request.method == 'POST':
            # Handle POST callback (PayU, Paytm)
            callback_data = request.POST.dict()
        else:
            # Handle GET callback (Razorpay)
            callback_data = request.GET.dict()
        
        # Log callback data for debugging
        print(f"Payment callback received: {callback_data}")
        
        # Process based on gateway
        gateway = callback_data.get('gateway', 'unknown')
        
        if gateway == 'razorpay':
            return payment_success(request)
        else:
            # Handle other gateways
            messages.info(request, 'Payment callback received and processed')
            return redirect('repayments:list')
            
    except Exception as e:
        messages.error(request, f'Callback processing error: {str(e)}')
        return redirect('repayments:list')
