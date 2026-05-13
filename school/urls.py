# school/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    # --- НОВЫЕ ПУТИ ---
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    # ------------------

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('logout/', views.logout_view, name='logout'),
    path('classes/', views.SchoolClassListView.as_view(), name='class_list'),

    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),

    path('students/<int:pk>/edit-own/', views.student_edit_own, name='student_edit_own'),
]