from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('', views.dashboard, name='dashboard'),
    path('register/', views.StudentRegistrationView.as_view(), name='register'),
    path('login/', views.StudentLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(http_method_names=['get', 'post']), name='logout'),
    
    # Profile URLs
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    path('profile/update/', views.StudentProfileUpdateView.as_view(), name='profile_update'),
    
    # Dashboard and History URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('loan-history/', views.loan_history, name='loan_history'),
    path('repayment-history/', views.repayment_history, name='repayment_history'),
    
    # API URLs for AJAX requests
    path('api/loan-status/<int:loan_id>/', views.get_loan_status, name='loan_status_api'),
    path('api/repayment-summary/', views.get_repayment_summary, name='repayment_summary_api'),
]
