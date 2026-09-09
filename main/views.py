from django.shortcuts import render
from main.models import Experience

def show_main(request):
    context = {
        "name": "Adam Wahyu Syaputra",
        "npm": "2506534964",
        "study_program": "Computer Science",
        "bio": (
            "Hi, I'm Adam! I'm a Computer Science student at the University of Indonesia, "
            "passionate about cybersecurity, systems, and software engineering."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Adam Wahyu Syaputra",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)
