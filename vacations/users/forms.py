from django import forms
from .models import Vacation

class VacationForm(forms.ModelForm):
    class Meta:
        model = Vacation
        exclude = ['user', 'year']
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

        self.fields['day_end'].required = True
        self.fields['day_end'].widget.attrs.update({'required': 'required'})

        # Перестановка полей
        self.order_fields(['day_start', 'how_long', 'day_end'])

    def clean(self):
        cleaned = super().clean()
        day_start = cleaned.get('day_start')
        day_end   = cleaned.get('day_end')

        if not day_end:
            self.add_error('day_end', 'Укажите дату окончания отпуска.')
            return cleaned

        if day_start and day_end and day_end.year != day_start.year:
            self.add_error(
                'day_end',
                'Отпуск не может переходить на следующий календарный год.'
            )

        return cleaned
