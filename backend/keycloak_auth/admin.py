from django.contrib import admin

from .models import KeycloakGroup, ExternalLinks, GroupPermission


@admin.register(KeycloakGroup)
class RequestGroupAccessAdmin(admin.ModelAdmin):
    autocomplete_fields = ('parent',)
    search_fields = ('name', 'keycloak_id', 'id')
    ordering = ('name',)


@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'role', 'user', 'via_group', 'created_at')
    list_filter = ('role',)
    autocomplete_fields = ('group', 'user', 'via_group')
    search_fields = ('group__name', 'user__username', 'user__email', 'via_group__name')


@admin.register(ExternalLinks)
class ExternalLinksAdmin(admin.ModelAdmin):
    autocomplete_fields = ('keycloak_group',)
    search_fields = ('keycloak_group__name', 'keycloak_group__keycloak_id')
