from django.views.generic import ListView, DetailView

from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib import messages

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .models import Student, School, SchoolClass
# from .forms import StudentForm  # Если у тебя есть форма для ученика
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout as auth_logout




def index(request):
    """
    Главная страница сайта.
    """
    return render(request, 'school/index.html')

# Импортируем стандартные формы Django для пользователя

# --- ВЬЮХИ ДЛЯ ПРОСМОТРА (ДОСТУПНЫ ВСЕМ) ---

class SchoolListView(ListView):
    model = School
    template_name = 'school/school_list.html'


class SchoolClassListView(ListView):
    model = SchoolClass
    template_name = 'school/class_list.html'


class StudentListView(ListView):
    model = Student
    template_name = 'school/student_list.html'
    context_object_name = 'student_list'


class StudentDetailView(DetailView):
    model = Student
    template_name = 'school/student_detail.html'
    context_object_name = 'student'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('classes_history')


# --- ВЬЮХИ ДЛЯ АВТОРИЗАЦИИ (ТВОИ НОВЫЕ КЛАССЫ) ---

# 1. Форма для регистрации (CreateView)
class SignUpView(CreateView):
    # Используем стандартную форму создания пользователя
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'school/signup.html'


# 2. Форма для входа (LoginView)
class CustomLoginView(auth_views.LoginView):
    # Используем стандартную форму аутентификации
    authentication_form = AuthenticationForm
    template_name = 'school/login.html'
    # Перенаправление настроено в settings.py через LOGIN_REDIRECT_URL


# --- ВЬЮХИ ДЛЯ ЛИЧНОГО КАБИНЕТА (ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ) ---

@login_required
def profile(request):
    """
    Личный кабинет пользователя.
    """
    return render(request, 'school/profile.html')


@login_required
def profile_edit(request):
    """
    Позволяет пользователю редактировать свои данные (email, имя и т.д.)
    """
    user = request.user

    # Эта часть кода выполнится ТОЛЬКО при нажатии кнопки "Сохранить"
    if request.method == 'POST':
        # Берем данные из формы и сохраняем их в модель пользователя
        user.email = request.POST.get('email', user.email)  # Если поле пустое, оставляем старое значение
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)

        user.save()  # Сохраняем изменения в базу данных

        # Перенаправляем пользователя на ту же страницу, чтобы он увидел результат
        messages.success(request, 'Данные успешно сохранены')
        return redirect('profile_edit')

        # Эта часть кода выполнится при обычном открытии страницы
    return render(request, 'school/profile_edit.html', {'user': user})


@login_required
def student_edit_own(request, pk):
    """
    Позволяет пользователю редактировать СВОЮ запись в модели Student.
    """
    student = get_object_or_404(Student, pk=pk)

    if hasattr(student, 'user') and student.user == request.user:
        if request.method == 'POST':
            student.first_name = request.POST.get('first_name')
            student.last_name = request.POST.get('last_name')
            student.description = request.POST.get('description')
            student.save()
            return redirect('student_detail', pk=student.pk)
        return render(request, 'school/student_form.html', {'student': student})

    return render(request, '403.html', status=403)

# Простая функция для выхода из системы
def logout_view(request):
    auth_logout(request) # Выполняем выход
    return redirect('home')