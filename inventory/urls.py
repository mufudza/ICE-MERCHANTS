from django.urls import path

from . import views


urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Production
    path('production/', views.production_list, name='production_list'),
    path('production/add/', views.add_production, name='add_production'),
    path('production/edit/<int:pk>/', views.edit_production, name='edit_production'),
    path('production/delete/<int:pk>/', views.delete_production, name='delete_production'),
    
    # Sales
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/add/', views.add_sale, name='add_sale'),
    path('sales/edit/<int:pk>/', views.edit_sale, name='edit_sale'),
    path('sale/delete/<int:pk>/', views.delete_sale, name='delete_sale'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Profile and Settings
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # Employees
    path('add-employee/', views.add_employee, name='add_employee'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employee/deactivate/<int:user_id>/', views.deactivate_employee, name='deactivate_employee'),
    path('employee/reactivate/<int:user_id>/', views.reactivate_employee, name='reactivate_employee'),
]