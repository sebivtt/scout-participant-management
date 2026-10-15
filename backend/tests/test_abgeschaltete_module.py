"""Essensplanung (food) und Programmideen (inspi) sind abgeschaltet.

Entscheidung vom 15.10.2026 (docs/entscheidungen.md): In beiden Modulen konnte
jede eingeloggte Person Einträge anderer ändern oder löschen. Bis ihre
Anforderungen abgestimmt sind, sind ihre Adressen nicht erreichbar. Code und
Datenbanktabellen bleiben erhalten.
"""
import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('path', [
    '/food/recipe/',
    '/food/meal-event/',
    '/inspi/activity/',
    '/inspi/tag/',
    '/inspi/experiment/',
])
def test_abgeschaltetes_modul_nicht_erreichbar(client, api, teilnehmer, path):
    assert client.get(path).status_code == 404
    assert api(teilnehmer).get(path).status_code == 404
    assert api(teilnehmer).post(path, {}, format='json').status_code == 404


def test_essensauswertung_der_veranstaltung_bleibt(api, veranstaltungsleitung, lager):
    # Liegt unter /event/ und nutzt nur Rechencode aus food, nicht dessen Adressen.
    assert api(veranstaltungsleitung).get(f'/event/event/{lager.id}/summary/food/').status_code == 200
