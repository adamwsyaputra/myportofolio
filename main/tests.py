from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from main.models import Experience, Project

class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))
        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="EduText AI",
            description="Platform aksesibilitas AI melalui jaringan SMS 2G.",
            tech_stack="Python, API, Telephony",
            project_url="https://github.com/adamwsyaputra",
        )

    def test_projects_url_is_accessible_and_uses_correct_template(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_projects_page_displays_model_data(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.tech_stack)

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")

    def test_project_model_str(self):
        self.assertEqual(str(self.project), "EduText AI")

    def test_projects_page_contains_edit_link(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        edit_url = reverse("main:update_project", args=[self.project.id])
        self.assertContains(response, f'href="{edit_url}"')

    def test_update_project_get(self):
        edit_url = reverse("main:update_project", args=[self.project.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, "Edit Project:")

    def test_update_project_post_valid(self):
        from django.conf import settings
        edit_url = reverse("main:update_project", args=[self.project.id])
        payload = {
            "title": "EduText AI Updated",
            "description": "Updated description for AI SMS.",
            "tech_stack": "Python, Django, Telephony",
            "project_url": "https://github.com/adamwsyaputra/updated",
            "project_image_url": "",
            "secret_code": settings.PORTFOLIO_SECRET_CODE or "adam1012",
        }
        response = self.client.post(edit_url, payload)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "EduText AI Updated")

    def test_update_project_post_invalid_passcode(self):
        edit_url = reverse("main:update_project", args=[self.project.id])
        payload = {
            "title": "Hacked Title",
            "description": "Hacked description.",
            "tech_stack": "Hacked",
            "project_url": "https://hacked.com",
            "project_image_url": "",
            "secret_code": "wrong_passcode_xyz",
        }
        response = self.client.post(edit_url, payload)
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "EduText AI")