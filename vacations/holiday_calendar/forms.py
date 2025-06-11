from django import forms
from .models import Holiday


class HolidayForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        label='Дата'
    )

    is_workday = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Специальный рабочий день'
    )

    class Meta:
        model = Holiday
        fields = ['date', 'is_workday']