from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, NumberInput, CheckboxInput
from main.models import Project, Skill

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Portfolio Website", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Ceritakan Proyekmu", "rows": 3}),
            "tech_stack": TextInput(attrs={"placeholder": "Django, Python, HTML, CSS"}),
            "project_url": URLInput(attrs={"placeholder": "https://github.com/username/project"}),
            "project_image_url": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
        }

class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = [
            "name",
            "category",
            "proficiency_percent",
            "is_core",
        ]
        labels = {
            "name": "Skill Name",
            "category": "Category",
            "proficiency_percent": "Proficiency (%)",
            "is_core": "Highlight as Core Skill?",
        }
        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "e.g., Python, Linux Kernel, Reverse Engineering",
                    "class": "form-input",
                    "maxlength": 100,
                }
            ),
            "category": Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "proficiency_percent": NumberInput(
                attrs={
                    "min": 0,
                    "max": 100,
                    "class": "form-input",
                    "placeholder": "85",
                }
            ),
            "is_core": CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                }
            ),
    }