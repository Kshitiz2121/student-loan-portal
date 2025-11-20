from django.urls import path
from . import views

app_name = 'repayments'

urlpatterns = [
    # Repayment management URLs
    path('create/<int:loan_id>/', views.record_repayment, name='create'),
    path('create/class/<int:loan_id>/', views.RepaymentCreateView.as_view(), name='create_class'),
    path('list/', views.RepaymentListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.RepaymentDetailView.as_view(), name='detail'),
    
    # Admin management URLs
    path('admin/', views.admin_repayment_management, name='admin_management'),
    path('statistics/', views.repayment_statistics, name='statistics'),
    
    # API endpoints for repayment management
    path('api/mark-paid/<int:repayment_id>/', views.mark_repayment_paid, name='mark_paid_api'),
    path('api/mark-failed/<int:repayment_id>/', views.mark_repayment_failed, name='mark_failed_api'),
    path('api/summary/', views.repayment_summary, name='summary_api'),
    
    # Withdrawal management URLs
    path('withdrawals/create/', views.WithdrawalCreateView.as_view(), name='withdrawal_create'),
    path('withdrawals/list/', views.WithdrawalListView.as_view(), name='withdrawal_list'),
    path('withdrawals/detail/<int:pk>/', views.WithdrawalDetailView.as_view(), name='withdrawal_detail'),
    
    # Admin withdrawal management URLs
    path('withdrawals/admin/', views.admin_withdrawal_management, name='admin_withdrawal_management'),
    
    # API endpoints for withdrawal management
    path('api/withdrawals/approve/<int:withdrawal_id>/', views.approve_withdrawal, name='approve_withdrawal_api'),
    path('api/withdrawals/complete/<int:withdrawal_id>/', views.complete_withdrawal, name='complete_withdrawal_api'),
    path('api/withdrawals/reject/<int:withdrawal_id>/', views.reject_withdrawal, name='reject_withdrawal_api'),
    
    # Payment Gateway URLs
    path('payment/initiate/<int:repayment_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
]
