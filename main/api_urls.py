from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("projects/", api_views.project_list, name="project-list"),
    path("projects/<uuid:project_id>/", api_views.project_detail, name="project-detail"),
    path("projects/<uuid:project_id>/star/", api_views.project_star, name="project-star"),
    path("skills/", api_views.skill_list, name="skill-list"),
    path("skills/<uuid:skill_id>/", api_views.skill_detail, name="skill-detail"),
    path("skills/<uuid:skill_id>/star/", api_views.skill_star, name="skill-star"),
    path("experience/", api_views.experience_list, name="experience-list"),
    path("experience/<uuid:experience_id>/", api_views.experience_detail, name="experience-detail"),
    path("experience/<uuid:experience_id>/vouch/", api_views.experience_vouch, name="experience-vouch"),
    path("experience/<uuid:experience_id>/star/", api_views.experience_vouch, name="experience-star"),
]
