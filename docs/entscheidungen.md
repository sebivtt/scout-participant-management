# Entscheidungen

Fachliche und technische Entscheidungen mit Begründung. Neue Einträge oben. Wer eine Regel ändern will, ergänzt einen neuen Eintrag, statt einen alten zu überschreiben.

Format: Datum · Entscheidung · Begründung · Umsetzung

---

## 2026-10-19 · Vite 8: Vitest schon jetzt entfernen

**Entscheidung:**
- Mit dem Update von Vite 2.9 auf 8.3 wird das alte, nie benutzte Testwerkzeug Vitest 0.9 gleich mit entfernt, samt Beispieltest und den Befehlen `yarn test` und `yarn test:ci` im Frontend. Cypress bleibt wie geplant bis zum Aufräumen in Schritt 4. Ändert im Eintrag „Rauchtests: Werkzeug und Aufbau“ (16.10.2026) nur den Zeitpunkt für Vitest (Sebastian, auf Empfehlung der KI).
- Technisch (KI): Ziel ist die aktuelle Hauptversion Vite 8, nicht Vite 7. `@vitejs/plugin-vue` geht zwingend mit (2 → 6). `unplugin-auto-import` und `unplugin-vue-components` laufen unverändert mit Vite 8 und bleiben auf ihrer Fassung. Die Einstellungsdatei heißt jetzt `vite.config.mts`, weil Vite das alte Format künftig nicht mehr lädt.

**Begründung (Zusammenfassung der KI):** Vitest 0.9 bringt fest eine eigene Kopie von Vite 2 mit. Bliebe es, läge nach dem Update weiter ein altes Vite im Projekt, und die Sicherheitsprüfung zählte seine Lücken mit (24 Meldungen). Vite 2 bekommt seit Jahren keine Fehlerbehebungen mehr. Vite 8 statt 7, weil der Sprung von 2 auf 7 schon fast alle Umstellungen verlangt und Vite 8 länger gepflegt wird. Den eigentlichen Unterschied macht Rolldown, das neue Innenleben von Vite 8 zum Zusammenpacken des Codes. Deshalb liefen die Rauchtests auch gegen die gebaute Fassung, nicht nur gegen `yarn dev`.
**Umsetzung:** `frontend/package.json`, `frontend/vite.config.mts`, `frontend/yarn.lock` (PR #82).

## 2026-10-17 · Texteditor: bei Quill bleiben und auf Quill 2 aktualisieren

**Entscheidung:**
- Der Texteditor in Formularen (Einladungstext, Beschreibung eines Bausteins) bleibt Quill. `@vueup/vue-quill` geht von 1.2.0 auf 1.5.5 und bringt `quill` 2.0.2 mit. Kein Wechsel zu einem anderen Editor wie TipTap (Sebastian, auf Vorschlag der KI).
- Bestehende Texte und Formulare müssen nicht zwingend unverändert ins neue Format übernommen werden. Sebastian erneuert sie ohnehin (Sebastian).
- Technisch (KI): `Html.vue` übersetzt beim Laden mit Quills eigener Umwandlung in das Format von Quill 2 und speichert gewöhnliches HTML (`getSemanticHTML`), nicht das rohe HTML des Editors. `@vueup/vue-quill` steht in `package.json` fest auf 1.5.5 wie `axios`, damit eine neue Fassung nur gezielt kommt und vorher geprüft wird, ob sie wieder `quill` 2.0.3 zulässt.

**Begründung (Zusammenfassung der KI):** `quill` 1.3.7 war die einzige gemeldete Sicherheitslücke in Code, der im Browser läuft, und Quill 1 wird nicht mehr gepflegt. Ein Wechsel des Editors brächte neue Pakete, ein anderes Aussehen und mehr Risiko. Quill 2 speichert Listen intern in einem eigenen Format. Ohne Übersetzung verschwänden gespeicherte Aufzählungen beim Öffnen, und neue erschienen außerhalb des Editors nummeriert. Auch ohne alte Texte ist die Übersetzung nötig, weil jeder neu gespeicherte Text beim erneuten Bearbeiten wieder geladen wird. Nachteil: Quill wird schwach gepflegt (letzte Fassung November 2024), und 2.0.3 hat eine eigene, unbehobene Lücke. Deshalb schließt `@vueup/vue-quill` sie aus, und es bleibt bei 2.0.2. Das Update schließt die Warnung der Sicherheitsprüfung, schützt aber nicht davor, dass jemand mit Bearbeitungsrecht schädliches HTML speichert: Das Backend filtert gespeichertes HTML nicht.
**Umsetzung:** `frontend/package.json`, `frontend/src/components/field/Html.vue`, Rauchtest „Einladungstext mit Listen im Texteditor …“ in `rauchtests/tests/anmeldeablauf.spec.ts`.

## 2026-10-17 · Rauchtests 1c: alle Pflichtpunkte in einem Pull Request

**Entscheidung:**
- Schritt 1c der Rauchtests (Anmeldeablauf) setzt alle Pflichtpunkte aus „Vorarbeit für die Rauchtests“ (Fahrplan) in einem einzigen Pull Request um, samt der nötigen Erweiterung der Beispieldaten. Ausnahme von „ein Thema pro Pull Request“ (`CONTRIBUTING.md` Abschnitt 6).
- Die Tests räumen ihre Daten im Backend selbst auf.
- Auf GitHub laufen die Rauchtests dafür nur einmal, mit dem Label `rauchtests` am fertigen Pull Request.

**Begründung:** Effizienz. Die Pflichtpunkte teilen sich Einrichtung, Beispieldaten und Hilfsfunktionen, getrennte Pull Requests hätten jeweils dieselbe Vorarbeit und Prüfung gebraucht.
**Umsetzung:** `rauchtests/tests/anmeldeablauf.spec.ts`, `backend/basic/management/commands/load_sample_data.py`, `dev/keycloak-setup.sh` (PR #62).

## 2026-10-17 · Rollen klären, bevor Rechte geändert werden

**Entscheidung:**
- Bevor Rechte geändert werden, wird geklärt, welche Rollen es gibt, was jede Rolle darf und wann wer welche Rolle wie erhält. Dazu gehört, wie die Oberfläche dazu passt, z. B. was Suchen und Auswahllisten einer Rolle anzeigen.
- Die Klärung ist der erste Punkt in Strang 2 („Rollen und Rechte“), vor „Anmelden“. Rechte kommen in jedem Ablauf vor, so muss die Tabelle „wer darf was“ nicht in jedem Ablauf neu entschieden und später umgebaut werden. Ersetzt im Eintrag „Reihenfolge nach der Aufräumrunde“ (16.10.2026) „zuerst mit ‚Anmelden‘“.
- Issue #60 (anmeldende Leitung findet beim Hinzufügen einer verantwortlichen Person niemanden) kommt in Schritt 6 zu den Fehlern und wartet auf diese Klärung. Die Regel „könnte durch eine KI-Änderung entstanden sein, kommt direkt dran“ gilt hier ausdrücklich nicht.

**Begründung:** Sebastian möchte den ganzen Rollenaufbau ändern. Einzelne Rechte vorher anzupassen, würde Arbeit erzeugen, die danach wieder umgebaut werden müsste.
**Umsetzung:** `docs/fahrplan.md` (Strang 2, Punkt 1; Schritt 6; „Schon gesammelte Fragen“), Issue #60.

## 2026-10-17 · Rauchtests: nur bei Bedarf auf GitHub

**Entscheidung:**
- Auf GitHub laufen die Rauchtests nur, wenn ein Pull Request das Label `rauchtests` trägt, oder wenn jemand sie von Hand startet. Ersetzt im Eintrag „Rauchtests: Werkzeug und Aufbau“ (16.10.2026) „auf GitHub bei jeder Änderung“.
- Die riskanten Updates (Fahrplan, Schritt 3) bekommen das Label immer. Sonst entscheidet die KI im Einzelfall, etwa bei Änderungen an Login, Navigation oder vielen Seiten, und begründet das in der Beschreibung des Pull Requests. Sebastian kann das Label jederzeit setzen oder entfernen.
- In der Cloud-Sitzung lässt die KI die Rauchtests vor jedem Pull Request laufen, der Code ändert, und nennt das Ergebnis in der Beschreibung.

**Begründung:** Das Repository ist privat, GitHub stellt dafür nur ein begrenztes Kontingent an Rechenzeit bereit (2.000 Minuten im Monat im kostenlosen Tarif). Vom 14. bis 16.10.2026 liefen 55 Prüfläufe mit je mindestens 4 Minuten, bei diesem Tempo wäre das Kontingent im Monat schon ausgeschöpft. Ein Lauf der Rauchtests dauert auf GitHub gut 6,5 Minuten, abgerechnet werden 7. Die Läufe in der Cloud kosten nichts und fangen auch Brüche bei Änderungen ab, die niemand für riskant gehalten hätte.
**Umsetzung:** `.github/workflows/rauchtests.yml`, Label `rauchtests` auf GitHub (PR #61).

## 2026-10-16 · Rauchtests: Werkzeug und Aufbau

**Entscheidung:**
- Werkzeug ist Playwright (technisch, KI). Die alten, nie benutzten Testwerkzeuge im Frontend (Cypress 9.5, Vitest 0.9) werden nicht verwendet und später beim Aufräumen (Fahrplan, Schritt 4) entfernt.
- Es gibt nur eine Stufe (technisch, KI): Die Rauchtests laufen immer gegen das echte Backend mit echtem Keycloak 26.7, nicht gegen ein Platzhalter-Backend im Browser.
- Die Rauchtests laufen in der Cloud-Sitzung vor jedem Pull Request und auf GitHub bei jeder Änderung, als eigene Prüfung, die die Übernahme nicht sperrt. Livetests auf Sebastians Mac sind für die Rauchtests nicht nötig.
- Drei Pull Requests: 1a Beispieldaten und Anleitung, 1b jede Seite lädt ohne Programmfehler (mit der Prüfung auf GitHub), 1c Anmeldeablauf mit den Pflichtpunkten.
- Beispieldaten: Der Befehl `load_sample_data` legt die Veranstaltung „Beispiellager“ so an wie die Oberfläche und dazu eine Anmeldung mit zwei erfundenen Personen. Die Testkonten haben feste Rollen: `leitung` leitet, `stammesleitung` hat angemeldet, `teilnehmer` hat keine Rolle. Der Befehl verändert keine vorhandenen Daten und verweigert im Echtbetrieb.
- Pull Request 1a wird erst übernommen, wenn Sebastian die neuen Schritte der Anleitung auf seinem Mac ausprobiert hat (Sebastian).

**Begründung (Zusammenfassung der KI):** Keycloak läuft entgegen der bisherigen Annahme auch in der Cloud (Programmpaket von GitHub statt Docker-Abbild). Damit kann das ganze Tool dort und auf GitHub starten. Eine Stufe mit echtem Backend braucht nur einen Satz Beispieldaten, prüft zugleich, ob Oberfläche und Backend zusammenpassen, und hat keine gespielten Antworten, die veralten. Der Preis sind einige Minuten Laufzeit statt Sekunden. Playwright steuert einen echten Browser, hängt nicht von der Vite-Version ab und ist in der Cloud schon installiert. Cypress 9.5 bräuchte selbst erst ein riskantes Update. Die Anleitung kann die KI nicht auf einem Mac prüfen. Weil Sebastians Umgebung schon läuft, genügt es, nur die neuen Schritte zu prüfen (etwa 10 bis 15 Minuten).
**Umsetzung:** `backend/basic/management/commands/load_sample_data.py`, `tests/test_beispieldaten.py`, `docs/lokal-starten.md`, `docs/arbeitsumgebung.md` (PR 1a); Rauchtests in 1b und 1c. Ersetzt im Fahrplan „Zwei mögliche Stufen, noch abzustimmen“.

## 2026-10-16 · Der Fahrplan ist die einzige Reihenfolge

**Entscheidung:**
- `docs/fahrplan.md` enthält eine einzige Liste, die festlegt, was als Nächstes kommt, was danach, was vor dem ersten Echtbetrieb, was irgendwann und was bewusst nicht. Jedes offene Issue steht darin an seiner Stelle.
- Das Label `geklärt` heißt nur: fachlich fertig geklärt. Umgesetzt wird ein Issue erst, wenn es im Fahrplan an der Reihe ist **und** das Label trägt.
- Die Fehlerlisten im alten Fahrplan sind aufgelöst: Was Nutzende sehen oder spüren, ist ein Issue (neu #43 bis #57). Technische Schritte ohne sichtbare Wirkung (Updates, eslint, Prüfregeln, Aufräumen) stehen als Schritte im Fahrplan. Die Punkte zu Datenschutz und Betrieb bleiben als Liste „Vor dem ersten Echtbetrieb“ und werden zu Issues, wenn sie nach vorne rücken. „Keine Bestätigung nach dem Speichern“ geht in #39 auf, „Weiterleitung nach dem Speichern einer Gruppe“ in #41, der Reiter „Module“ und die Buchungsoption in die Abstimmung der Abläufe. Gestrichen ist „Zu komplexe Funktionen aufteilen“ (regelt die Pfadfinderregel). Die Weiterleitung im eingefrorenen Kontaktformular bleibt nur in `docs/qualitaet.md` vermerkt.
- Die offenen Fragen „Klicktest zu PR #11“ und „Person aus einer Anmeldung löschen“ sind gestrichen. Das prüfen künftig die Rauchtests und die Abstimmung. Fällt etwas fälschlich gesperrt auf, wird es ein Issue.

**Begründung (Zusammenfassung der KI):** Nach mehreren parallelen Sitzungen gab es drei Stellen, die jeweils festlegten, was als Nächstes kommt (Fahrplan, Issues mit Label, Entscheidungen), und sie widersprachen sich. Die Pop-ups #38 bis #42 waren geklärt, sollten laut #35 aber erst nach den Rauchtests und Tailwind kommen. Eine neue Sitzung hätte nach `CLAUDE.md` trotzdem mit ihnen beginnen dürfen. GitHub kann eine Wartebedingung wie „nach den Rauchtests“ nicht abbilden, weil die Rauchtests kein Issue sind.
**Umsetzung:** `docs/fahrplan.md` (neu aufgebaut), `docs/arbeitsumgebung.md` (Einrichtung der Cloud-Sitzung, ausgelagert), `CLAUDE.md` und `.claude/skills/grill-me/SKILL.md` (je ein Hinweis). Die älteren Einträge verweisen teils auf Abschnitte des alten Fahrplans („Übergabe“, „Reihenfolge der nächsten Schritte“, „Phase 3d“). Deren Inhalt steht jetzt unter „Reihenfolge“, „Vorgehen für künftige Updates“ und „Vorarbeit für die Rauchtests“. Was in „Phase 4“, „Phase 5“ und „Offene Punkte für später“ stand, ist ein Issue (#43 bis #57) oder steht unter „Vor dem ersten Echtbetrieb“ bzw. „Irgendwann, ohne festen Platz“.

## 2026-10-16 · Reihenfolge nach der Aufräumrunde

**Entscheidung:**
- Es gibt keinen festen Termin für den ersten Echtbetrieb. Gründlichkeit geht vor Tempo. Datenschutz und Betrieb kommen vor dem ersten Einsatz mit echten Anmeldungen, aber nicht jetzt.
- Die Abstimmung der Funktionen und Abläufe beginnt jetzt, parallel zur technischen Arbeit, zuerst mit „Anmelden“. Je Strang (Technik und Abstimmung) ist höchstens ein Pull Request gleichzeitig offen. Die Regel „der nächste Pull Request erst, wenn der vorige in `main` ist“ gilt je Strang.
- Strang Technik: Rauchtests → #37 → riskante Updates → eslint in die automatische Prüfung (mit #43) → Pop-ups #38 bis #42 → übrige Fehler und Anforderungen → Rest von Qualität II.
- Nach den Updates kommen zuerst die Pop-ups, dann die übrigen Fehler und Anforderungen.
- #37 („Mich selbst anmelden“ mittig) kommt nach den Rauchtests und vor den Updates, vorher mit `grill-me` geklärt.
- Technisch (KI): Bei den riskanten Updates kommt `quill` zuerst, weil es die einzige verbliebene Sicherheitslücke in Code ist, der im Browser läuft. Tailwind kommt zuletzt und direkt vor den Pop-ups, weil beide das Aussehen ändern und Sebastian es so nur einmal prüfen muss. Innerhalb von Schritt 6 kommen Fehler vor Anforderungen „Wichtig“ vor „Wäre schön“. Die Reihenfolge innerhalb dieser Gruppen ist ein Vorschlag der KI, den Sebastian jederzeit ändern kann.

**Begründung (Zusammenfassung der KI):** Die Abstimmung ist der Engpass: An ihr hängen T-Shirts und Lunch Pakete, die Buchungsoption, „bestätigt“ (#51), die offenen Fragen in #30 und Qualität II 4a/4b. Sie braucht vor allem Sebastians Zeit, kaum Programmierung, und stört die technische Arbeit deshalb nicht. Die Pop-ups sind geklärt und schließen ans Tailwind-Update an. In dieser Zeit klärt die Abstimmung die Regeln, die mehrere der übrigen Issues brauchen. Ohne Termin kostet diese Reihenfolge nichts. #37 ist klein und sofort sichtbar, und nach den Rauchtests ist das Fenster schon abgesichert, in dem #19 und #23 zweimal Fehler hatten.
**Umsetzung:** `docs/fahrplan.md`, Abschnitt „Reihenfolge“

## 2026-10-16 · Neue Fehler einsortieren

**Entscheidung:** Ein neuer Fehler kommt direkt nach dem laufenden Pull Request dran (nach `grill-me`), wenn er eine dieser Bedingungen erfüllt: Auswirkung „Blockiert“, er liegt im Bereich des nächsten Updates, oder er könnte durch eine KI-Änderung entstanden sein. Alle anderen neuen Issues werden in Schritt 6 des Fahrplans nach Auswirkung bzw. Wichtigkeit einsortiert.
**Begründung:** Ersetzt den Eintrag „Erst die Updates, dann gesammelte Fehler“ (16.10.2026) und übernimmt dessen zwei Ausnahmen. Ersetzt außerdem die Regel im Skill `grill-me`, nach der unter mehreren geklärten Issues die Wichtigkeit entscheidet. Beide galten nebeneinander und ließen offen, was Vorrang hat. Fehler wie #19 (Anmelden unmöglich) sollen weiter sofort drankommen, alles andere wartet seinen Platz ab. Die Ausnahmen verhindern, dass nach einem Update unklar ist, ob ein Fehler alt oder neu ist (so bei #23 vor Vue 3.5), und dass selbst verursachte Fehler liegen bleiben.
**Umsetzung:** `docs/fahrplan.md`, Abschnitt „Regeln für die Reihenfolge“, Skill `grill-me` (Abschnitt „Danach“)

## 2026-10-16 · Anforderungen warten auf die Abstimmung ihres Ablaufs

**Entscheidung:** Eine Anforderung aus den Issues wird erst umgesetzt, wenn der Ablauf, zu dem sie gehört, abgestimmt ist. Im Fahrplan steht bei jeder Anforderung, auf welchen Ablauf sie wartet. Fehler warten nicht, außer sie brauchen ausdrücklich eine fachliche Antwort aus der Abstimmung (z. B. #51). Die Pop-ups (#38 bis #42) ändern nur die Darstellung, nicht Funktionen oder Inhalte, und warten deshalb nicht.
**Begründung:** Fasst die Entscheidung „Abstimmung aller Funktionen und Abläufe vor Phase 4“ (15.10.2026) genauer, seit die Abstimmung parallel zur Technik läuft. Die Regel „erst abstimmen, dann Anforderungen anpassen“ gilt weiter, aber je Ablauf statt erst nach allen sechs. So entsteht kaum Wartezeit, und keine Anforderung wird gegen ungeklärte Regeln gebaut.
**Umsetzung:** `docs/fahrplan.md`, Abschnitte „Regeln für die Reihenfolge“ und Schritt 6

## 2026-10-16 · Rauchtests: eigenes Rot vor der Übernahme beheben

**Entscheidung:** Macht ein Pull Request einen vorher grünen Rauchtest rot, wird das vor der Übernahme behoben oder im Pull Request begründet. Was schon vorher rot war, wird ein Issue und blockiert nichts. GitHub sperrt die Übernahme nicht automatisch.
**Begründung:** Beantwortet die offene Frage im Eintrag „Rauchtests und Umgang mit gefundenen Fehlern“ (16.10.2026), wie von der KI vorgeschlagen. Sonst wären die Rauchtests für die riskanten Updates wirkungslos, denn ein Update würde trotz Bruch übernommen.
**Umsetzung:** `docs/fahrplan.md`, Abschnitt „Regeln für die Reihenfolge“

## 2026-10-16 · Issues erst klären, dann umsetzen

**Entscheidung:**
- Neue Issues werden beim Anlegen auf Abhängigkeiten zu offenen Issues geprüft (blockiert durch, blockiert, berührt dieselbe Stelle, Dublette). Abhängigkeiten stehen als Verknüpfung auf GitHub und mit Begründung im Text.
- Bevor die KI ein Issue umsetzt, fragt sie Sebastian mit dem Skill `grill-me` aus: erst eine Übersicht der zu klärenden Themen, dann eine Frage pro Nachricht, jeweils mit Möglichkeiten und Empfehlung, so lange, bis nichts mehr offen ist. Fachliches entscheidet Sebastian, Technisches die KI mit Begründung. Was die KI im Code nachsehen kann, fragt sie nicht.
- Alle Antworten werden ins Issue übernommen (als Kriterium, Beispiel, Abgrenzung oder Abhängigkeit), dazu ein Kommentar mit dem Frage-Antwort-Protokoll.
- Danach wird entschieden, ob das Issue in einem Schritt umgesetzt wird oder in Unter-Issues aufgeteilt wird. Teile werden als Unter-Issues verknüpft, die Reihenfolge als „blockiert durch“.
- Das Label `geklärt` ist die Freigabe. Umgesetzt wird nur, was es trägt. Es wird erst nach Sebastians ausdrücklichem Okay gesetzt.
- Umsetzung: ein Issue = ein Pull Request mit eigenem Test, der Reihe nach.
- Abgrenzung: Das gilt für Fehler und Anforderungen aus den Issues. Die geplanten Schritte im Fahrplan (z. B. Rauchtests, Updates) laufen weiter wie bisher.

**Begründung (Zusammenfassung der KI):** Sebastian möchte, dass Anforderungen, Grenzfälle und Probleme vollständig geklärt sind, bevor etwas umgesetzt wird, und dass große Vorhaben in kleine Schritte zerlegt werden, weil sonst das Risiko für Fehler zu groß ist. Die Abhängigkeiten verhindern, dass zwei Änderungen sich gegenseitig stören.
**Umsetzung:** `.claude/skills/grill-me/SKILL.md`, `.claude/skills/issue-anlegen/SKILL.md`, `CLAUDE.md` (Abschnitt „Arbeitsweise“), Label `geklärt` auf GitHub.

## 2026-10-16 · Vorlagen für Fehler und Anforderungen

**Entscheidung:**
- Neue Fehler und Anforderungen werden nur noch als Issue auf GitHub festgehalten, jeweils eines pro Thema. Die Listen im Fahrplan werden nicht weiter ergänzt. Bestehende Listenpunkte können nach und nach zu Issues werden.
- Es gibt zwei Vorlagen (`.github/ISSUE_TEMPLATE/`): „Fehler melden“ (Label `bug`) und „Neue Anforderung“ (Label `enhancement`). Wer kein Schreibrecht hat, kann auf GitHub keine leeren Issues ohne Vorlage anlegen. Wer Schreibrecht hat (auch Sebastian), sieht „Blank issue“ weiterhin, nimmt aber trotzdem eine Vorlage.
- Faustregel für die Einordnung: Fehler heißt, das Tool tut etwas Falsches oder Unerwartetes. Anforderung heißt, das Tool soll etwas können, was bisher nicht vorgesehen ist.
- Die bestehenden Issues werden anschließend nach den Vorlagen überarbeitet.

**Begründung:** Gleich aufgebaute Issues lassen sich ohne Rückfragen bearbeiten, und es gibt nur eine Stelle, an der offene Punkte stehen. Sebastian schreibt die Issues, die Umsetzung übernimmt meist die KI.
**Umsetzung:** `.github/ISSUE_TEMPLATE/fehler.yml`, `anforderung.yml`, `config.yml`. Legt die KI ein Issue über die Schnittstelle an, gilt die Vorlage nicht automatisch: Sie übernimmt alle Überschriften der Vorlage als `### …`, auch die der Auswahlfelder (Rolle, Auswirkung, Wichtigkeit), und setzt das Label selbst.

## 2026-10-16 · Rauchtests und Umgang mit gefundenen Fehlern

**Entscheidung:**
- Der wichtigste Ablauf für die Rauchtests ist die Standard-Anmeldung über alle Schritte bis zum Absenden.
- Rote Rauchtests blockieren keine Übernahme. Jeder gefundene Fehler wird als Issue auf GitHub angelegt und danach der Reihe nach abgearbeitet.
- Für Livetests auf dem Mac steht Docker zur Verfügung.

**Offen (Abgrenzung):** Gilt „blockiert nicht“ auch, wenn ein Pull Request die Rauchtests selbst rot macht, etwa ein Versionssprung? Die älteren Einträge „Modernisierung des Frontends: risikoarme Sprünge“ und „Erst die Updates, dann gesammelte Fehler“ sehen die Rauchtests als Sicherheitsnetz für die riskanten Sprünge. Vorschlag der KI: GitHub sperrt die Übernahme nicht automatisch, aber ein Rot, das der eigene Pull Request verursacht, wird vorher behoben oder im Pull Request begründet. Wartet auf Sebastians Antwort.
**Begründung (Zusammenfassung der KI):** Fehler sollen sichtbar und nachvollziehbar gesammelt werden, ohne die Arbeit an anderen Stellen anzuhalten.
**Umsetzung:** `docs/fahrplan.md`, Abschnitte „Übergabe“ und „Vorarbeit für die Rauchtests“

## 2026-10-16 · T-Shirts und Lunch Pakete nicht in jeder Veranstaltung

**Entscheidung:** Die Abfragen „T-Shirts“ und „Lunch Pakete“ sollen nicht standardmäßig in jeder neuen Veranstaltung auftauchen. Was Standard ist und was die Veranstaltungsleitung zusätzlich wählt, wird in der Abstimmung der Funktionen und Abläufe geklärt.
**Begründung:** Seit PR #27 erscheinen beide Schritte im Anmeldeablauf, weil die Standardvorlage sie jeder neuen Veranstaltung mitgibt (`backend/data/main/3_event.json`, `other_required_modules`). Vorher waren sie zwar enthalten, aber nicht beantwortbar und blockierten den Ablauf (Issue #25).
**Umsetzung:** offen, bis zur Abstimmung bleibt die Vorlage unverändert. Die Veranstaltungsleitung kann beide Schritte in der Veranstaltung entfernen.

## 2026-10-16 · Erst die Updates, dann gesammelte Fehler

**Entscheidung:** Neu gemeldete Fehler werden gesammelt und nach den Versionssprüngen im Frontend behoben. Ausnahme: Ein Fehler liegt genau in dem Bereich, den das nächste Update betrifft, oder er könnte durch eine KI-Änderung entstanden sein. Dann kommt er zuerst.
**Begründung:** Das Tool ist noch nicht im Echtbetrieb, die Modernisierung soll vorankommen. Ein bekannter Fehler im Bereich eines Updates macht aber unklar, ob ein Problem danach alt ist oder vom Update kommt (so bei Issue #23 vor Vue 3.5).
**Umsetzung:** `docs/fahrplan.md`, Abschnitt „Übergabe“ (gesammelte Fehler)

## 2026-10-15 · Dublettenprüfung beim Anmelden

**Entscheidung:**
- Ist eine Person (gleicher Vor- und Nachname, gleicher Geburtstag) schon für die Veranstaltung angemeldet, erscheint die Meldung sofort beim Hinzufügen der Person, nicht erst beim Abschicken. Das gilt für alle Wege: neue Person, „Mich selbst anmelden“, Stammesmitglieder.
- Bei einer neuen Anmeldung darf jede eingeloggte Person diese Prüfung auslösen, solange neue Anmeldungen möglich sind, also mit denselben Rechten wie beim Anlegen der Anmeldung selbst. Die Veranstaltungsleitung ist von Sperren ausgenommen. Bei einer bestehenden Anmeldung bleibt die Prüfung der anmeldenden Leitung und der Veranstaltungsleitung vorbehalten.
- Wer eine schon gespeicherte Person bearbeitet, bekommt keine Dublettenmeldung für die Person selbst.

**Begründung:** Issue #19: Seit PR #3 war jede neue Anmeldung mit Personen unmöglich, weil die Prüfung eine Anmeldung erwartete, die es noch nicht gab. Die Prüfung verrät nur „ja oder nein“ für genau eine Person, mehr als das Anlegen einer Anmeldung ohnehin erlaubt, braucht sie nicht.
**Umsetzung:** `anmelde_tool/registration/views.py` (`EventCheckPersonViewSet`, `CheckPersonViewSet`), Tests in `tests/test_dublettenpruefung.py` (PR #21)

## 2026-10-15 · Modernisierung des Frontends: risikoarme Sprünge vor den Rauchtests

**Entscheidung:** Die Versionssprünge im Frontend werden nach Risiko aufgeteilt (Weg C). Risikoarme Sprünge kommen sofort, je als kleiner Pull Request mit Klickliste: TypeScript und eslint, `uuid`, Vue 3.5. Danach folgen die Rauchtests, dann die riskanten Sprünge (Vite, Pinia, vue-router, `quill`, Tailwind). Zieht ein risikoarmer Sprung einen riskanten nach sich, wird er nach hinten verschoben.
**Begründung:** Ändert den Eintrag „Reihenfolge: erst Sicherheitsnetz, dann Frontend aktualisieren“ vom selben Tag. Fehler beim Bauen meldet die automatische Prüfung schon heute. Rauchtests fangen zusätzlich Seiten ab, die sich bauen lassen, im Browser aber leer bleiben oder Fehler zeigen. Dieses Risiko ist bei Vite, Pinia, vue-router und `quill` hoch, bei TypeScript und eslint (nur Entwicklungswerkzeuge), `uuid` (eine Stelle) und Vue 3.5 (verträglich) gering. So geht die Modernisierung sofort voran, ohne an den riskanten Stellen auf das Sicherheitsnetz zu verzichten. Tailwind verändert das Aussehen, das auch Rauchtests nicht sehen: Dort prüft zusätzlich der Projektverantwortliche das Aussehen.
**Umsetzung:** `docs/fahrplan.md` Abschnitte „Reihenfolge der nächsten Schritte“ und „Phase 3d“

## 2026-10-15 · Sicherheitsupdates: Hauptversion und mitgebrachte Pakete

**Entscheidung:** Bei Sicherheitsupdates verlässt kein Paket, das wir selbst wählen, seine Hauptversion. Das gilt für Pakete in `package.json` und für Vorgaben über `resolutions`. Was ein aktualisiertes Paket zwingend selbst verlangt, darf mitkommen, auch in einer neuen Hauptversion. Jedes mitgebrachte Paket in neuer Hauptversion und jedes neu hinzugekommene Paket wird im Pull Request genannt und begründet (`CONTRIBUTING.md` Abschnitt 5). Kleine Hilfspakete desselben Ursprungs dürfen in einer Sammelzeile stehen.
**Begründung:** axios 1.20.0 schließt 33 Sicherheitslücken und verlangt dafür ein Hilfspaket in neuer Hauptversion (`proxy-from-env` 2) sowie ein neues Hilfspaket (`https-proxy-agent`). Beide laufen nur auf Servern, nicht im Browser. axios deshalb alt zu lassen, hätte bekannte Lücken offengelassen.
**Umsetzung:** `docs/fahrplan.md` Phase 3d („Vorgehen für künftige Updates“), erstmals angewendet in PR #16

## 2026-10-15 · Abgleich Frontend und Backend als automatische Prüfung

**Entscheidung (technisch):** Jede Anfrage des Frontends muss eine vorhandene Backend-Adresse mit erlaubter Anfrageart treffen. Ein Test prüft das bei jeder Änderung, und die Karte `docs/schnittstellen.md` wird aus dem Code erzeugt statt von Hand gepflegt.
**Begründung:** In PR #11 hätte das Entfernen einer Adresse fast alle Veranstaltungsseiten lahmgelegt, weil eine Textsuche zusammengesetzte Pfade nicht fand. Eine von Hand gepflegte Liste würde schnell veralten.
**Umsetzung:** `backend/tools/frontend_aufrufe.py`, `backend/tools/schnittstellen_karte.py`, `tests/test_frontend_abgleich.py` (PR #14)

## 2026-10-15 · Reihenfolge: erst Sicherheitsnetz, dann Frontend aktualisieren

**Entscheidung:** Vor den großen Versionssprüngen im Frontend entsteht ein Sicherheitsnetz: der automatische Abgleich zwischen Frontend und Backend und Rauchtests für das Frontend. Sicherheitsupdates innerhalb der Hauptversionen kommen früher. Die Modernisierung des Frontends (Phase 3d) kommt vor Phase 4. Die vollständige Reihenfolge steht im Fahrplan.
**Begründung:** Das Backend-Update war beherrschbar, weil 135 Tests jeden Schritt geprüft haben. Das Frontend hat keinen Test, ob nach einem Update noch alles geht, ließe sich also nur durch Klicken prüfen. Phase 4 baut den Anmeldeablauf stark um und soll nicht auf dem alten Fundament entstehen.
**Umsetzung:** `docs/fahrplan.md` Abschnitte „Reihenfolge der nächsten Schritte“ und „Phase 3d“

## 2026-10-15 · Abstimmung aller Funktionen und Abläufe vor Phase 4

**Entscheidung:** Bevor Anforderungen und Funktionen angepasst werden, stimmen KI und Projektverantwortlicher alle Funktionen und Abläufe gemeinsam ab. Am Ende gibt es zu jedem Ablauf einen Prozessablauf, und jede Funktion ist mit ihren Anforderungen abgestimmt: was kann wer, was darf wer und wann darf was gemacht werden.
**Begründung:** Diese Fragen stellen sich an vielen Stellen, auch bei der KI-Fehlerprüfung. Solange der Projektverantwortliche nicht nebenbei testen kann, ist ohne eine solche Grundlage kaum einzuschätzen, was wer wann darf.
**Umsetzung:** `docs/fahrplan.md` Abschnitt „Abstimmung der Funktionen und Abläufe“, Ergebnis in `docs/ablaeufe/`. Qualität II 4a/4b folgen danach.

## 2026-10-15 · Ansichtsgruppe ändert nichts

**Entscheidung:** Die Ansichtsgruppe einer Veranstaltung darf nichts ändern, auch keine Bausteine oder Preisstufen.
**Begründung:** So beschreibt es das Glossar. Der Code erlaubte ihr bisher, Bausteine und Preisstufen zu ändern und Anmeldungen zusammenzulegen.
**Umsetzung:** `anmelde_tool/event/permissions.py` (`IsSubEventResponsiblePersonOrReadOnly`), Tests in `tests/test_zugriffsschutz.py` (PR #11)

## 2026-10-15 · Veranstaltungsorte

**Entscheidung:**
- Den Ort einer bestimmten Veranstaltung passen nur das Anmeldeteam und die Veranstaltungsleitung an, beim Anlegen oder Bearbeiten der Veranstaltung.
- Zusätzlich soll es eine zentrale Verwaltung der Orte geben (neue Funktion), in der Admins und Leitungen Orte verwalten dürfen. Welche Leitungen genau, wird in der Abstimmung der Abläufe geklärt.

**Umsetzung bis zur zentralen Verwaltung:** Einen Ort ändert, wer alle Veranstaltungen an diesem Ort leitet, oder das Anmeldeteam. Unbenutzte Orte ändert nur das Anmeldeteam (PR #11).

## 2026-10-15 · Essensplanung und Programmideen abschalten

**Entscheidung:** Die eingefrorenen Module `food` (Essensplanung) und `inspi` (Programmideen) werden zunächst abgeschaltet. Abgesichert werden sie gegebenenfalls später, wenn ihre Anforderungen geklärt sind.
**Begründung:** In beiden kann jede eingeloggte Person Einträge anderer ändern oder löschen. Sie abzusichern wäre aufwendig, und ihre Anforderungen sind ohnehin offen.
**Umsetzung:** `backend/backend/urls.py`, Menüs im Frontend, Test `tests/test_abgeschaltete_module.py` (PR #12)

## 2026-10-15 · Rechte auf schreibende Schnittstellen

**Entscheidung (technisch):**
- Wer etwas ändert, braucht das Recht auf genau dieses Objekt: die Anmeldung (anmeldende Leitung oder Veranstaltungsleitung) oder die Veranstaltung (Veranstaltungsleitung). Der Login allein genügt nie.
- Die Zugehörigkeit eines Eintrags (zu welcher Veranstaltung, zu welcher Anmeldung) kommt aus der Adresse, nicht aus dem Inhalt der Anfrage.
- Antworten auf Zusatzfelder unterliegen derselben Änderungsfrist wie die Anmeldung.
- Gemeinsam genutzte Daten (Vorlagen für Zusatzfelder, Farbschemata) ändert nur das Anmeldeteam.
- Veranstaltungsorte siehe Eintrag „Veranstaltungsorte“ (15.10.2026).

**Begründung:** Qualität II fand 20 Lücken dieser Art, darunter Lesen und Ändern der Antworten aller Anmeldungen durch jede eingeloggte Person. Die Regeln folgen aus der Entscheidung „Wer sieht welche Anmeldungen“ vom 14.10.2026.
**Umsetzung:** `tests/test_zugriffsschutz.py`, `tests/test_schreibrechte_inventar.py`, `CONTRIBUTING.md` Abschnitt 3 (PR #11)

## 2026-10-15 · Sicherheitsregeln und feste Passwörter

**Entscheidung:**
- Die automatische Prüfung meldet bekannte unsichere Muster: abgeschaltete Zertifikatsprüfung, Passwörter im Code, verschluckte Fehler, unsichere Aufrufe (ruff, Regelgruppe S).
- Ein festes Passwort ist nur in Code erlaubt, der im Echtbetrieb verweigert wird (Prüfung auf `DEBUG=True`), mit Test. Administratoren im Echtbetrieb werden mit `python manage.py createsuperuser` angelegt.
- Tests dürfen `assert` und erfundene Passwörter verwenden.

**Begründung:** Das alte Startskript legte bei jedem Serverstart ein Administratorkonto mit öffentlich bekanntem Passwort an. Solche Fehler soll die Prüfung künftig von selbst finden.
**Umsetzung:** `CONTRIBUTING.md` Abschnitt 3, `backend/ruff.toml`, `tests/test_verwaltungsbefehle.py` (PR #10)

## 2026-10-15 · Regeln für Ausnahmen und bekannte Fehler

**Entscheidung:**
- `# noqa` nur mit Regelnummer. Pauschale und überflüssige Markierungen meldet ruff.
- Gewollte Markierungen (nötig, keine Altlast) tragen hinter der Regelnummer nach `--` eine Begründung und haben einen Test, der anschlägt, wenn die Zeile fehlt.
- Bekannte Fehler werden als `xfail(strict=True, raises=...)` mit genau der erwarteten Fehlerart festgehalten.

**Begründung:** Eine Markierung ohne Regelnummer schaltet auf ihrer Zeile auch Prüfungen ab, die erst später eingeschaltet werden, und versteckt so neue Funde. Ohne `raises` gälte jeder beliebige Fehler als „bekannt“. Ohne Begründung und Test lässt sich nicht erkennen, ob eine Markierung nötig ist: Ein scheinbar überflüssiger Import meldet zum Beispiel den Keycloak-Abgleich bei Celery an.
**Umsetzung:** `CONTRIBUTING.md` (Abschnitte 3 und Altlasten), `backend/ruff.toml` (PGH004, RUF100), `tests/test_signale.py` (PR #9)

## 2026-10-15 · Vorgehen bei der KI-Fehlerprüfung (Qualität II)

**Entscheidung:**
- Probleme, die schon für Phase 4 geplant sind (z. B. Absenden in Einzelschritten, „bestätigt“ wird nie gesetzt, feste Fehlermeldungen), werden in Qualität II nur als Test festgehalten, der sie als bekannten Fehler markiert. Behoben werden sie in Phase 4. Neu gefundene kleine Fehler werden sofort behoben, jeweils mit Test.
- Prüftiefe nach Modul: Automatische Prüfungen und die Sicherheitsprüfung von Hand (offene Adressen, Datenfreigabe, Rechte) laufen über den gesamten Code. Fachliche Randfälle und Fehlerbehandlung werden von Hand nur in den aktiven Modulen geprüft, nicht in den eingefrorenen (`food`, `inspi`, `messaging`, `notifications`).
- Funde in eingefrorenen Modulen werden in `docs/qualitaet.md` festgehalten, aber nicht behoben. Ausnahme: Sicherheitslücken werden sofort behoben, mit Test.

**Begründung:** Die Prüfung soll vollständig dokumentiert sein, ohne Aufwand in Code zu stecken, der derzeit nicht weiterentwickelt wird. Die eingefrorenen Module sind aber über eigene Adressen im Internet erreichbar, das Kontaktformular sogar ohne Login. Sicherheitslücken dort treffen deshalb das ganze Tool.
**Umsetzung:** `docs/fahrplan.md` Abschnitt „Qualität II“. Ob die eingefrorenen Module behalten oder entfernt werden, bleibt offen (siehe Fahrplan, offene Punkte).

## 2026-10-15 · Entwicklungsregeln und Qualitätsprüfungen

**Entscheidung:** Für alle Änderungen gelten die Regeln in `CONTRIBUTING.md`. GitHub prüft automatisch Stil, Komplexität, Tests, Migrationen und Sicherheitslücken. Vor jedem Pull Request prüft eine unabhängige KI-Instanz die Änderung.
**Begründung:** Der Code entsteht überwiegend mit KI, und der Projektverantwortliche kann ihn nicht im Detail prüfen. Die Qualität soll deshalb durch Mechanismen gesichert werden, nicht durch Vertrauen.
**Umsetzung:** `CONTRIBUTING.md`, `CLAUDE.md`, `backend/ruff.toml`, `.github/workflows/ci.yml`

## 2026-10-15 · Sprache im Code

**Entscheidung:** Englische Namen im Code, deutsche Erklärungen (Kommentare, Docstrings, Dokumentation, Pull Requests).
**Begründung:** Der übernommene Code ist englisch benannt. Die Erklärungen sollen für alle im Verband lesbar sein.

## 2026-10-14 · Fristen

**Entscheidung:**
- Der offizielle Anmeldeschluss sperrt nichts. Späte Anmeldungen sind im Ehrenamt üblich.
- Neue Anmeldungen lassen sich optional ab einem Datum technisch sperren oder jederzeit manuell.
- Änderungen an Anmeldungen sind bis „letzte Änderung möglich“ erlaubt, sonst bis Veranstaltungsbeginn. Auch sie lassen sich manuell sperren.
- Personen zu einer bestehenden Anmeldung hinzuzufügen zählt als Änderung.
- Sind Änderungen gesperrt, sind auch neue Anmeldungen gesperrt. Umgekehrt gilt das nicht.
- Die Veranstaltungsleitung ist von allen Sperren ausgenommen.

**Umsetzung:** `anmelde_tool/event/deadlines.py`, Tests in `tests/test_fristen.py` (PR #5)

## 2026-10-14 · Gruppenrechte im Tool statt in Keycloak

**Entscheidung:** Wer welche Gruppe verwalten oder einsehen darf, steht in der Tabelle `GroupPermission` im Tool. Keycloak liefert nur Login und Gruppenmitgliedschaften.
**Begründung:** Die bisherige Lösung brauchte die veraltete Keycloak-Funktion `admin-fine-grained-authz:v1`, die beim Verband abgeschaltet ist. Das Tool soll mit einem Standard-Keycloak laufen und Keycloak-Updates überstehen. Ein Ausfall von Keycloak führt zu weniger Rechten, nie zu mehr.
**Regeln:**
- Rechte gelten auch für Untergruppen. Admin schließt Ansicht ein.
- Führungsgruppen (Stammesführung, Bundesführung, …) verwalten die Gruppe darüber. Mitglieder eines Stamms sehen ihren Stamm.
- Eine Gruppe löschen darf nur, wer die Obergruppe verwaltet.
- Über die eigene Beitrittsanfrage entscheidet nie man selbst.
- Die Rolle „Anmeldeteam“ (Staff) hat überall Admin-Recht. Bleibt vorerst so, Feinabstimmung später.

**Umsetzung:** `keycloak_auth/access.py`, Tests in `tests/test_gruppenrechte.py` (PR #2)

## 2026-10-14 · Wer sieht welche Anmeldungen

**Entscheidung:**
- Die Veranstaltungsleitung sieht alle Anmeldungen ihrer Veranstaltung.
- Die anmeldende Leitung sieht und bearbeitet ihre eigene Anmeldung vollständig.
- Teilnehmende sehen von ihrer Gruppenanmeldung nur die Namen der Mitangemeldeten. Anmeldungen anderer Gruppen sehen sie nicht.
- Personenlisten eines Stamms sehen nur Leitungen mit Admin-Recht auf den Stamm.

**Umsetzung:** Tests in `tests/test_rechte.py`. Die Namensansicht für Teilnehmende ist noch nicht gebaut (Phase 5).

## 2026-10-14 · Zusatzfelder pro Veranstaltung

**Entscheidung:** Daten wie die Ausweisnummer werden nicht fest abgefragt, sondern von der Veranstaltungsleitung pro Veranstaltung als Zusatzfeld festgelegt.
**Begründung:** Die Ausweisnummer war nur für eine Auslandsfahrt nötig (Datensparsamkeit, DSGVO).
**Umsetzung:** offen (Phase 5)

## 2026-10-14 · Hosting und Daten

**Entscheidung:** Start mit leerer Datenbank (nur Stammdaten). Offizieller Betrieb später beim Verband, bis dahin eine günstige eigene Lösung. Keycloak des Verbands: Version 26.7.

## 2026-10-14 · Basis und Repository

**Entscheidung:** Ein gemeinsames Repository für Backend und Frontend, mit vollständiger Historie. Basis sind Backend `main` (12.03.2025) und Frontend `ce97a2d` (23.03.2025). Nutzung mit Erlaubnis der ursprünglichen Entwickler, Lizenz noch offen.
