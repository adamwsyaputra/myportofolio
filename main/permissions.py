from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Allow read-only access to anyone; write access restricted to the portfolio owner (superuser)."""

    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """
    Enforce 4-Tier RBAC for portfolio sections:
    - Anonymous & Regular users: SAFE_METHODS only (GET, HEAD, OPTIONS).
    - Editor group members: SAFE_METHODS plus PUT and PATCH updates.
    - Portfolio Owner (superuser): Full access including POST creation and DELETE.
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )
