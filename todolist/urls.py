from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('complete/<int:pk>/', views.complete_task, name='complete_task'),
    path('uncomplete/<int:pk>/', views.uncomplete_task, name='uncomplete_task'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('complete_subtask/<int:pk>/', views.complete_subtask, name='complete_subtask'),
    path('uncomplete_subtask/<int:pk>/', views.uncomplete_subtask, name='uncomplete_subtask'),
    path('task/<int:parent_task_id>/add_subtask/', views.add_subtask, name='add_subtask'),
    path('add_task/', views.add_task, name='add_task'),
    path('', views.task_list_view, name='task_list'),  # Список задач
]
