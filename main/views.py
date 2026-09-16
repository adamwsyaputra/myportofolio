from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import ProjectForm
from main.models import Experience, Project

NAME = "Adam Wahyu Syaputra"

def show_main(request):
    context = {
        "name": NAME,
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
        "name": NAME,
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")
    
    context = {
        "name": NAME,
        "form": form,
    }
    return render(request, "projects_form.html", context)

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")
    return redirect("main:show_projects")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def show_projects(request):
    # Pola data delivery: ambil response serialize JSON, lalu deserialize ke objek Python
    json_response = get_projects_json(request)
    deserialized = serializers.deserialize("json", json_response.content.decode("utf-8"))
    projects = [p.object for p in deserialized]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": NAME,
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "projects.html", context)