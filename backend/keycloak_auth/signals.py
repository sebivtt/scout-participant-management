from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from keycloak import KeycloakGetError

from backend.settings import keycloak_admin
from keycloak_auth.api_exceptions import NoKeycloakId
from keycloak_auth.models import KeycloakGroup


@receiver(post_save, sender=KeycloakGroup, dispatch_uid='post_save_keycloak_group')
def post_save_keycloak_group(sender: KeycloakGroup, instance: KeycloakGroup, created: bool, **kwargs):
    payload = {'name': instance.name}

    if not instance.keycloak_id:
        if instance.parent:
            if not instance.parent.keycloak_id:
                raise NoKeycloakId(instance.parent.name)
            new_group_id = keycloak_admin.create_group(payload=payload, parent=instance.parent.keycloak_id)
        else:
            new_group_id = keycloak_admin.create_group(payload=payload)
        instance.keycloak_id = new_group_id
        instance.save()
    else:
        group = keycloak_admin.get_group(instance.keycloak_id)

        if instance.name != group['name']:
            keycloak_admin.rename_group(instance.keycloak_id, instance.name)
        if instance.parent and instance.keycloak_group_name != group['path']:
            keycloak_admin.move_group(instance.keycloak_id, instance.name, parent=instance.parent.keycloak_id)


@receiver(post_delete, sender=KeycloakGroup, dispatch_uid='post_delete_keycloak_group')
def post_delete_keycloak_group(sender: KeycloakGroup, instance: KeycloakGroup, **kwargs):
    if instance.keycloak_id:
        try:
            group = keycloak_admin.get_group(instance.keycloak_id)
            if group['name'] == instance.name:
                keycloak_admin.delete_group(instance.keycloak_id)
        except KeycloakGetError:
            pass
