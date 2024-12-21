from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Уникальный email для всех пользователей
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Дополнительное поле
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.username

class Task(models.Model):
    """
    Модель задачи.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def complete_task_and_subtasks(self):
        """Отмечает задачу и все её подзадачи как выполненные"""
        self.completed = True
        self.save()
        for subtask in self.subtasks.all():
            subtask.completed = True
            subtask.save()
