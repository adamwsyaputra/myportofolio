import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project, Skill


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="test-password",
            email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio",
            description="My website",
            tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project",
            "description": "A useful app",
            "tech_stack": "Python",
            "project_url": "https://example.com/",
            "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": " "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")

        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by_names": "forged",
                "starred_by": [self.visitor.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SkillAPITest(APITestCase):
    """Comprehensive API tests for the Skill portfolio section across all 4 RBAC tiers."""

    def setUp(self):
        self.editor_group = Group.objects.create(name="Editor")
        self.owner = User.objects.create_superuser(
            username="skill_owner",
            password="test-password",
            email="owner@example.com",
        )
        self.editor = User.objects.create_user(
            username="skill_editor",
            password="test-password",
        )
        self.editor.groups.add(self.editor_group)
        self.visitor = User.objects.create_user(
            username="skill_visitor",
            password="test-password",
        )
        self.skill = Skill.objects.create(
            name="Python",
            category="languages",
            proficiency_percent=90,
            is_core=True,
            logo_url="https://example.com/python.png",
        )
        self.list_url = reverse("api:skill-list")
        self.detail_url = reverse("api:skill-detail", args=[self.skill.id])
        self.star_url = reverse("api:skill-star", args=[self.skill.id])
        self.payload = {
            "name": "Django REST Framework",
            "category": "frameworks",
            "proficiency_percent": 85,
            "is_core": True,
            "logo_url": "https://example.com/drf.png",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.skill.id))
        self.assertEqual(response.data[0]["name"], "Python")
        self.assertEqual(response.data[0]["category_display"], "Programming Languages")
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])

        detail_resp = self.client.get(self.detail_url)
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data["name"], "Python")

    def test_search_and_category_filtering(self):
        Skill.objects.create(
            name="Docker",
            category="systems",
            proficiency_percent=80,
            is_core=False,
        )
        # Search by query 'q'
        res_q = self.client.get(self.list_url, {"q": "pyth"})
        self.assertEqual(len(res_q.data), 1)
        self.assertEqual(res_q.data[0]["name"], "Python")

        # Filter by category
        res_cat = self.client.get(self.list_url, {"category": "systems"})
        self.assertEqual(len(res_cat.data), 1)
        self.assertEqual(res_cat.data[0]["name"], "Docker")

        # Non-matching search
        res_empty = self.client.get(self.list_url, {"q": "non-existent-skill"})
        self.assertEqual(res_empty.data, [])

    def test_missing_skill_returns_404(self):
        url = reverse("api:skill-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_regular_user_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(self.detail_url, {"name": "Hacked"}, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.put(self.detail_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        # Verify database state remained intact
        self.assertEqual(Skill.objects.count(), 1)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python")

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        # Editor cannot POST create
        create_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Skill.objects.count(), 1)

        # Editor can PATCH update
        patch_resp = self.client.patch(
            self.detail_url,
            {"name": "Python 3.12", "proficiency_percent": 95},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python 3.12")
        self.assertEqual(self.skill.proficiency_percent, 95)

        # Editor can PUT update
        put_resp = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Django REST Framework")

        # Editor cannot DELETE
        del_resp = self.client.delete(self.detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Skill.objects.filter(pk=self.skill.id).exists())

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        # Create
        create_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Skill.objects.filter(pk=create_resp.data["id"]).exists())

        # Patch
        patch_resp = self.client.patch(
            self.detail_url,
            {"name": "Advanced Python"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Advanced Python")

        # Delete
        del_resp = self.client.delete(self.detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(del_resp.content, b"")
        self.assertFalse(Skill.objects.filter(pk=self.skill.id).exists())

    def test_skill_input_validation_and_xss_stripping(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"name": "   "}, "name"),
            ({"name": '<img src="x" onerror="alert(1)">'}, "name"),
            ({"proficiency_percent": -5}, "proficiency_percent"),
            ({"proficiency_percent": 105}, "proficiency_percent"),
            ({"logo_url": "javascript:alert(1)"}, "logo_url"),
        ]:
            resp = self.client.post(
                self.list_url,
                {**self.payload, **changes},
                format="json",
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, resp.data)
        self.assertEqual(Skill.objects.count(), 1)

        # Verify HTML tags are stripped when text remains
        clean_resp = self.client.post(
            self.list_url,
            {**self.payload, "name": "<b>Rust</b>"},
            format="json",
        )
        self.assertEqual(clean_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(clean_resp.data["name"], "Rust")

    def test_star_requires_login_and_toggles(self):
        # Anonymous visitor rejected
        anon_resp = self.client.post(self.star_url)
        self.assertEqual(anon_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.skill.starred_by.count(), 0)

        # Regular user toggles star on and off
        self.client.force_authenticate(user=self.visitor)
        resp1 = self.client.post(self.star_url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertTrue(resp1.data["is_starred"])
        self.assertEqual(resp1.data["star_count"], 1)
        self.assertIn("skill_visitor", resp1.data["starred_by_names"])

        resp2 = self.client.post(self.star_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertFalse(resp2.data["is_starred"])
        self.assertEqual(resp2.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by_names": "forged",
                "starred_by": [self.visitor.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_wrong_method_returns_405(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.get(self.star_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_write_without_csrf_is_rejected_and_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="skill_editor", password="test-password"))

        # Editor PATCH without CSRF token is rejected (403)
        rejected = client.patch(
            self.detail_url,
            {"name": "CSRF Bypass Attempt"},
            format="json",
        )
        self.assertEqual(rejected.status_code, status.HTTP_403_FORBIDDEN)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python")

        # Obtain CSRF cookie and retry with X-CSRFToken
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        accepted = client.patch(
            self.detail_url,
            {"name": "Python Verified"},
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(accepted.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python Verified")


class ExperienceAPITest(APITestCase):
    """Comprehensive API tests for the Experience portfolio section across all 4 RBAC tiers."""

    def setUp(self):
        self.editor_group = Group.objects.create(name="Editor")
        self.owner = User.objects.create_superuser(
            username="exp_owner",
            password="test-password",
            email="exp_owner@example.com",
        )
        self.editor = User.objects.create_user(
            username="exp_editor",
            password="test-password",
        )
        self.editor.groups.add(self.editor_group)
        self.visitor = User.objects.create_user(
            username="exp_visitor",
            password="test-password",
        )
        self.experience = Experience.objects.create(
            title="Software Engineer Intern",
            description="Built backend microservices in Python.",
            category="internship",
            thumbnail="https://example.com/intern.png",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.vouch_url = reverse("api:experience-vouch", args=[self.experience.id])
        self.payload = {
            "title": "Security Researcher",
            "description": "Conducted vulnerability assessments.",
            "category": "research",
            "thumbnail": "https://example.com/research.png",
            "is_ongoing": False,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertEqual(response.data[0]["title"], "Software Engineer Intern")
        self.assertEqual(response.data[0]["category_display"], "Internship")
        self.assertTrue(response.data[0]["is_ongoing"])
        self.assertFalse(response.data[0]["is_vouched"])
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])

        detail_resp = self.client.get(self.detail_url)
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data["title"], "Software Engineer Intern")

    def test_search_and_category_filtering(self):
        Experience.objects.create(
            title="Teaching Assistant",
            description="Assisted in Platform-Based Programming course.",
            category="part-time",
        )
        # Search by query 'q'
        res_q = self.client.get(self.list_url, {"q": "Teaching"})
        self.assertEqual(len(res_q.data), 1)
        self.assertEqual(res_q.data[0]["title"], "Teaching Assistant")

        # Filter by category
        res_cat = self.client.get(self.list_url, {"category": "internship"})
        self.assertEqual(len(res_cat.data), 1)
        self.assertEqual(res_cat.data[0]["title"], "Software Engineer Intern")

        # Non-matching query
        res_empty = self.client.get(self.list_url, {"q": "non-existent-role"})
        self.assertEqual(res_empty.data, [])

    def test_missing_experience_returns_404(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_regular_user_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(self.detail_url, {"title": "Hacked"}, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.put(self.detail_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Software Engineer Intern")

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        # Editor cannot POST create
        create_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

        # Editor can PATCH update (including toggling is_ongoing to False)
        patch_resp = self.client.patch(
            self.detail_url,
            {"title": "Senior SWE Intern", "is_ongoing": False},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Senior SWE Intern")
        self.assertIsNotNone(self.experience.ended_at)
        self.assertFalse(self.experience.is_ongoing)

        # Editor can PATCH is_ongoing back to True
        patch_ongoing = self.client.patch(
            self.detail_url,
            {"is_ongoing": True},
            format="json",
        )
        self.assertEqual(patch_ongoing.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)
        self.assertTrue(self.experience.is_ongoing)

        # Editor cannot DELETE
        del_resp = self.client.delete(self.detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        # Create completed experience (is_ongoing=False sets ended_at)
        create_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created_exp = Experience.objects.get(pk=create_resp.data["id"])
        self.assertIsNotNone(created_exp.ended_at)

        # Delete
        del_resp = self.client.delete(self.detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(del_resp.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_experience_validation_and_xss_stripping(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "   "}, "description"),
            ({"description": "<b>   </b>"}, "description"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
        ]:
            resp = self.client.post(
                self.list_url,
                {**self.payload, **changes},
                format="json",
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, resp.data)
        self.assertEqual(Experience.objects.count(), 1)

        # Verify HTML tags are stripped when text remains
        clean_resp = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "<b>Lead Engineer</b>",
                "description": "<div>Architected core systems.</div>",
            },
            format="json",
        )
        self.assertEqual(clean_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(clean_resp.data["title"], "Lead Engineer")
        self.assertEqual(clean_resp.data["description"], "Architected core systems.")

    def test_vouch_requires_login_and_toggles(self):
        # Anonymous visitor rejected
        anon_resp = self.client.post(self.vouch_url)
        self.assertEqual(anon_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.vouched_by.count(), 0)

        # Authenticated user toggles vouch on and off
        self.client.force_authenticate(user=self.visitor)
        resp1 = self.client.post(self.vouch_url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertTrue(resp1.data["is_vouched"])
        self.assertTrue(resp1.data["is_starred"])
        self.assertEqual(resp1.data["vouch_count"], 1)
        self.assertEqual(resp1.data["star_count"], 1)
        self.assertIn("exp_visitor", resp1.data["vouched_by_names"])
        self.assertIn("exp_visitor", resp1.data["starred_by_names"])

        resp2 = self.client.post(self.vouch_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertFalse(resp2.data["is_vouched"])
        self.assertEqual(resp2.data["vouch_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "vouch_count": 99,
                "is_vouched": True,
                "vouched_by_names": "forged",
                "star_count": 99,
                "is_starred": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["vouch_count"], 0)
        self.assertFalse(response.data["is_vouched"])

    def test_session_write_without_csrf_is_rejected_and_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="exp_owner", password="test-password"))

        # POST without CSRF token is rejected (403)
        rejected = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(rejected.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

        # Obtain CSRF cookie and retry with X-CSRFToken
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        accepted = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(accepted.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experience.objects.count(), 2)
