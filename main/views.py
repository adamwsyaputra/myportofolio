import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import ExperienceForm, ProjectForm, SkillForm
from main.models import Experience, Project, Skill

NAME = "Adam Wahyu Syaputra"

def is_editor(user):
    """
    Verify if an account is an editor.
    Superusers have implicit editor privileges.
    """
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name="Editor").exists())

is_editor_or_superuser = is_editor


def show_main(request):
    context = {
        "name": NAME,
        "npm": "2506534964",
        "study_program": "Computer Science",
        "bio": (
            "Hi, I'm Adam! I'm a Computer Science student at the University of Indonesia, "
            "passionate about cybersecurity, systems, and software engineering."
        ),
        "last_login": request.COOKIES.get("last_login", "Never"),
    }
    return render(request, "index.html", context)

# Experience field
def show_experience(request):
    category_query = request.GET.get("category", "").strip()
    experiences = Experience.objects.all().order_by("-started_at")
    if category_query:
        experiences = experiences.filter(category=category_query)
    context = {
        "name": NAME,
        "experience_list": experiences,
        "selected_category": category_query,
    }
    return render(request, "experience.html", context)

def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")
    
    context = {
        "name": NAME,
        "form": form,
        "action_title": "Add New Experience",
        "btn_label": "Tambah Pengalaman",
        "kicker": "TAMBAHKAN PENGALAMAN BARU",
    }
    return render(request, "experience_form.html", context)

def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Pengalaman {experience.title} berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": NAME,
        "form": form,
        "action_title": f"Edit Experience: {experience.title}",
        "btn_label": "Simpan Perubahan",
        "kicker": "MANAGEMENT CONSOLE",
    }
    return render(request, "experience_form.html", context)

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_experience")


# Projects field
@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")
    
    context = {
        "name": NAME,
        "form": form,
        "action_title": "Add New Project",
        "btn_label": "Tambah Project",
        "kicker": "TAMBAHKAN PROYEK BARU",
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def update_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Proyek {project.title} berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": NAME,
        "form": form,
        "action_title": f"Edit Project: {project.title}",
        "btn_label": "Simpan Perubahan",
        "kicker": "MANAGEMENT CONSOLE",
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
    return redirect("main:show_projects")

@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    return redirect("main:show_projects")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True)
    return HttpResponse(projects_json, content_type="application/json")

def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all().prefetch_related("starred_by")
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    context = {
        "name": NAME,
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "projects.html", context)


# Skills field
# 1. API: Retrieve data in JSON format
def get_skills_json(request):
    category_query = request.GET.get("category", "").strip()
    skills = Skill.objects.all().order_by("-is_core", "-proficiency_percent")
    if category_query:
        skills = skills.filter(category=category_query)
    skills_json = serializers.serialize("json", skills)
    return HttpResponse(skills_json, content_type="application/json")

# 2. Display: Fetch JSON & deserialize to Python objects
def show_skills(request):
    json_response = get_skills_json(request)
    deserialized = serializers.deserialize("json", json_response.content.decode("utf-8"))
    skills = [item.object for item in deserialized]
    category_query = request.GET.get("category", "").strip()

    context = {
        "name": NAME,
        "skill_list": skills,
        "selected_category": category_query,
    }
    return render(request, "skills.html", context)

@login_required(login_url="/login/")
def create_skill(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Keahlian baru berhasil ditambahkan!")
        return redirect("main:show_skills")

    context = {
        "name": NAME,
        "form": form,
        "action_title": "Add New Skill",
        "btn_label": "Tambah Skill",
    }
    return render(request, "skill_form.html", context)

@login_required(login_url="/login/")
def update_skill(request, skill_id):
    if not is_editor(request.user):
        raise PermissionDenied
    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skill)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Keahlian {skill.name} berhasil diperbarui!")
        return redirect("main:show_skills")

    context = {
        "name": NAME,
        "form": form,
        "action_title": f"Edit Skill: {skill.name}",
        "btn_label": "Simpan Perubahan",
    }
    return render(request, "skill_form.html", context)

@login_required(login_url="/login/")
def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Keahlian berhasil dihapus!")
    return redirect("main:show_skills")

@login_required(login_url="/login/")
def toggle_star_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        if request.user in skill.starred_by.all():
            skill.starred_by.remove(request.user)
        else:
            skill.starred_by.add(request.user)
    return redirect("main:show_skills")


# Authentication Views
def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your account has been successfully created!")
        return redirect("main:login")
    
    context = {
        "name": NAME,
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response
    
    context = {
        "name": NAME,
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response