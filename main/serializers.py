from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project, Skill


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the Project model with computed read-only star metadata."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for the Skill model with XSS sanitization and computed star/endorse fields."""

    category_display = serializers.SerializerMethodField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "category",
            "category_display",
            "proficiency_percent",
            "is_core",
            "logo_url",
            "created_at",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Skill name cannot be empty.")
        return value

    def validate_proficiency_percent(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Proficiency percent must be between 0 and 100.")
        return value

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for the Experience model with ongoing state handling and vouch/star metadata."""

    category_display = serializers.SerializerMethodField()
    is_ongoing = serializers.BooleanField(required=False, default=True)
    vouch_count = serializers.SerializerMethodField()
    is_vouched = serializers.SerializerMethodField()
    vouched_by_names = serializers.SerializerMethodField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_display",
            "thumbnail",
            "started_at",
            "ended_at",
            "is_ongoing",
            "vouch_count",
            "is_vouched",
            "vouched_by_names",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id", "started_at", "ended_at"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Experience title cannot be empty.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        return value

    def _apply_ongoing_state(self, validated_data, instance=None):
        if "is_ongoing" in validated_data:
            is_ongoing = validated_data.pop("is_ongoing")
            if is_ongoing:
                validated_data["ended_at"] = None
            elif instance is None or instance.ended_at is None:
                validated_data["ended_at"] = timezone.now()

    def create(self, validated_data):
        self._apply_ongoing_state(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._apply_ongoing_state(validated_data, instance=instance)
        return super().update(instance, validated_data)

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_vouch_count(self, obj):
        return obj.vouched_by.count()

    def get_is_vouched(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.vouched_by.all()

    def get_vouched_by_names(self, obj):
        return ", ".join(user.username for user in obj.vouched_by.all())

    def get_star_count(self, obj):
        return obj.vouched_by.count()

    def get_is_starred(self, obj):
        return self.get_is_vouched(obj)

    def get_starred_by_names(self, obj):
        return self.get_vouched_by_names(obj)
