from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea, Select, NumberInput, CheckboxInput, URLInput
from main.models import Experience, Project, Skill

class ProjectForm(ModelForm):
    secret_code = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter secret code to authorize",
                "class": "form-input",
            }
        ),
        label="Secret Passcode",
        required=True,
    )
    
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

    def clean_secret_code(self):
        code = self.cleaned_data.get("secret_code")
        expected_code = settings.PORTFOLIO_SECRET_CODE
        if expected_code and code != expected_code:
            raise ValidationError("Kode otorisasi salah! Aksi dibatalkan.")
        return code

class SkillForm(ModelForm):
    secret_code = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter secret code to authorize",
                "class": "form-input",
            }
        ),
        label="Secret Passcode",
        required=True,
    )

    class Meta:
        model = Skill
        fields = [
            "name",
            "category",
            "proficiency_percent",
            "logo_url",
            "is_core",
        ]
        labels = {
            "name": "Skill Name",
            "category": "Category",
            "proficiency_percent": "Proficiency (%)",
            "logo_url": "Logo URL (Google Drive / Direct Link)",
            "is_core": "Highlight as Core Skill?",
        }
        widgets = {
            "name": TextInput(attrs={"placeholder": "e.g., Python, Linux Kernel", "class": "form-input", "maxlength": 100}),
            "category": Select(attrs={"class": "form-input"}),
            "proficiency_percent": NumberInput(attrs={"min": 0, "max": 100, "class": "form-input", "placeholder": "85"}),
            "logo_url": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000", "class": "form-input"}),
            "is_core": CheckboxInput(attrs={"class": "form-checkbox"}),
        }

    def clean_secret_code(self):
        code = self.cleaned_data.get("secret_code")
        if code != settings.PORTFOLIO_SECRET_CODE:
            raise ValidationError("Kode rahasia salah! Aksi tidak diizinkan.")
        return code

class ExperienceForm(ModelForm):
    secret_code = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter secret code to authorize",
                "class": "form-input",
            }
        ),
        label="Secret Passcode",
        required=True,
    )
    is_ongoing = forms.BooleanField(
        required=False,
        initial=True,
        label="Sedang Berlangsung?",
        widget=CheckboxInput(attrs={"class": "form-checkbox"}),
    )

    class Meta:
        model = Experience
        fields = [
            "title",
            "category",
            "description",
            "thumbnail",
        ]
        labels = {
            "title": "Judul Pengalaman",
            "category": "Kategori",
            "description": "Deskripsi Peran & Tanggung Jawab",
            "thumbnail": "URL Thumbnail (Opsional)",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "e.g., Software Engineer Intern", "class": "form-input", "maxlength": 255}),
            "category": Select(attrs={"class": "form-input"}),
            "description": Textarea(attrs={"placeholder": "Ceritakan peran, proyek, dan kontribusi Anda...", "rows": 4}),
            "thumbnail": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000", "class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["is_ongoing"].initial = self.instance.is_ongoing

    def clean_secret_code(self):
        code = self.cleaned_data.get("secret_code")
        expected_code = settings.PORTFOLIO_SECRET_CODE
        if expected_code and code != expected_code:
            raise ValidationError("Kode otorisasi salah! Aksi dibatalkan.")
        return code

    def save(self, commit=True):
        from django.utils import timezone
        instance = super().save(commit=False)
        is_ongoing = self.cleaned_data.get("is_ongoing")
        if is_ongoing:
            instance.ended_at = None
        elif not instance.ended_at:
            instance.ended_at = timezone.now()
        if commit:
            instance.save()
        return instance