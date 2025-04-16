from django import forms
from .models import Vacation

class VacationForm(forms.ModelForm):
    class Meta:
        model = Vacation
        exclude = ['user', 'year', 'can_redact']
        widgets = {
            'id': forms.Textarea(attrs={"cols": 40, "rows": 1}),
            'day_start': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'id': 'id_day_start', 'placeholder': 'Выберите дату'}
            ),
            'day_end': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'id': 'id_day_end', 'placeholder': 'Выберите дату'}
            ),
            'how_long': forms.NumberInput(
                attrs={ 
                    'id': 'id_how_long', 
                    'placeholder': 'календарных дней', 
                    'min': '1', 
                    'step': '1', 
                    'class': 'form-control'
                }
            ),
        }
        labels = {
            'day_start': 'Начало отпуска',
            'day_end': 'Окончание отпуска',
            'how_long': 'Кол-во дней',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем одинаковые классы и атрибуты в поля формы
        date_field_style = {'class': 'form-control'}
        self.fields['day_start'].widget.attrs.update(date_field_style)
        self.fields['how_long'].widget.attrs.update(date_field_style)
        self.fields['day_end'].widget.attrs.update(date_field_style)

        # Перестановка полей
        self.order_fields(['day_start', 'how_long', 'day_end'])
