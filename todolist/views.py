from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponse
from django.core.mail import EmailMessage
from .models import Task
from .tokens import account_activation_token
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, TaskForm


@login_required
def task_list_view(request):
    tasks = Task.objects.filter(user=request.user).order_by('deadline')

    # Добавляем дополнительную логику для работы с подзадачами
    for task in tasks:
        task.subtasks_list = task.subtasks.all()  # Получаем все подзадачи
        task.has_subtasks = task.subtasks.exists()  # Проверяем, есть ли подзадачи у задачи
        task.are_all_subtasks_completed = all(
            subtask.completed for subtask in task.subtasks.all())  # Проверяем, выполнены ли все подзадачи

    return render(request, 'task_list.html', {'tasks': tasks})



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # После успешной регистрации перенаправляем на страницу входа
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated successfully!')
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid!')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Используем get, чтобы избежать ошибки KeyError
        password = request.POST.get('password')  # То же для пароля

        # Если отсутствует username или password, возвращаем ошибку
        if not username or not password:
            messages.error(request, 'Пожалуйста, введите имя пользователя и пароль.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Перенаправляем на следующую страницу или на страницу задач после успешного входа
            next_page = request.POST.get('next', 'task_list')
            return redirect(next_page)
        else:
            messages.error(request, 'Неверные данные для входа')
    return render(request, 'login.html')


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)  # Получаем задачи текущего пользователя
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # Привязываем задачу к текущему пользователю
            task.save()
            print("Задача сохранена:", task)  # Отладочное сообщение
            return redirect('task_list')
        else:
            print("Ошибка в форме:", form.errors)  # Показываем ошибки формы в консоли

    return render(request, 'task_list.html', {'tasks': tasks, 'form': form})


@login_required
def edit_task(request, pk):
    # Получаем задачу для текущего пользователя
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)  # Привязываем форму к задаче
        if form.is_valid():
            form.save()  # Сохраняем изменения в задаче
            return redirect('task_list')  # Перенаправляем на список задач после сохранения
    else:
        form = TaskForm(instance=task)  # Если это GET-запрос, передаем текущую задачу в форму

    return render(request, 'edit_task.html', {'form': form})

@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = True
    task.save()

    # Если задача завершена, помечаем все её подзадачи как выполненные
    subtasks = Task.objects.filter(parent=task)
    for subtask in subtasks:
        subtask.completed = True
        subtask.save()

    return redirect('task_list')

@login_required
def uncomplete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = False
    task.save()

    # Если задача отменена, отменяем выполнение всех её подзадач
    subtasks = Task.objects.filter(parent=task)
    for subtask in subtasks:
        subtask.completed = False
        subtask.save()

    return redirect('task_list')




@login_required
def complete_subtask(request, pk):
    subtask = get_object_or_404(Task, pk=pk, user=request.user)
    subtask.completed = True
    subtask.save()
    return redirect('task_list')

@login_required
def uncomplete_subtask(request, pk):
    subtask = get_object_or_404(Task, pk=pk, user=request.user)
    subtask.completed = False  # Меняем статус на невыполненную
    subtask.save()
    return redirect('task_list')


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    return redirect('task_list')

@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('task_list')


