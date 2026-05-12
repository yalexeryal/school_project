from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from .models import School, SchoolClass, Student, CustomUser


# --- ВЬЮХИ ДЛЯ ПРОСМОТРА СПИСКОВ (ДОСТУПНЫ ВСЕМ) ---

class SchoolListView(ListView):
    model = School
    template_name = 'school/school_list.html'


class SchoolClassListView(ListView):
    model = SchoolClass
    template_name = 'school/class_list.html'


class StudentListView(ListView):
    model = Student
    template_name = 'school/student_list.html'


# --- ВЬЮХА ДЛЯ ЛИЧНОГО КАБИНЕТА (ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ) ---

@login_required
def profile_edit(request):
    """
    Позволяет пользователю редактировать свои данные (email, имя и т.д.)
    """
    user = request.user  # Это текущий залогиненный пользователь

    if request.method == 'POST':
        # Обработка формы (здесь для простоты просто сохраняем)
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        return redirect('profile_edit')

    return render(request, 'school/profile_edit.html', {'user': user})


@login_required
def student_edit_own(request, pk):
    """
    Позволяет пользователю редактировать СВОЮ запись в модели Student,
    если такая запись существует и связана с ним.
    """
    student = get_object_or_404(Student, pk=pk)

    # Проверка: принадлежит ли этот ученик текущему пользователю?
    if hasattr(student, 'user') and student.user == request.user:
        if request.method == 'POST':
            student.first_name = request.POST.get('first_name')
            student.last_name = request.POST.get('last_name')
            student.description = request.POST.get('description')
            student.save()
            return redirect('student_list')
        return render(request, 'school/student_form.html', {'student': student})

    # Если это не его ученик - возвращаем ошибку 403 (Доступ запрещен)
    return render(request, '403.html', status=403)