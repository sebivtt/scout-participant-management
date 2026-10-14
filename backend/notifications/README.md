# notifications

Übernommen aus [django-notifications-hq](https://github.com/django-notifications/django-notifications) 1.8.3 (BSD-Lizenz, siehe `LICENSE.txt`).

Das Paket wird nicht mehr gepflegt und läuft nicht mit Django 5.1+ und Python 3.12+. Übernommen wurde nur, was das Tool nutzt: Datenmodell `Notification`, Signal `notify`, Verwaltung und Migrationen.

Änderungen gegenüber dem Original:
- `index_together` durch `Meta.indexes` ersetzt (Django 5.1), Migration `0010`
- `distutils`-Versionsprüfung entfernt (Python 3.12)
