from django.urls import path
from . import views

urlpatterns = [
    path('', views.SchoolListView.as_view(), name='home'),
    path('classes/', views.SchoolClassListView.as_view(), name='class_list'),
    path('students/', views.StudentListView.as_view(), name='student_list'),

    # URL для личного кабинета (редактирование своего профиля)
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # URL для редактирования своей записи ученика (если пользователь == ученик)
    path('student/<int:pk>/edit-own/', views.student_edit_own, name='student_edit_own'),
]