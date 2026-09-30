from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from main.models import Experience, Project, Skill

class MainTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group, User
        self.editor_group = Group.objects.create(name="Editor")
        self.regular_user = User.objects.create_user(username="regular_exp", password="RegularPassword123!")
        self.editor_user = User.objects.create_user(username="editor_exp", password="EditorPassword123!")
        self.editor_user.groups.add(self.editor_group)
        self.superuser = User.objects.create_superuser(username="admin_exp", password="AdminPassword123!")

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

    def test_experience_page_anonymous_controls(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        edit_url = reverse("main:update_experience", args=[self.experience.id])
        self.assertNotContains(response, f'href="{edit_url}"')
        self.assertNotContains(response, "+ Tambah Pengalaman")
        self.assertNotContains(response, f'popovertarget="delete-exp-{self.experience.id}"')
        vouch_url = reverse("main:toggle_vouch_experience", args=[self.experience.id])
        self.assertContains(response, f'action="{vouch_url}"')

    def test_create_experience_anonymous_redirects(self):
        response = self.client.get(reverse("main:create_experience"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_create_experience_non_superuser_forbidden(self):
        self.client.login(username="regular_exp", password="RegularPassword123!")
        response = self.client.get(reverse("main:create_experience"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="editor_exp", password="EditorPassword123!")
        response_ed = self.client.get(reverse("main:create_experience"))
        self.assertEqual(response_ed.status_code, 403)

    def test_create_experience_superuser_allowed(self):
        self.client.login(username="admin_exp", password="AdminPassword123!")
        response = self.client.get(reverse("main:create_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")

        payload = {
            "title": "Backend Intern",
            "category": "internship",
            "description": "Building microservices with Django and FastAPI.",
            "thumbnail": "",
            "is_ongoing": "on",
        }
        post_response = self.client.post(reverse("main:create_experience"), payload)
        self.assertRedirects(post_response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Backend Intern").exists())

    def test_update_experience_anonymous_redirects(self):
        edit_url = reverse("main:update_experience", args=[self.experience.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_update_experience_regular_forbidden(self):
        self.client.login(username="regular_exp", password="RegularPassword123!")
        edit_url = reverse("main:update_experience", args=[self.experience.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 403)

    def test_update_experience_editor_allowed(self):
        self.client.login(username="editor_exp", password="EditorPassword123!")
        edit_url = reverse("main:update_experience", args=[self.experience.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, self.experience.title)

        payload = {
            "title": "Koordinator Asisten Dosen PBP",
            "category": "part-time",
            "description": "Memimpin tim asisten dosen pengembangan web.",
            "thumbnail": "",
            "is_ongoing": "on",
        }
        post_response = self.client.post(edit_url, payload)
        self.assertRedirects(post_response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Koordinator Asisten Dosen PBP")

    def test_delete_experience_anonymous_redirects(self):
        delete_url = reverse("main:delete_experience", args=[self.experience.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_delete_experience_regular_and_editor_forbidden(self):
        delete_url = reverse("main:delete_experience", args=[self.experience.id])

        self.client.login(username="regular_exp", password="RegularPassword123!")
        response_reg = self.client.post(delete_url)
        self.assertEqual(response_reg.status_code, 403)

        self.client.login(username="editor_exp", password="EditorPassword123!")
        response_ed = self.client.post(delete_url)
        self.assertEqual(response_ed.status_code, 403)

    def test_delete_experience_superuser_allowed(self):
        self.client.login(username="admin_exp", password="AdminPassword123!")
        delete_url = reverse("main:delete_experience", args=[self.experience.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_toggle_vouch_experience(self):
        vouch_url = reverse("main:toggle_vouch_experience", args=[self.experience.id])

        # Anonymous cannot vouch
        anon_resp = self.client.post(vouch_url)
        self.assertEqual(anon_resp.status_code, 302)
        self.assertIn("/login/", anon_resp.url)

        # Regular user can vouch
        self.client.login(username="regular_exp", password="RegularPassword123!")
        post_resp = self.client.post(vouch_url)
        self.assertRedirects(post_resp, reverse("main:show_experience"))
        self.assertTrue(self.experience.vouched_by.filter(id=self.regular_user.id).exists())

        # Unvouch
        post_resp2 = self.client.post(vouch_url)
        self.assertRedirects(post_resp2, reverse("main:show_experience"))
        self.assertFalse(self.experience.vouched_by.filter(id=self.regular_user.id).exists())


class ProjectTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.superuser = User.objects.create_superuser(
            username="admin_proj",
            password="AdminPassword123!",
        )
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
        # show_projects serves an empty HTML shell; project_list is decoupled from context
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("project_list", response.context)
        # Static project card content is not server-rendered
        self.assertNotContains(response, self.project.title)
        # Assert state containers exist
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="error"')

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, "Belum ada proyek...")

    def test_project_model_str(self):
        self.assertEqual(str(self.project), "EduText AI")

    def test_projects_page_contains_edit_link(self):
        # In the AJAX shell, individual edit links are rendered dynamically via JavaScript.
        # Verify that the server-rendered shell provides the superuser controls and modal.
        self.client.login(username="admin_proj", password="AdminPassword123!")
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'const IS_SUPERUSER = "true" === "true";')
        self.assertContains(response, "Tambah Proyek")
        self.assertContains(response, 'popovertarget="add-project-modal"')
        self.assertContains(response, 'id="add-project-modal"')
        self.assertIn("form", response.context)

    def test_update_project_get(self):
        self.client.login(username="admin_proj", password="AdminPassword123!")
        edit_url = reverse("main:update_project", args=[self.project.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, "Edit Project:")

    def test_update_project_post_valid(self):
        self.client.login(username="admin_proj", password="AdminPassword123!")
        edit_url = reverse("main:update_project", args=[self.project.id])
        payload = {
            "title": "EduText AI Updated",
            "description": "Updated description for AI SMS.",
            "tech_stack": "Python, Django, Telephony",
            "project_url": "https://github.com/adamwsyaputra/updated",
            "project_image_url": "",
        }
        response = self.client.post(edit_url, payload)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "EduText AI Updated")

    def test_update_project_post_invalid_data(self):
        self.client.login(username="admin_proj", password="AdminPassword123!")
        edit_url = reverse("main:update_project", args=[self.project.id])
        payload = {
            "title": "",
            "description": "Hacked description.",
            "tech_stack": "Hacked",
            "project_url": "https://hacked.com",
            "project_image_url": "",
        }
        response = self.client.post(edit_url, payload)
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "EduText AI")


class AuthTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPassword123!",
        )

    def test_register_page_get(self):
        response = self.client.get(reverse("main:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, "Create an Account")
        self.assertContains(response, f'action="{reverse("main:register")}"')

    def test_register_post_valid(self):
        from django.contrib.auth.models import User
        payload = {
            "username": "newuser",
            "password1": "AnotherPassword456!",
            "password2": "AnotherPassword456!",
        }
        response = self.client.post(reverse("main:register"), payload)
        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_page_get(self):
        response = self.client.get(reverse("main:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertContains(response, "Login")
        self.assertContains(response, f'action="{reverse("main:login")}"')

    def test_login_post_valid(self):
        payload = {
            "username": "testuser",
            "password": "StrongPassword123!",
        }
        response = self.client.post(reverse("main:login"), payload)
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_logout(self):
        self.client.login(username="testuser", password="StrongPassword123!")
        response = self.client.get(reverse("main:logout"))
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_navbar_unauthenticated(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, f'href="{reverse("main:login")}"')
        self.assertContains(response, f'href="{reverse("main:register")}"')
        self.assertNotContains(response, f'href="{reverse("main:logout")}"')

    def test_navbar_authenticated(self):
        self.client.login(username="testuser", password="StrongPassword123!")
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "testuser")
        self.assertContains(response, f'href="{reverse("main:logout")}"')
        self.assertNotContains(response, f'href="{reverse("main:login")}"')
        self.assertNotContains(response, f'href="{reverse("main:register")}"')

    def test_login_sets_last_login_cookie(self):
        payload = {
            "username": "testuser",
            "password": "StrongPassword123!",
        }
        response = self.client.post(reverse("main:login"), payload)
        self.assertIn("last_login", response.cookies)
        self.assertTrue(len(response.cookies["last_login"].value) > 0)

    def test_logout_deletes_last_login_cookie(self):
        payload = {
            "username": "testuser",
            "password": "StrongPassword123!",
        }
        self.client.post(reverse("main:login"), payload)
        response = self.client.get(reverse("main:logout"))
        # In Django, delete_cookie sets max-age=0 and expires in the past
        self.assertIn("last_login", response.cookies)
        self.assertEqual(response.cookies["last_login"].value, "")

    def test_show_main_displays_last_login(self):
        self.client.cookies["last_login"] = "2026-09-27 10:55:00"
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026-09-27 10:55:00")


class ProjectPermissionTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group, User
        self.regular_user = User.objects.create_user(
            username="regular",
            password="RegularPassword123!",
        )
        self.superuser = User.objects.create_superuser(
            username="adminuser",
            password="AdminPassword123!",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor_user = User.objects.create_user(
            username="editor_proj",
            password="EditorPassword123!",
        )
        self.editor_user.groups.add(self.editor_group)
        self.project = Project.objects.create(
            title="Secured Project",
            description="Testing authorization rules.",
            tech_stack="Django, Auth",
        )

    def test_create_project_anonymous_redirects(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_create_project_non_superuser_forbidden(self):
        self.client.login(username="regular", password="RegularPassword123!")
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 403)

    def test_create_project_superuser_allowed(self):
        self.client.login(username="adminuser", password="AdminPassword123!")
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 200)

        payload = {
            "title": "Superuser Project",
            "description": "Created by superuser.",
            "tech_stack": "Django",
            "project_url": "",
            "project_image_url": "",
        }
        post_response = self.client.post(reverse("main:create_project"), payload)
        self.assertRedirects(post_response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Superuser Project").exists())

    def test_delete_project_anonymous_redirects(self):
        delete_url = reverse("main:delete_project", args=[self.project.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_non_superuser_forbidden(self):
        self.client.login(username="regular", password="RegularPassword123!")
        delete_url = reverse("main:delete_project", args=[self.project.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_superuser_allowed(self):
        self.client.login(username="adminuser", password="AdminPassword123!")
        delete_url = reverse("main:delete_project", args=[self.project.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_update_project_anonymous_redirects(self):
        edit_url = reverse("main:update_project", args=[self.project.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_update_project_non_superuser_forbidden(self):
        self.client.login(username="regular", password="RegularPassword123!")
        edit_url = reverse("main:update_project", args=[self.project.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 403)

    def test_update_project_editor_allowed(self):
        self.client.login(username="editor_proj", password="EditorPassword123!")
        edit_url = reverse("main:update_project", args=[self.project.id])
        get_res = self.client.get(edit_url)
        self.assertEqual(get_res.status_code, 200)

        payload = {
            "title": "Secured Project Edited by Editor",
            "description": "Edited by editor.",
            "tech_stack": "Django",
            "project_url": "",
            "project_image_url": "",
        }
        post_res = self.client.post(edit_url, payload)
        self.assertRedirects(post_res, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Secured Project Edited by Editor")

    def test_projects_page_ui_controls_visitor_vs_superuser(self):
        # Anonymous visitor
        response = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(response, "Tambah Proyek")
        self.assertNotContains(response, 'id="add-project-modal"')
        self.assertNotContains(response, 'popovertarget="add-project-modal"')
        self.assertContains(response, 'const IS_SUPERUSER = "false" === "true";')
        self.assertContains(response, 'const IS_EDITOR = "false" === "true";')

        # Regular user
        self.client.login(username="regular", password="RegularPassword123!")
        response = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(response, "Tambah Proyek")
        self.assertNotContains(response, 'id="add-project-modal"')
        self.assertNotContains(response, 'popovertarget="add-project-modal"')
        self.assertContains(response, 'const IS_SUPERUSER = "false" === "true";')
        self.assertContains(response, 'const IS_EDITOR = "false" === "true";')

        # Editor user
        self.client.login(username="editor_proj", password="EditorPassword123!")
        response_ed = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(response_ed, "Tambah Proyek")
        self.assertNotContains(response_ed, 'id="add-project-modal"')
        self.assertNotContains(response_ed, 'popovertarget="add-project-modal"')
        self.assertContains(response_ed, 'const IS_SUPERUSER = "false" === "true";')
        self.assertContains(response_ed, 'const IS_EDITOR = "true" === "true";')

        # Superuser
        self.client.login(username="adminuser", password="AdminPassword123!")
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "Tambah Proyek")
        self.assertContains(response, 'popovertarget="add-project-modal"')
        self.assertContains(response, 'id="add-project-modal"')
        self.assertContains(response, 'const IS_SUPERUSER = "true" === "true";')
        self.assertContains(response, 'const IS_EDITOR = "true" === "true";')


class ProjectStarTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username="staruser",
            password="StarPassword123!",
        )
        self.project = Project.objects.create(
            title="Starry Project",
            description="Testing the star and unstar functionality.",
            tech_stack="Django, M2M",
        )

    def test_toggle_star_anonymous_redirects(self):
        star_url = reverse("main:toggle_star", args=[self.project.id])
        response = self.client.post(star_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_toggle_star_authenticated_success(self):
        self.client.login(username="staruser", password="StarPassword123!")
        star_url = reverse("main:toggle_star", args=[self.project.id])

        # First POST: Star the project
        response1 = self.client.post(star_url)
        self.assertRedirects(response1, reverse("main:show_projects"))
        self.assertEqual(self.project.starred_by.count(), 1)
        self.assertTrue(self.project.starred_by.filter(id=self.user.id).exists())

        # Second POST: Unstar the project
        response2 = self.client.post(star_url)
        self.assertRedirects(response2, reverse("main:show_projects"))
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_star_button_ui_rendering(self):
        # In the AJAX architecture, star state and counts are delivered via get_projects_json
        # Initially unstarred
        res_unstarred = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(res_unstarred.status_code, 200)
        data = res_unstarred.json()
        proj = next(item for item in data if item["pk"] == str(self.project.id))
        self.assertEqual(proj["fields"]["star_count"], 0)
        self.assertFalse(proj["fields"]["is_starred"])

        # Star the project
        self.project.starred_by.add(self.user)
        self.client.login(username="staruser", password="StarPassword123!")
        res_starred = self.client.get(reverse("main:get_projects_json"))
        data_starred = res_starred.json()
        proj_starred = next(item for item in data_starred if item["pk"] == str(self.project.id))
        self.assertEqual(proj_starred["fields"]["star_count"], 1)
        self.assertTrue(proj_starred["fields"]["is_starred"])
        self.assertIn("staruser", proj_starred["fields"]["starred_by_names"])

    def test_api_projects_use_natural_foreign_keys(self):
        # Tutorial 5 replaced natural foreign keys with optimized manual JSON assembly
        self.project.starred_by.add(self.user)
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/json"))
        data = response.json()
        starred_project = next(item for item in data if item["pk"] == str(self.project.id))
        self.assertEqual(starred_project["fields"]["star_count"], 1)
        self.assertIn("staruser", starred_project["fields"]["starred_by_names"])


class SkillTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group, User
        self.editor_group = Group.objects.create(name="Editor")
        self.regular_user = User.objects.create_user(username="regular_skill", password="RegularPassword123!")
        self.editor_user = User.objects.create_user(username="editor_skill", password="EditorPassword123!")
        self.editor_user.groups.add(self.editor_group)
        self.superuser = User.objects.create_superuser(username="admin_skill", password="AdminPassword123!")

        self.skill = Skill.objects.create(
            name="Python",
            category="languages",
            proficiency_percent=90,
            is_core=True,
        )

    def test_skills_page_displays_skill(self):
        response = self.client.get(reverse("main:show_skills"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")

    # Anonymous Visitor Tests
    def test_anonymous_cannot_create_skill(self):
        response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_anonymous_cannot_update_skill(self):
        edit_url = reverse("main:update_skill", args=[self.skill.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_anonymous_cannot_delete_skill(self):
        delete_url = reverse("main:delete_skill", args=[self.skill.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_anonymous_cannot_toggle_star_skill(self):
        star_url = reverse("main:toggle_star_skill", args=[self.skill.id])
        response = self.client.post(star_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    # Regular User Tests
    def test_regular_user_cannot_create_skill(self):
        self.client.login(username="regular_skill", password="RegularPassword123!")
        response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_update_skill(self):
        self.client.login(username="regular_skill", password="RegularPassword123!")
        edit_url = reverse("main:update_skill", args=[self.skill.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_delete_skill(self):
        self.client.login(username="regular_skill", password="RegularPassword123!")
        delete_url = reverse("main:delete_skill", args=[self.skill.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_can_toggle_star_skill(self):
        self.client.login(username="regular_skill", password="RegularPassword123!")
        star_url = reverse("main:toggle_star_skill", args=[self.skill.id])
        # Star
        response = self.client.post(star_url)
        self.assertRedirects(response, reverse("main:show_skills"))
        self.assertTrue(self.skill.starred_by.filter(id=self.regular_user.id).exists())
        # Unstar
        response2 = self.client.post(star_url)
        self.assertRedirects(response2, reverse("main:show_skills"))
        self.assertFalse(self.skill.starred_by.filter(id=self.regular_user.id).exists())

    # Editor Tests
    def test_editor_cannot_create_skill(self):
        self.client.login(username="editor_skill", password="EditorPassword123!")
        response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(response.status_code, 403)

    def test_editor_cannot_delete_skill(self):
        self.client.login(username="editor_skill", password="EditorPassword123!")
        delete_url = reverse("main:delete_skill", args=[self.skill.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 403)

    def test_editor_can_update_skill(self):
        self.client.login(username="editor_skill", password="EditorPassword123!")
        edit_url = reverse("main:update_skill", args=[self.skill.id])
        get_response = self.client.get(edit_url)
        self.assertEqual(get_response.status_code, 200)

        payload = {
            "name": "Python 3.12",
            "category": "languages",
            "proficiency_percent": 95,
            "is_core": True,
            "logo_url": "",
        }
        post_response = self.client.post(edit_url, payload)
        self.assertRedirects(post_response, reverse("main:show_skills"))
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python 3.12")

    # Superuser Tests
    def test_superuser_can_create_skill(self):
        self.client.login(username="admin_skill", password="AdminPassword123!")
        get_response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(get_response.status_code, 200)

        payload = {
            "name": "Rust",
            "category": "languages",
            "proficiency_percent": 80,
            "is_core": False,
            "logo_url": "",
        }
        post_response = self.client.post(reverse("main:create_skill"), payload)
        self.assertRedirects(post_response, reverse("main:show_skills"))
        self.assertTrue(Skill.objects.filter(name="Rust").exists())

    def test_superuser_can_update_skill(self):
        self.client.login(username="admin_skill", password="AdminPassword123!")
        edit_url = reverse("main:update_skill", args=[self.skill.id])
        payload = {
            "name": "Python Master",
            "category": "languages",
            "proficiency_percent": 99,
            "is_core": True,
            "logo_url": "",
        }
        post_response = self.client.post(edit_url, payload)
        self.assertRedirects(post_response, reverse("main:show_skills"))
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python Master")

    def test_superuser_can_delete_skill(self):
        self.client.login(username="admin_skill", password="AdminPassword123!")
        delete_url = reverse("main:delete_skill", args=[self.skill.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("main:show_skills"))
        self.assertFalse(Skill.objects.filter(id=self.skill.id).exists())

    def test_skills_page_ui_controls_4_tiers(self):
        edit_url = reverse("main:update_skill", args=[self.skill.id])
        endorse_url = reverse("main:toggle_endorse_skill", args=[self.skill.id])

        # 1. Anonymous visitor
        response_anon = self.client.get(reverse("main:show_skills"))
        self.assertNotContains(response_anon, "+ Tambah Skill")
        self.assertNotContains(response_anon, f'href="{edit_url}"')
        self.assertNotContains(response_anon, f'popovertarget="delete-skill-{self.skill.id}"')
        self.assertContains(response_anon, f'action="{endorse_url}"')
        self.assertContains(response_anon, "Endorse")
        self.assertContains(response_anon, '<span class="star-count endorse-count">0</span>')

        # 2. Regular user
        self.client.login(username="regular_skill", password="RegularPassword123!")
        response_reg = self.client.get(reverse("main:show_skills"))
        self.assertNotContains(response_reg, "+ Tambah Skill")
        self.assertNotContains(response_reg, f'href="{edit_url}"')
        self.assertNotContains(response_reg, f'popovertarget="delete-skill-{self.skill.id}"')
        self.assertContains(response_reg, f'action="{endorse_url}"')

        # Regular user endorses the skill
        self.client.post(endorse_url)
        response_reg_starred = self.client.get(reverse("main:show_skills"))
        self.assertContains(response_reg_starred, "is-endorsed")
        self.assertContains(response_reg_starred, "Endorsed")
        self.assertContains(response_reg_starred, '<span class="star-count endorse-count">1</span>')
        self.assertContains(response_reg_starred, "regular_skill")

        # 3. Editor user
        self.client.login(username="editor_skill", password="EditorPassword123!")
        response_editor = self.client.get(reverse("main:show_skills"))
        self.assertNotContains(response_editor, "+ Tambah Skill")
        self.assertContains(response_editor, f'href="{edit_url}"')
        self.assertNotContains(response_editor, f'popovertarget="delete-skill-{self.skill.id}"')
        self.assertContains(response_editor, f'action="{endorse_url}"')

        # 4. Superuser
        self.client.login(username="admin_skill", password="AdminPassword123!")
        response_admin = self.client.get(reverse("main:show_skills"))
        self.assertContains(response_admin, "+ Tambah Skill")
        self.assertContains(response_admin, f'href="{edit_url}"')
        self.assertContains(response_admin, f'popovertarget="delete-skill-{self.skill.id}"')
        self.assertContains(response_admin, f'action="{endorse_url}"')

    def test_api_skills_use_natural_foreign_keys(self):
        import json
        self.skill.starred_by.add(self.regular_user)
        response = self.client.get(reverse("main:get_skills_json"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        starred_skill = next(item for item in data if item["pk"] == str(self.skill.id))
        self.assertEqual(starred_skill["fields"]["starred_by"], [["regular_skill"]])




class RoleArchitectureTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group, User
        self.editor_group = Group.objects.create(name="Editor")
        self.regular_user = User.objects.create_user(username="regular_role", password="Password123!")
        self.editor_user = User.objects.create_user(username="editor_role", password="Password123!")
        self.editor_user.groups.add(self.editor_group)
        self.superuser = User.objects.create_superuser(username="admin_role", password="Password123!")

    def test_is_editor_helper(self):
        from django.contrib.auth.models import AnonymousUser
        from main.views import is_editor

        self.assertFalse(is_editor(AnonymousUser()))
        self.assertFalse(is_editor(self.regular_user))
        self.assertTrue(is_editor(self.editor_user))
        self.assertTrue(is_editor(self.superuser))


class ProjectAjaxRoutesTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group, User
        self.editor_group = Group.objects.create(name="Editor")

        self.superuser = User.objects.create_superuser(
            username="ajax_admin",
            password="AdminPassword123!",
        )
        self.regular_user = User.objects.create_user(
            username="ajax_regular",
            password="RegularPassword123!",
        )
        self.editor_user = User.objects.create_user(
            username="ajax_editor",
            password="EditorPassword123!",
        )
        self.editor_user.groups.add(self.editor_group)

        self.project = Project.objects.create(
            title="EduText AI",
            description="Platform aksesibilitas AI melalui jaringan SMS 2G.",
            tech_stack="Python, Twilio, OpenAI",
            project_url="https://github.com/adamwsyaputra/sms-ai",
            project_image_url="https://images.unsplash.com/photo-ai.jpg",
        )

    # 1. get_projects_json tests
    def test_get_projects_json_returns_200_and_json(self):
        url = reverse("main:get_projects_json")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/json"))

    def test_get_projects_json_fields_and_unstarred_state(self):
        url = reverse("main:get_projects_json")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

        item = next(p for p in data if p["pk"] == str(self.project.id))
        fields = item["fields"]
        self.assertEqual(fields["title"], "EduText AI")
        self.assertEqual(fields["description"], "Platform aksesibilitas AI melalui jaringan SMS 2G.")
        self.assertEqual(fields["tech_stack"], "Python, Twilio, OpenAI")
        self.assertEqual(fields["project_url"], "https://github.com/adamwsyaputra/sms-ai")
        self.assertEqual(fields["project_image_url"], "https://images.unsplash.com/photo-ai.jpg")
        self.assertIn("star_count", fields)
        self.assertIn("is_starred", fields)
        self.assertIn("starred_by_names", fields)
        self.assertEqual(fields["star_count"], 0)
        self.assertFalse(fields["is_starred"])

    def test_get_projects_json_authenticated_starred_state(self):
        self.project.starred_by.add(self.regular_user)
        url = reverse("main:get_projects_json")

        # Anonymous visitor sees star count but is_starred=False
        anon_resp = self.client.get(url)
        anon_item = next(p for p in anon_resp.json() if p["pk"] == str(self.project.id))
        self.assertEqual(anon_item["fields"]["star_count"], 1)
        self.assertFalse(anon_item["fields"]["is_starred"])

        # Authenticated starer sees is_starred=True
        self.client.login(username="ajax_regular", password="RegularPassword123!")
        auth_resp = self.client.get(url)
        auth_item = next(p for p in auth_resp.json() if p["pk"] == str(self.project.id))
        self.assertEqual(auth_item["fields"]["star_count"], 1)
        self.assertTrue(auth_item["fields"]["is_starred"])
        self.assertIn("ajax_regular", auth_item["fields"]["starred_by_names"])

    def test_get_projects_json_title_search_filter(self):
        Project.objects.create(
            title="Comic Canvas App",
            description="Comic book editor.",
            tech_stack="TypeScript, React",
        )
        url = reverse("main:get_projects_json")

        # Query matching 'EduText'
        resp_edu = self.client.get(url, {"title": "EduText"})
        data_edu = resp_edu.json()
        self.assertEqual(len(data_edu), 1)
        self.assertEqual(data_edu[0]["fields"]["title"], "EduText AI")

        # Query matching 'Canvas'
        resp_comic = self.client.get(url, {"title": "Canvas"})
        data_comic = resp_comic.json()
        self.assertEqual(len(data_comic), 1)
        self.assertEqual(data_comic[0]["fields"]["title"], "Comic Canvas App")

        # Query non-matching
        resp_none = self.client.get(url, {"title": "NonExistentTermXYZ"})
        self.assertEqual(resp_none.json(), [])

    # 2. create_project_ajax tests
    def test_create_project_ajax_superuser_receives_201_and_pk(self):
        self.client.login(username="ajax_admin", password="AdminPassword123!")
        url = reverse("main:create_project_ajax")
        payload = {
            "title": "Quantum Leap Simulation",
            "description": "Simulasi komputasi kuantum dalam peramban web.",
            "tech_stack": "Python, Qiskit, WebAssembly",
            "project_url": "https://github.com/adamwsyaputra/quantum",
            "project_image_url": "https://example.com/quantum.png",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response["Content-Type"].startswith("application/json"))

        data = response.json()
        self.assertIn("message", data)
        self.assertIn("pk", data)

        created = Project.objects.get(id=data["pk"])
        self.assertEqual(created.title, "Quantum Leap Simulation")
        self.assertEqual(created.tech_stack, "Python, Qiskit, WebAssembly")

    def test_create_project_ajax_non_superuser_receives_403(self):
        url = reverse("main:create_project_ajax")
        payload = {
            "title": "Hacked Project",
            "description": "Attempt to bypass permission.",
            "tech_stack": "Malware",
        }

        # 1. Anonymous visitor
        anon_resp = self.client.post(url, payload)
        self.assertEqual(anon_resp.status_code, 403)
        self.assertIn("message", anon_resp.json())

        # 2. Regular user
        self.client.login(username="ajax_regular", password="RegularPassword123!")
        reg_resp = self.client.post(url, payload)
        self.assertEqual(reg_resp.status_code, 403)
        self.assertIn("message", reg_resp.json())

        # 3. Editor user (non-superuser)
        self.client.login(username="ajax_editor", password="EditorPassword123!")
        ed_resp = self.client.post(url, payload)
        self.assertEqual(ed_resp.status_code, 403)
        self.assertIn("message", ed_resp.json())

        # Confirm not created in database
        self.assertFalse(Project.objects.filter(title="Hacked Project").exists())

    def test_create_project_ajax_invalid_inputs_returns_400_with_errors(self):
        self.client.login(username="ajax_admin", password="AdminPassword123!")
        url = reverse("main:create_project_ajax")

        # Empty required fields
        payload = {
            "title": "",
            "description": "",
            "tech_stack": "",
            "project_url": "not-a-valid-url",
            "project_image_url": "not-a-valid-url",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response["Content-Type"].startswith("application/json"))

        data = response.json()
        self.assertIn("errors", data)
        self.assertIn("title", data["errors"])
        self.assertIn("description", data["errors"])
        self.assertIn("tech_stack", data["errors"])

    def test_create_project_ajax_cleanses_xss_inputs(self):
        self.client.login(username="ajax_admin", password="AdminPassword123!")
        url = reverse("main:create_project_ajax")
        payload = {
            "title": "<script>alert('pwned')</script>Cleaned Title",
            "description": "<div>Safe description text.</div>",
            "tech_stack": "<b>Django</b>, <i>AJAX</i>",
            "project_url": "https://github.com/safe",
            "project_image_url": "",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)

        data = response.json()
        saved = Project.objects.get(id=data["pk"])
        self.assertEqual(saved.title, "alert('pwned')Cleaned Title")
        self.assertEqual(saved.description, "Safe description text.")
        self.assertEqual(saved.tech_stack, "Django, AJAX")





