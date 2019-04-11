from django.shortcuts import render
from django.utils.safestring import mark_safe
import json


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, subject):
    return render(request, 'chat/room.html', {
        'subject_json': mark_safe(json.dumps(subject)),
        'room_pk': mark_safe(json.dumps("")),
    })


def roomandmore(request, subject):
    return render(request, 'chat/room.html', {
        'subject_json': mark_safe(json.dumps(subject)),
    })
