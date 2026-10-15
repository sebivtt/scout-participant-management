import uuid
from django.db import models


class KeycloakGroup(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    keycloak_id = models.CharField(max_length=36, unique=True, blank=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='keycloak_group', blank=True)
    membership_allowed = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    @property
    def children(self):
        return KeycloakGroup.objects.filter(parent=self.id)

    @property
    def keycloak_group_name(self) -> str:
        if self.parent:
            return f'{self.parent.keycloak_group_name}/{self.name}'
        else:
            return f'/{self.name}'

    def __generate_tree_name(self) -> str:
        name = self.name.lower()

        if self.parent:
            return f'{self.parent.__generate_tree_name()}_{name}'
        else:
            return name

    @property
    def keycloak_role_name(self) -> str:
        return f'{self.__generate_tree_name()}'

    def __str__(self):
        if self.parent:
            return f"{self.name} ({self.parent.name})"
        return f"{self.name}"

class GroupPermission(models.Model):
    """Wer darf eine Gruppe verwalten (admin) oder einsehen (view)?

    Ein Recht gilt entweder für eine einzelne Person (user) oder für alle
    Mitglieder einer anderen Gruppe (via_group), z. B. "Mitglieder der Gruppe
    Stammesführung verwalten den Stamm". Rechte gelten auch für alle
    Untergruppen. Admin schließt Ansicht ein.

    Ersetzt die früheren Client-Rollen "group-<id>-admin-role" in Keycloak,
    die die veraltete Keycloak-Funktion admin-fine-grained-authz:v1 brauchten.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        VIEW = 'view', 'Ansicht'

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(KeycloakGroup, on_delete=models.CASCADE, related_name='permissions')
    role = models.CharField(max_length=10, choices=Role.choices)
    user = models.ForeignKey(
        'authentication.CustomUser', null=True, blank=True, on_delete=models.CASCADE, related_name='group_permissions'
    )
    via_group = models.ForeignKey(
        KeycloakGroup, null=True, blank=True, on_delete=models.CASCADE, related_name='granted_permissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gruppenrecht'
        verbose_name_plural = 'Gruppenrechte'
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, via_group__isnull=True)
                    | models.Q(user__isnull=True, via_group__isnull=False)
                ),
                name='grouppermission_user_xor_via_group',
            ),
            models.UniqueConstraint(fields=['group', 'role', 'user'], name='grouppermission_unique_user'),
            models.UniqueConstraint(fields=['group', 'role', 'via_group'], name='grouppermission_unique_via_group'),
        ]

    def __str__(self):
        holder = self.user or f'Mitglieder von {self.via_group}'
        return f'{holder}: {self.get_role_display()} für {self.group}'


class ExternalLinks(models.Model):
    id = models.AutoField(primary_key=True)
    wiki = models.URLField(blank=True, null=True)
    cloud = models.URLField(blank=True, null=True)
    keycloak_group = models.OneToOneField(KeycloakGroup, on_delete=models.CASCADE)

    def __str__(self):
        return self.keycloak_group.name
