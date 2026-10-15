from celery import shared_task

from keycloak_auth.access import users_with_admin
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from keycloak import KeycloakPutError
from notifications.signals import notify

from backend.settings import keycloak_admin
from .api_exceptions import KeycloakError
from .choices import RequestGroupAccessChoices
from .models import CustomUser, RequestGroupAccess, Person

User: CustomUser = get_user_model()

logger = get_task_logger(__name__)


# @receiver(pre_delete, sender=CustomUser, dispatch_uid='pre_delete_user')
# def pre_delete_user(sender, instance: CustomUser, **kwargs):
#     try:
#         instance.person.delete()
#     except:
#         pass
#     try:
#         delete_keycloak_user_async.delay(instance.keycloak_id, instance.username)
#     except:
#         pass


# @shared_task
# def delete_keycloak_user_async(keycloak_id, username):
# if keycloak_id:
#     try:
#         keycloak_user = keycloak_admin.get_user(keycloak_id)
#
#         if keycloak_user['username'] == username:
#             keycloak_admin.delete_user(keycloak_id)
#         else:
#             print('shit')
#
#     except KeycloakGetError:
#         pass


# @receiver(post_save, sender=CustomUser, dispatch_uid='post_save_user')
# def post_save_user(sender, instance: CustomUser, created, **kwargs):
#     if not created:
#         save_keycloak_user(instance)


# @receiver(post_save, sender=Person, dispatch_uid='post_save_person')
# def post_save_person(sender, instance: Person, created, **kwargs):
#     if not created:
#         save_keycloak_person(instance)


# Felder, die Keycloak bei einer Aktualisierung mitgeschickt bekommen muss.
# Keycloak ab Version 24 behandelt eine Aktualisierung als vollständiges
# Profil: Was fehlt, wird gelöscht. Früher gingen so E-Mail, Vor- und
# Nachname verloren, und die Person konnte sich danach nicht mehr anmelden.
_KEYCLOAK_PROFILE_FIELDS = ('username', 'email', 'firstName', 'lastName', 'enabled', 'emailVerified')


def update_keycloak_profile(keycloak_id: str, fields: dict | None = None, attributes: dict | None = None) -> None:
    """Ändert einzelne Felder eines Keycloak-Kontos, ohne die übrigen zu verlieren.

    attributes: {name: wert}; ein leerer Wert entfernt das Attribut.
    """
    current = keycloak_admin.get_user(keycloak_id)
    payload = {key: current[key] for key in _KEYCLOAK_PROFILE_FIELDS if key in current}
    payload.update({key: value for key, value in (fields or {}).items() if value is not None})

    merged = dict(current.get('attributes') or {})
    for name, value in (attributes or {}).items():
        if value:
            merged[name] = [value]
        else:
            merged.pop(name, None)
    payload['attributes'] = merged

    try:
        keycloak_admin.update_user(keycloak_id, payload)
    except KeycloakPutError as exc:
        raise KeycloakError(exc.error_message)


def save_keycloak_user(instance: User):
    if not instance.keycloak_id:
        return
    keycloak_user = keycloak_admin.get_user(instance.keycloak_id)
    if keycloak_user['username'] != instance.username:
        return
    update_keycloak_profile(instance.keycloak_id, fields={
        'email': instance.email or None,
        'firstName': instance.first_name or None,
        'lastName': instance.last_name or None,
    })


def save_keycloak_person(instance: Person):
    if not instance.user or not instance.user.keycloak_id:
        return
    keycloak_user = keycloak_admin.get_user(instance.user.keycloak_id)
    if keycloak_user['username'] != instance.user.username:
        return

    attributes = {'fahrtenname': instance.scout_name}
    if instance.scout_group:
        attributes.update({
            'verband': instance.scout_group.verband,
            'bund': instance.scout_group.bund,
            'stamm': instance.scout_group.name,
        })
    update_keycloak_profile(instance.user.keycloak_id, attributes=attributes)


@receiver(post_save, sender=RequestGroupAccess, dispatch_uid='post_save_request_group_access')
def post_save_request_group_access(sender, instance: RequestGroupAccess, created, **kwargs):
    if not instance.pk or not instance.user:
        return

    if created:
        create_notification_async.delay(instance.id)
    else:
        move_user_into_group.delay(instance.id)


@shared_task
def move_user_into_group(instance_pk):
    instance = RequestGroupAccess.objects.get(id=instance_pk)

    in_group = False
    user_groups = keycloak_admin.get_user_groups(user_id=instance.user.keycloak_id)
    if any(d['id'] == instance.group.keycloak_id for d in user_groups):
        in_group = True
    decision = ''
    if instance.status == RequestGroupAccessChoices.ACCEPTED:
        if not in_group:
            keycloak_admin.group_user_add(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)
        decision = 'angenommen'
    elif instance.status == RequestGroupAccessChoices.DECLINED:
        if in_group:
            keycloak_admin.group_user_remove(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)
        decision = 'abgelehnt'

    notify.send(
        sender=instance.checked_by,
        recipient=instance.user,
        verb=f'Deine Gruppenanfrage wurde {decision}.',
        target=instance,
    )


@shared_task
def create_notification_async(instance_pk):
    instance = RequestGroupAccess.objects.get(id=instance_pk)
    recipients = User.objects.filter(pk__in=[user.pk for user in users_with_admin(instance.group)])
    if recipients.count() == 0:
        recipients = User.objects.filter(is_staff=True)
    notify.send(
        sender=instance.user,
        recipient=recipients,
        verb='Eine Person möchte gerne in eine Gruppe aufgenommen werden.',
        target=instance.group,
    )
