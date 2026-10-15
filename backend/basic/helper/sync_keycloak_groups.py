from keycloak import KeycloakGetError

from backend.settings import keycloak_admin
from basic.models import ScoutHierarchy
from keycloak_auth.helper import get_or_create_keycloak_model
from keycloak_auth.models import KeycloakGroup


class SyncKeycloakGroups:

    def __init__(self):
        self.groups = {}
        self.groups_added = []
        self.groups_deleted = []

    def run(self):  # noqa: C901
        print('checking django groups')  # noqa: T201
        all_django_groups = KeycloakGroup.objects.all()
        for group in all_django_groups:
            name = self.generate_name(group)
            self.groups[name] = False

        print('checking keycloak groups')  # noqa: T201
        all_groups = keycloak_admin.get_groups()
        for group in all_groups:
            self.get_subgroup(group)

        print('Checking diff')  # noqa: T201
        for group in self.groups:
            if not self.groups[group]:
                self.groups_deleted.append(group)

        if self.groups_added:
            print('')  # noqa: T201
            print('added groups:')  # noqa: T201
            for group in self.groups_added:
                print(group)  # noqa: T201

        if self.groups_deleted:
            print('')  # noqa: T201
            print('groups to be deleted:')  # noqa: T201
            for group in self.groups_deleted:
                print(group)  # noqa: T201

        print('Assign KeycloakGroup to ScoutHierarchies')  # noqa: T201
        for scout_hierarchy in ScoutHierarchy.objects.all():
            if not scout_hierarchy.keycloak:
                keycloak_group = None
                try:
                    keycloak_group: dict = keycloak_admin.get_group_by_path(
                        path=scout_hierarchy.keycloak_group_name,
                        search_in_subgroups=True
                    )
                except (KeycloakGetError, KeyError):
                    pass
                if keycloak_group:
                    django_keycloak_group = KeycloakGroup.objects.get(keycloak_id=keycloak_group['id'])
                    scout_hierarchy.keycloak = django_keycloak_group
                    scout_hierarchy.save()
            if scout_hierarchy.keycloak and not scout_hierarchy.keycloak.membership_allowed:
                scout_hierarchy.keycloak.membership_allowed = True
                scout_hierarchy.keycloak.save()

        print('')  # noqa: T201
        print('Checks finished')  # noqa: T201
        if not self.groups_added and not self.groups_deleted:
            print('All fine')  # noqa: T201

    def get_subgroup(self, group, parent: KeycloakGroup = None):
        keycloak_group, created = get_or_create_keycloak_model(group, parent)
        if created:
            self.groups_added.append(self.generate_name(keycloak_group))

        if keycloak_group.name != group['name']:
            keycloak_group.name = group['name']
            keycloak_group.save()

        if keycloak_group.parent is None or keycloak_group.parent != parent:
            keycloak_group.parent = parent
            keycloak_group.save()

        name = self.generate_name(keycloak_group)
        self.groups[name] = True

        for sub_group in keycloak_admin.get_child_groups(group):
            self.get_subgroup(sub_group, keycloak_group)

    def generate_name(self, group: KeycloakGroup):
        parents = []
        iterator: KeycloakGroup = group
        while iterator:
            parents.append(iterator.name)
            iterator = iterator.parent
        parents.reverse()
        name = '_'.join(parents)
        return name
