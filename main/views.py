from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import ProjectForm, SkillForm
from main.models import Experience, Project, Skill
from django.conf import settings

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

# Experience field
def show_experience(request):
    context = {
        "name": NAME,
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


# Projects field
def create_project(request):
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

def update_project(request, project_id):
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

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        code = request.POST.get("secret_code", "")
        expected_code = settings.PORTFOLIO_SECRET_CODE
        if not expected_code or code == expected_code:
            project.delete()
            messages.success(request, "Project berhasil dihapus!")
        else:
            messages.error(request, "Gagal menghapus: Kode rahasia salah!")
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

# 3. Create Skill with Secret Code Protection
def create_skill(request):
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

# 4. Update Skill with Secret Code Protection
def update_skill(request, skill_id):
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

# 5. Delete Skill with Secret Code Protection
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        code = request.POST.get("secret_code", "")
        if code == settings.PORTFOLIO_SECRET_CODE:
            skill.delete()
            messages.success(request, "Keahlian berhasil dihapus!")
        else:
            messages.error(request, "Gagal menghapus: Kode rahasia salah!")
    return redirect("main:show_skills")