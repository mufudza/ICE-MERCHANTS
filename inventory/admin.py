from django.contrib import admin
from .models import Production, Sale, Expense, Profile

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('date', 'quantity', 'cost_per_unit', 'total_cost', 'created_by')
    list_filter = ('date', 'created_by')
    search_fields = ('date',)
    date_hierarchy = 'date'

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('date', 'quantity', 'price_per_unit', 'total_revenue', 'customer', 'created_by')
    list_filter = ('date', 'created_by')
    search_fields = ('date', 'customer')
    date_hierarchy = 'date'

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'expense_type', 'amount', 'created_by')
    list_filter = ('date', 'expense_type', 'created_by')
    search_fields = ('date', 'description')
    date_hierarchy = 'date'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic', 'deactivation_reason')