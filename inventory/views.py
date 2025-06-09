from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseForbidden

from .models import Production, Sale, Expense, Profile
from .forms import ProductionForm, SaleForm, ExpenseForm
from django.contrib.auth.models import User
from django import forms
from django.conf import settings
import os
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
import secrets

# Profile form for updating user info and profile picture
class ProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

@login_required
def dashboard(request):
    # Get stats for the last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)

    # Production stats
    total_production = Production.objects.aggregate(
        total_quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
        total_cost=Coalesce(Sum('total_cost', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    recent_production = Production.objects.filter(date__gte=thirty_days_ago).aggregate(
        recent_quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
        recent_cost=Coalesce(Sum('total_cost', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    # Sales stats
    total_sales = Sale.objects.aggregate(
        total_quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
        total_revenue=Coalesce(Sum('total_revenue', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    recent_sales = Sale.objects.filter(date__gte=thirty_days_ago).aggregate(
        recent_quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
        recent_revenue=Coalesce(Sum('total_revenue', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    # Expense stats
    total_expenses = Expense.objects.aggregate(
        total_amount=Coalesce(Sum('amount', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    recent_expenses = Expense.objects.filter(date__gte=thirty_days_ago).aggregate(
        recent_amount=Coalesce(Sum('amount', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    # Calculate current stock
    current_stock = total_production['total_quantity'] - total_sales['total_quantity']

    # Calculate profit
    total_profit = total_sales['total_revenue'] - total_expenses['total_amount']
    recent_profit = recent_sales['recent_revenue'] - recent_expenses['recent_amount']

    # Get recent activities for dashboard
    recent_productions = Production.objects.order_by('-date')[:5]
    recent_sales_list = Sale.objects.order_by('-date')[:5]
    recent_expenses_list = Expense.objects.order_by('-date')[:5]

    # Expense breakdown by type
    expense_by_type = Expense.objects.values('expense_type').annotate(
        total=Sum('amount', output_field=DecimalField())
    ).order_by('-total')

    # Monthly data for charts
    months = 6
    monthly_data = []

    for i in range(months, 0, -1):
        start_date = timezone.now().date().replace(day=1) - timedelta(days=30 * (i - 1))
        if i > 1:
            end_date = timezone.now().date().replace(day=1) - timedelta(days=30 * (i - 2) - 1)
        else:
            end_date = timezone.now().date()

        month_sales = Sale.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(
            total=Coalesce(Sum('total_revenue', output_field=DecimalField()), 0, output_field=DecimalField())
        )['total']

        month_expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), 0, output_field=DecimalField())
        )['total']

        month_profit = month_sales - month_expenses

        monthly_data.append({
            'month': start_date.strftime('%b %Y'),
            'sales': float(month_sales),
            'expenses': float(month_expenses),
            'profit': float(month_profit)
        })

    context = {
        'total_production': total_production,
        'recent_production': recent_production,
        'total_sales': total_sales,
        'recent_sales': recent_sales,
        'total_expenses': total_expenses,
        'recent_expenses': recent_expenses,
        'current_stock': current_stock,
        'total_profit': total_profit,
        'recent_profit': recent_profit,
        'recent_productions': recent_productions,
        'recent_sales_list': recent_sales_list,
        'recent_expenses_list': recent_expenses_list,
        'expense_by_type': expense_by_type,
        'monthly_data': monthly_data,
    }

    return render(request, 'inventory/dashboard.html', context)


# Production Views
@login_required
def production_list(request):
    productions = Production.objects.all()
    return render(request, 'inventory/production_list.html', {'productions': productions})


@login_required
def add_production(request):
    if request.method == 'POST':
        form = ProductionForm(request.POST)
        if form.is_valid():
            production = form.save(commit=False)
            production.created_by = request.user
            production.save()
            messages.success(request, "Production record added successfully!")
            return redirect('production_list')
    else:
        form = ProductionForm()

    return render(request, 'inventory/production_form.html', {'form': form, 'title': 'Add Production'})


@login_required
def edit_production(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit records.")
    production = get_object_or_404(Production, pk=pk)
    if request.method == 'POST':
        form = ProductionForm(request.POST, instance=production)
        if form.is_valid():
            form.save()
            messages.success(request, "Production record updated successfully!")
            return redirect('production_list')
    else:
        form = ProductionForm(instance=production)

    return render(request, 'inventory/production_form.html', {'form': form, 'title': 'Edit Production'})


@login_required
def delete_production(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete records.")
    production = get_object_or_404(Production, pk=pk)
    if request.method == 'POST':
        production.delete()
        messages.success(request, "Production record deleted successfully!")
        return redirect('production_list')
    return render(request, 'inventory/confirm_delete.html', {'object': production, 'type': 'Production'})

# Sales Views
@login_required
def sale_list(request):
    sales = Sale.objects.all()
    return render(request, 'inventory/sale_list.html', {'sales': sales})


@login_required
def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.created_by = request.user
            sale.save()
            messages.success(request, "Sale recorded successfully!")
            return redirect('sale_list')
    else:
        form = SaleForm()

    return render(request, 'inventory/sale_form.html', {'form': form, 'title': 'Record Sale'})


@login_required
def edit_sale(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit records.")
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, "Sale record updated successfully!")
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)

    return render(request, 'inventory/sale_form.html', {'form': form, 'title': 'Edit Sale'})


@login_required
def delete_sale(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete records.")
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, "Sale record deleted successfully!")
        return redirect('sale_list')
    return render(request, 'inventory/confirm_delete.html', {'object': sale, 'type': 'Sale'})

# Expense Views
@login_required
def expense_list(request):
    expenses = Expense.objects.all()

    # Calculate total expenses
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Get expenses by type for chart
    expense_by_type = list(Expense.objects.values('expense_type').annotate(
        total=Sum('amount')
    ).order_by('-total'))

    context = {
        'expenses': expenses,
        'total': total,
        'expense_by_type': expense_by_type
    }

    return render(request, 'inventory/expense_list.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'inventory/expense_form.html', {'form': form, 'title': 'Add Expense'})


@login_required
def edit_expense(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit records.")
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'inventory/expense_form.html', {'form': form, 'title': 'Edit Expense'})


@login_required
def delete_expense(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete records.")
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense record deleted successfully!")
        return redirect('expense_list')
    return render(request, 'inventory/confirm_delete.html', {'object': expense, 'type': 'Expense'})

@login_required
def reports(request):
    # Summary stats
    total_production = Production.objects.aggregate(
        total_quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
        total_cost=Coalesce(Sum('total_cost', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    total_sales = Sale.objects.aggregate(
        total_quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
        total_revenue=Coalesce(Sum('total_revenue', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    total_expenses = Expense.objects.aggregate(
        total_amount=Coalesce(Sum('amount', output_field=DecimalField()), 0, output_field=DecimalField())
    )

    # Calculate current stock and profit
    current_stock = total_production['total_quantity'] - total_sales['total_quantity']
    total_profit = total_sales['total_revenue'] - total_expenses['total_amount']

    # Monthly data for charts (last 12 months)
    months = 12
    monthly_data = []

    for i in range(months, 0, -1):
        start_date = timezone.now().date().replace(day=1) - timedelta(days=30 * (i - 1))
        if i > 1:
            end_date = timezone.now().date().replace(day=1) - timedelta(days=30 * (i - 2) - 1)
        else:
            end_date = timezone.now().date()

        month_production = Production.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(
            quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
            cost=Coalesce(Sum('total_cost', output_field=DecimalField()), 0, output_field=DecimalField())
        )

        month_sales = Sale.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(
            quantity=Coalesce(Sum('quantity', output_field=DecimalField()), 0, output_field=DecimalField()),
            revenue=Coalesce(Sum('total_revenue', output_field=DecimalField()), 0, output_field=DecimalField())
        )

        month_expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(
            amount=Coalesce(Sum('amount', output_field=DecimalField()), 0, output_field=DecimalField())
        )

        month_profit = month_sales['revenue'] - month_expenses['amount']

        monthly_data.append({
            'month': start_date.strftime('%b %Y'),
            'production': float(month_production['quantity']),
            'sales_quantity': float(month_sales['quantity']),
            'revenue': float(month_sales['revenue']),
            'expenses': float(month_expenses['amount']),
            'profit': float(month_profit)
        })

    # Expense breakdown by type
    expense_by_type = list(Expense.objects.values('expense_type').annotate(
        total=Sum('amount', output_field=DecimalField())
    ).order_by('-total'))

    context = {
        'total_production': total_production,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'current_stock': current_stock,
        'total_profit': total_profit,
        'monthly_data': monthly_data,
        'expense_by_type': expense_by_type,
    }

    return render(request, 'inventory/reports.html', context)

@login_required
def profile(request):
    user = request.user
    # Ensure user has a profile
    profile, created = Profile.objects.get_or_create(user=user)
    profile_pic_url = profile.profile_pic.url if profile.profile_pic else None

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            # Save profile picture if provided
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
                profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'inventory/profile.html', {'form': form, 'profile_pic_url': profile_pic_url})

# Settings form for changing password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def settings_view(request):
    password_changed = False
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            password_changed = True
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'inventory/settings.html', {'form': form, 'password_changed': password_changed})

@login_required
def add_employee(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can add employees.")
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = False
            user.save()
            messages.success(request, f"Employee account for {user.username} created.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'inventory/add_employee.html', {'form': form})

@login_required
def employee_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can view employees.")
    employees = User.objects.filter(is_superuser=False).order_by('-is_active', 'username')
    # Optionally, get recent activity (last login, date joined, etc.)
    return render(request, 'inventory/employee_list.html', {'employees': employees})

@login_required
def deactivate_employee(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can deactivate employees.")
    employee = get_object_or_404(User, pk=user_id, is_superuser=False)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        employee.is_active = False
        employee.profile.deactivation_reason = reason
        employee.profile.save()
        employee.save()
        messages.success(request, f"{employee.username} has been deactivated.")
        return redirect('employee_list')
    return render(request, 'inventory/deactivate_employee.html', {'employee': employee})

@login_required
def reactivate_employee(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can reactivate employees.")
    employee = get_object_or_404(User, pk=user_id, is_superuser=False)
    if request.method == 'POST':
        employee.is_active = True
        employee.profile.deactivation_reason = ''
        employee.profile.save()
        employee.save()
        messages.success(request, f"{employee.username} has been reactivated.")
        return redirect('employee_list')
    return render(request, 'inventory/confirm_reactivate.html', {'employee': employee})