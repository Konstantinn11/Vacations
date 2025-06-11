from django import forms
from .models import Vacation, Tag, Unit, CustomUser, User_info

class VacationForm(forms.ModelForm):
    how_long = forms.IntegerField(
        required=False,
        label='Кол-во дней',
        min_value=1,
        error_messages={'min_value': 'Количество дней должно быть не меньше 1.'},
        widget=forms.NumberInput(attrs={
            'id': 'id_how_long',
            'placeholder': 'календарных дней',
            'min': '1',
            'step': '1',
            'class': 'form-control'
        })
    )
    
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
        }
        labels = {
            'day_start': 'Начало отпуска',
            'day_end': 'Окончание отпуска',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем одинаковые классы и атрибуты в поля формы
        date_field_style = {'class': 'form-control'}
        self.fields['day_start'].widget.attrs.update(date_field_style)
        self.fields['how_long'].widget.attrs.update(date_field_style)
        self.fields['day_end'].widget.attrs.update(date_field_style)

        self.fields['day_start'].required = True
        self.fields['day_start'].widget.attrs.update({'required': 'required'})
        self.fields['day_end'].required = True
        self.fields['day_end'].widget.attrs.update({'required': 'required'})

        # Перестановка полей
        self.order_fields(['day_start', 'how_long', 'day_end'])

    def clean(self):
        cleaned = super().clean()
        day_start = cleaned.get('day_start')
        day_end   = cleaned.get('day_end')

        if not day_start:
            self.add_error('day_start', 'Укажите дату начала отпуска.')

        if not day_end:
            self.add_error('day_end', 'Укажите дату окончания отпуска.')
            return cleaned

        if day_start and day_end and day_end.year != day_start.year:
            self.add_error(
                'day_end',
                'Отпуск не может переходить на следующий календарный год.'
            )

        return cleaned
    

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, "Ключевой сотрудник"',
            }),
        }
        labels = {
            'name': 'Название',
        }


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, user):
        full_name = user.get_full_name()
        user_info = getattr(user, 'user_info', None)
        position = ''
        if user_info is not None:
            ui = user_info.first() if hasattr(user_info, 'first') else user_info
            if ui and ui.position:
                position = ui.position.position
        return f"{full_name}" + (f", {position}" if position else "")


class UnitForm(forms.ModelForm):
    boss = UserModelChoiceField(
        queryset=CustomUser.objects.filter(
            user_info__in=User_info.active.all()
        ).distinct(),
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        label='Руководитель отдела',
        required=False,
        empty_label=''
    )
    
    class Meta:
        model = Unit
        fields = ['title', 'boss']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, "Производственный отдел (307)"',
            }),
        }
        labels = {
            'title': 'Название',
        }