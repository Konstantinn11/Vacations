from django import forms
from .models import Holiday

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['date', 'is_workday']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_workday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'date': 'Дата',
            'is_workday': 'Специальный рабочий день',
        }