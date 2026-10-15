"""Tests für die Gruppenverwaltung (Phase 2: Rechte im Tool statt in Keycloak).

Regeln:
- Verwalten (aufnehmen, entfernen, Anfragen entscheiden, umbenennen) nur mit
  Admin-Recht auf die Gruppe. Löschen nur mit Admin-Recht auf die Obergruppe.
- Admin-Recht kommt direkt (Person) oder über eine Führungsgruppe
  (z. B. "Stammesführung") und gilt auch für alle Untergruppen.
- Ein normales Mitglied darf nur selbst austreten und Beitritt anfragen.
- Über die eigene Beitrittsanfrage entscheidet nie man selbst.
- Ist Keycloak nicht erreichbar, gelten nur direkt vergebene Rechte.
"""
import pytest
from keycloak.exceptions import KeycloakConnectionError

from authentication.choices import RequestGroupAccessChoices
from authentication.models import RequestGroupAccess
from basic.helper.initialize_keycloak_scout_hierarchies import grant_hierarchy_permissions
from basic.models import ScoutHierarchy
from keycloak_auth.access import grant, group_role
from keycloak_auth.models import GroupPermission, KeycloakGroup

pytestmark = pytest.mark.django_db

ADMIN = GroupPermission.Role.ADMIN
VIEW = GroupPermission.Role.VIEW

BUND_ID = '00000000-0000-0000-0000-0000000b0000'
STAMM_ID = '00000000-0000-0000-0000-0000000a0000'
FUEHRUNG_ID = '00000000-0000-0000-0000-0000000af000'


class KeycloakSpielwiese:
    """Spielt die Teile der Keycloak-Admin-API nach, die die Gruppenverwaltung braucht."""

    def __init__(self, fake):
        self.fake = fake
        self.calls = []
        self.members: dict[str, set[str]] = {}
        fake.get_user_groups = self.get_user_groups
        fake.get_group_members = self.get_group_members
        fake.group_user_add = self.group_user_add
        fake.group_user_remove = self.group_user_remove
        fake.get_group = lambda group_id: {'id': group_id, 'name': self._name(group_id), 'path': self._path(group_id)}
        fake.delete_group = lambda group_id: self.calls.append(('delete', group_id))

    def _name(self, group_id):
        group = KeycloakGroup.objects.filter(keycloak_id=group_id).first()
        return group.name if group else 'neu'

    def _path(self, group_id):
        group = KeycloakGroup.objects.filter(keycloak_id=group_id).first()
        return group.keycloak_group_name if group else '/neu'

    def get_user_groups(self, user_id, brief_representation=True, **kwargs):
        return [{'id': g} for g, users in self.members.items() if user_id in users]

    def get_group_members(self, group_id, query=None):
        return [{'id': u, 'enabled': True} for u in self.members.get(group_id, set())]

    def group_user_add(self, user_id, group_id):
        self.calls.append(('add', user_id, group_id))
        self.members.setdefault(group_id, set()).add(user_id)

    def group_user_remove(self, user_id, group_id):
        self.calls.append(('remove', user_id, group_id))
        self.members.get(group_id, set()).discard(user_id)

    def make_member(self, user, group):
        self.members.setdefault(group.keycloak_id, set()).add(user.keycloak_id)


def existing_group(keycloak_id, name, parent=None):
    # bulk_create umgeht das Speichersignal: Gruppe gilt als bereits in Keycloak vorhanden
    (group,) = KeycloakGroup.objects.bulk_create([KeycloakGroup(keycloak_id=keycloak_id, name=name, parent=parent)])
    return group


@pytest.fixture
def keycloak(fake_keycloak):
    return KeycloakSpielwiese(fake_keycloak)


@pytest.fixture
def bund(db):
    return existing_group(BUND_ID, 'Nordlicht')


@pytest.fixture
def stamm(bund):
    return existing_group(STAMM_ID, 'Adler', parent=bund)


@pytest.fixture
def stammesfuehrung(stamm):
    return existing_group(FUEHRUNG_ID, 'Stammesführung', parent=stamm)


@pytest.fixture
def stammesleitung(anmeldende_leitung, stamm, stammesfuehrung, keycloak):
    """Mitglied der Stammesführung, die den Stamm verwaltet."""
    grant(stamm, ADMIN, via_group=stammesfuehrung)
    keycloak.make_member(anmeldende_leitung, stammesfuehrung)
    return anmeldende_leitung


def url(group_id, suffix=''):
    return f'/keycloak/group/{group_id}/{suffix}'


# --- Wer darf verwalten -------------------------------------------------------

class TestOhneRechte:

    def test_kann_niemanden_aufnehmen(self, api, teilnehmer, fremde_leitung, stamm, keycloak):
        response = api(teilnehmer).post(url(STAMM_ID, 'invite/'), {'userId': fremde_leitung.keycloak_id}, format='json')
        assert response.status_code == 403
        assert keycloak.calls == []

    def test_kann_niemanden_entfernen(self, api, teilnehmer, fremde_leitung, stamm, keycloak):
        response = api(teilnehmer).post(url(STAMM_ID, 'kick/'), {'userId': fremde_leitung.keycloak_id}, format='json')
        assert response.status_code == 403
        assert keycloak.calls == []

    def test_kann_gruppe_nicht_loeschen(self, api, teilnehmer, stamm, keycloak):
        assert api(teilnehmer).delete(url(STAMM_ID)).status_code == 403
        assert KeycloakGroup.objects.filter(keycloak_id=STAMM_ID).exists()

    def test_kann_gruppe_nicht_umbenennen(self, api, teilnehmer, stamm, keycloak):
        assert api(teilnehmer).put(url(STAMM_ID), {'name': 'Gekapert'}, format='json').status_code == 403
        stamm.refresh_from_db()
        assert stamm.name == 'Adler'

    def test_sieht_keine_beitrittsanfragen(self, api, teilnehmer, stamm, keycloak):
        assert api(teilnehmer).get(url(STAMM_ID, 'requests/')).status_code == 403

    def test_kann_alle_mitglieder_nicht_durchsuchen(self, api, teilnehmer, keycloak):
        assert api(teilnehmer).get('/keycloak/members/?search=Kim').status_code == 403

    def test_mitglied_kann_selbst_austreten(self, api, teilnehmer, stamm, keycloak):
        keycloak.make_member(teilnehmer, stamm)
        assert api(teilnehmer).post(url(STAMM_ID, 'leave/'), {}, format='json').status_code == 200
        assert keycloak.calls == [('remove', teilnehmer.keycloak_id, STAMM_ID)]


class TestStammesleitung:

    def test_kann_aufnehmen(self, api, stammesleitung, teilnehmer, stamm, keycloak):
        response = api(stammesleitung).post(url(STAMM_ID, 'invite/'), {'userId': teilnehmer.keycloak_id}, format='json')
        assert response.status_code == 200
        assert ('add', teilnehmer.keycloak_id, STAMM_ID) in keycloak.calls

    def test_kann_entfernen(self, api, stammesleitung, teilnehmer, stamm, keycloak):
        keycloak.make_member(teilnehmer, stamm)
        response = api(stammesleitung).post(url(STAMM_ID, 'kick/'), {'userId': teilnehmer.keycloak_id}, format='json')
        assert response.status_code == 200
        assert ('remove', teilnehmer.keycloak_id, STAMM_ID) in keycloak.calls

    def test_aufnahme_unbekannter_person_aendert_nichts(self, api, stammesleitung, stamm, keycloak):
        response = api(stammesleitung).post(url(STAMM_ID, 'invite/'), {'userId': 'gibt-es-nicht'}, format='json')
        assert response.status_code == 404
        assert keycloak.calls == []

    def test_verwaltet_auch_untergruppen(self, api, stammesleitung, teilnehmer, stamm, keycloak):
        sippe = existing_group('00000000-0000-0000-0000-0000000a5100', 'Sippe Fuchs', parent=stamm)
        response = api(stammesleitung).post(
            url(sippe.keycloak_id, 'invite/'), {'userId': teilnehmer.keycloak_id}, format='json')
        assert response.status_code == 200

    def test_verwaltet_nicht_den_bund_darueber(self, api, stammesleitung, teilnehmer, bund, keycloak):
        response = api(stammesleitung).post(url(BUND_ID, 'invite/'), {'userId': teilnehmer.keycloak_id}, format='json')
        assert response.status_code == 403

    def test_kann_eigenen_stamm_nicht_loeschen(self, api, stammesleitung, stamm, keycloak):
        # Löschen wirkt bis ins Verbands-Keycloak: dafür braucht es Rechte auf die Obergruppe
        assert api(stammesleitung).delete(url(STAMM_ID)).status_code == 403

    def test_gruppe_zeigt_administrator(self, api, stammesleitung, stamm, keycloak):
        response = api(stammesleitung).get(url(STAMM_ID))
        assert response.status_code == 200
        assert response.json()['permission'] == 'Administrator'

    def test_meine_rechte(self, api, stammesleitung, stamm, keycloak):
        response = api(stammesleitung).get('/auth/my-permissions/')
        assert response.status_code == 200
        assert response.json() == [f'group-{STAMM_ID}-admin-role']


class TestBundesleitung:

    def test_kann_stamm_im_bund_loeschen(self, api, fremde_leitung, bund, stamm, keycloak):
        grant(bund, ADMIN, user=fremde_leitung)
        assert api(fremde_leitung).delete(url(STAMM_ID)).status_code == 204
        assert not KeycloakGroup.objects.filter(keycloak_id=STAMM_ID).exists()


# --- Beitrittsanfragen ---------------------------------------------------------

class TestBeitrittsanfragen:

    def anfrage(self, api, user):
        response = api(user).post(url(STAMM_ID, 'requests/'), {'applicationText': 'Hallo'}, format='json')
        assert response.status_code == 201, response.content
        return response.json()['id']

    def test_eigene_anfrage_nicht_selbst_annehmen(self, api, teilnehmer, stamm, stammesleitung, keycloak):
        request_id = self.anfrage(api, teilnehmer)
        response = api(teilnehmer).post(url(STAMM_ID, f'requests/{request_id}/accept/'), {}, format='json')
        assert response.status_code == 403
        assert ('add', teilnehmer.keycloak_id, STAMM_ID) not in keycloak.calls

    def test_leitung_nimmt_anfrage_an(self, api, teilnehmer, stamm, stammesleitung, keycloak):
        request_id = self.anfrage(api, teilnehmer)
        response = api(stammesleitung).post(url(STAMM_ID, f'requests/{request_id}/accept/'), {}, format='json')
        assert response.status_code == 200
        assert RequestGroupAccess.objects.get(id=request_id).status == RequestGroupAccessChoices.ACCEPTED
        assert ('add', teilnehmer.keycloak_id, STAMM_ID) in keycloak.calls

    def test_anfrage_nur_ueber_eigene_gruppe_entscheiden(self, api, teilnehmer, stamm, stammesleitung, keycloak):
        andere = existing_group('00000000-0000-0000-0000-0000000c0000', 'Falken')
        keycloak.fake.get_user_groups = keycloak.get_user_groups
        response = api(teilnehmer).post(
            url(andere.keycloak_id, 'requests/'), {'applicationText': 'Hallo'}, format='json')
        request_id = response.json()['id']
        # Stammesleitung der Adler versucht, über die Falken-Anfrage zu entscheiden
        response = api(stammesleitung).post(url(STAMM_ID, f'requests/{request_id}/accept/'), {}, format='json')
        assert response.status_code == 404

    def test_leitung_wird_benachrichtigt(self, api, teilnehmer, stamm, stammesleitung, keycloak):
        from notifications.models import Notification
        self.anfrage(api, teilnehmer)
        assert Notification.objects.filter(recipient=stammesleitung).exists()


# --- Rechte-Logik direkt ---------------------------------------------------------

class TestRechteLogik:

    def test_admin_schliesst_ansicht_ein(self, anmeldende_leitung, stamm):
        grant(stamm, ADMIN, user=anmeldende_leitung)
        assert group_role(anmeldende_leitung, stamm) == ADMIN

    def test_ohne_recht_none(self, teilnehmer, stamm, keycloak):
        assert group_role(teilnehmer, stamm) is None

    def test_staff_ist_ueberall_admin(self, teilnehmer, stamm):
        teilnehmer.is_staff = True
        assert group_role(teilnehmer, stamm) == ADMIN

    def test_keycloak_ausfall_nur_direkte_rechte(self, anmeldende_leitung, fremde_leitung, stamm, stammesfuehrung, fake_keycloak):
        grant(stamm, ADMIN, via_group=stammesfuehrung)
        grant(stamm, VIEW, user=fremde_leitung)

        def down(*args, **kwargs):
            raise KeycloakConnectionError('nicht erreichbar')
        fake_keycloak.get_user_groups = down

        assert group_role(anmeldende_leitung, stamm) is None
        assert group_role(fremde_leitung, stamm) == VIEW

    def test_keycloak_nur_gefragt_wenn_noetig(self, anmeldende_leitung, stamm, fake_keycloak):
        # Kein Recht hängt an einer Mitgliedschaft: FakeKeycloak darf nicht gefragt werden
        grant(stamm, ADMIN, user=anmeldende_leitung)
        assert group_role(anmeldende_leitung, stamm) == ADMIN

    def test_standardrechte_fuer_hierarchie(self, stamm_level, stamm, stammesfuehrung):
        ScoutHierarchy.objects.create(name='Adler', level=stamm_level, level_choice='Stamm', keycloak=stamm)
        assert grant_hierarchy_permissions() == 2
        assert GroupPermission.objects.filter(group=stamm, role=ADMIN, via_group=stammesfuehrung).exists()
        assert GroupPermission.objects.filter(group=stamm, role=VIEW, via_group=stamm).exists()
        assert grant_hierarchy_permissions() == 0


# --- Eigene Gruppen über /auth/my-groups/ (Qualität II, 1b-2) ------------------
# Die Liste der eigenen Gruppen erlaubte früher auch Ändern und Löschen, ohne die
# Regeln oben zu prüfen. Das Frontend liest dort nur.

class TestEigeneGruppenListe:

    @pytest.fixture
    def mitglied(self, teilnehmer, stamm, keycloak):
        keycloak.make_member(teilnehmer, stamm)
        return teilnehmer

    def test_mitglied_sieht_eigene_gruppe(self, api, mitglied, stamm):
        response = api(mitglied).get('/auth/my-groups/')
        assert response.status_code == 200
        assert STAMM_ID in [group['id'] for group in response.json()]

    def test_mitglied_loescht_eigene_gruppe_nicht(self, api, mitglied, stamm, keycloak):
        api(mitglied).delete(f'/auth/my-groups/{stamm.id}/')
        assert KeycloakGroup.objects.filter(keycloak_id=STAMM_ID).exists()
        assert keycloak.calls == []

    def test_mitglied_benennt_eigene_gruppe_nicht_um(self, api, mitglied, stamm):
        api(mitglied).patch(f'/auth/my-groups/{stamm.id}/', {'name': 'Gekapert'}, format='json')
        stamm.refresh_from_db()
        assert stamm.name == 'Adler'
