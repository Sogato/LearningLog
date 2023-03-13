from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def index(request):
    """Домашняя страница приложения Learning Log"""
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """Выводит список тем."""
    topics_all = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics_all}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """Выводит одну тему и все ее записи."""
    topic_object = get_object_or_404(Topic, id=topic_id)
    # Проверка того, что тема принадлежит текущему пользователю.
    if topic_object.owner != request.user:
        raise Http404

    entries = topic_object.entry_set.order_by('-date_added')
    context = {'topics': topic_object, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Определяет новую тему."""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = TopicForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic_object = form.save(commit=False)
            new_topic_object.owner = request.user
            new_topic_object.save()
            return redirect('learning_logs:topics')

    # Вывести пустую или недействительную форму.
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме."""
    topic_object = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = EntryForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry_object = form.save(commit=False)
            new_entry_object.topic = topic_object
            new_entry_object.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Вывести пустую или недействительную форму.
    context = {'topic': topic_object, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись."""
    entry_object = Entry.objects.get(id=entry_id)
    topic_object = entry_object.topic
    if topic_object.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = EntryForm(instance=entry_object)
    else:
        # Отправка данных POST; обработать данные.
        form = EntryForm(instance=entry_object, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic_object.id)
    context = {'entry': entry_object, 'topic': topic_object, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
