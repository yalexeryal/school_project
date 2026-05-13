# school/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

# Получаем нашу модель пользователя
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.
    """
    email = forms.EmailField(required=False) # Делаем как в твоем шаблоне
    username = forms.CharField(required=False) # Делаем как в твоем шаблоне

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем стили и плейсхолдеры для красоты
        self.fields['username'].widget.attrs.update({'placeholder': 'Имя пользователя'})
        self.fields['email'].widget.attrs.update({'placeholder': 'E-mail'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повтор пароля'})


class CustomLoginForm(AuthenticationForm):
    """
    Форма для входа пользователя.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Имя пользователя или E-mail'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Пароль'})