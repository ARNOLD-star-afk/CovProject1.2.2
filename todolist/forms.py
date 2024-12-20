from django import forms
from django.forms import DateTimeInput

from .models import CustomUser, Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'deadline', 'parent']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.fields['parent'].queryset = Task.objects.filter(user=user)

        # Используем стандартный DateTimeInput, который включает как дату, так и время
        self.fields['deadline'].widget = DateTimeInput(attrs={'type': 'datetime-local'})



class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'date_of_birth', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


