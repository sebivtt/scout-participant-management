import json
from urllib import request

from django.core.management.base import BaseCommand

from basic.choices import StateChoices
from basic.models import ZipCode

choices = dict(StateChoices.choices)
get_abbr = lambda state: [abbreviation for abbreviation, name in choices.items() if name == state]


class Command(BaseCommand):
    """Ergänzt bei allen Postleitzahlen das Bundesland über den öffentlichen Dienst opendatasoft.

    Stellt eine Anfrage pro Postleitzahl, braucht also Internetzugang und bei
    allen deutschen Postleitzahlen entsprechend lange.
    """

    help = 'Ergänzt das Bundesland bei allen Postleitzahlen (Internetzugang nötig)'

    def handle(self, *args, **options):
        """Fragt für jede Postleitzahl das Bundesland ab und speichert es."""
        zip_codes = ZipCode.objects.all()
        for zip_code in zip_codes:
            api_url = f'https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-germany-postleitzahl&q={zip_code.zip_code}&facet=lan_name'
            # Ohne eigenen Kontext prüft Python das Zertifikat. Die frühere Abschaltung
            # der Prüfung hätte gefälschte Antworten in die Datenbank gelassen.
            contents = request.urlopen(api_url).read()
            result_json = json.loads(contents)
            state = result_json['facet_groups'][0]['facets'][0]['name']

            abbreviation = get_abbr(state)[0]
            zip_code.state = StateChoices[abbreviation]
            zip_code.save()
