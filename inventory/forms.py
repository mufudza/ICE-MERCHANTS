from django import forms
from .models import Production, Sale, Expense
from django.core.exceptions import ValidationError
from django.utils import timezone

class DateInput(forms.DateInput):
    input_type = 'date'

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ['date', 'quantity', 'cost_per_unit']
        widgets = {
            'date': DateInput(),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError("Date cannot be in the future")
        return date

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")
        return quantity

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['date', 'quantity', 'price_per_unit', 'customer', 'notes']
        widgets = {
            'date': DateInput(),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError("Date cannot be in the future")
        return date

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")
        
        # Get total produced and sold to check if we have enough stock
        from django.db.models import Sum
        total_produced = Production.objects.aggregate(total=Sum('quantity'))['total'] or 0
        total_sold = Sale.objects.aggregate(total=Sum('quantity'))['total'] or 0
        
        # If this is an update, exclude the current sale
        if self.instance.pk:
            total_sold -= self.instance.quantity
            
        available_stock = total_produced - total_sold
        
        if quantity > available_stock:
            raise ValidationError(f"Not enough stock. Only {available_stock} units available.")
            
        return quantity

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'description', 'amount', 'expense_type', 'notes', 'receipt']
        widgets = {
            'date': DateInput(),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError("Date cannot be in the future")
        return date

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        return amount