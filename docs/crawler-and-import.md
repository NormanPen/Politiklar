# Crawler und Datenimporte

Alle bestehenden Importer verwenden offizielle Bundestag-Quellen und legen fuer jede Antwort eine Quellenprovenienz an: angefragte und aufgeloeste URL, Abrufzeit, HTTP-Status, Content-Type, SHA-256-Hash und Archivpfad.

## Installation

```bash
make crawler-install
make help
```

## Vollimport und inkrementeller Refresh

```bash
# Vollständiger Import aller Quellen der aktuellen Wahlperiode:
make bundestag-import

# Inkrementelles Update: Überspringt bereits vorhandene Quellen sekundenschnell
# und zieht nur neue Dokumente sowie fehlende Abgeordneten-Profilbilder nach:
make bundestag-refresh

# Optional mit Limit (z. B. für Tests oder begrenzte Durchläufe):
make bundestag-refresh LIMIT=10

# Auf eine Quellfamilie beschränken:
make bundestag-refresh FAMILY=members   # Nur Abgeordnete und fehlende Profilbilder
make bundestag-refresh FAMILY=votes     # Nur namentliche Abstimmungen (XLSX)
make bundestag-refresh FAMILY=protocols # Nur Plenarprotokolle (XML)

# Trockenlauf zur Prüfung der Link-Discovery (ohne DB-Schreibzugriff):
make bundestag-import DRY_RUN=1 LIMIT=5
```

`bundestag-import` entdeckt und importiert alle aktuell verlinkten Bundestag-Biografien, namentlichen Abstimmungslisten und Plenarprotokolle der 21. Wahlperiode. `bundestag-refresh` prüft vorab gegen die vorhandenen Einträge in `source_documents` und lädt nur noch unverarbeitete URLs bzw. fehlende Profilbilder nach. Beide Befehle geben live Fortschrittsmeldungen im Terminal aus und schließen mit einem JSON-Zusammenfassungsbericht ab.

## Quellenabruf

```bash
make crawler-fetch URL=https://www.bundestag.de/
```

Der Abruf speichert die unveraenderte Antwort in `var/source-archive/<hash-prefix>/<sha256>`. Das Verzeichnis ist lokal ignoriert und muss im Betrieb zusammen mit der Datenbank gesichert werden.

## Abgeordnetenbiografie

```bash
make member-import URL=https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330
```

Der Import nutzt die MDB-ID aus der amtlichen Biografie-URL. Er speichert Profilsnapshots, Bundestags- und Wahlkreisbuero-Adressen, Kontaktformular, externe Profil-Links, Wahlkreismandat und strukturierte Bundestagsrollen. Zudem wird automatisch versucht, das verifizierte Profilbild aus Wikimedia Commons zu laden. Wiederholte Imports gleicher Fachwerte erzeugen keine doppelten Fakten.

## Abgeordneten-Profilbilder (Wikimedia Commons & Wikidata)

```bash
make member-image URL=https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330
```

Der Importer ermittelt über die Wikidata-API das zur MDB-ID gehörende Wikidata-Item. Um Verwechslungen auszuschließen, wird das Item streng über `P1713` (Bundestag-Biografie-URL) oder `P1186` (MdB-ID) verifiziert; es findet kein Namensraten statt. Liegt ein Bild in Property `P18` vor, ruft der Crawler die Bild- und Lizenzmetadaten von der Wikimedia-Commons-API ab, archiviert den Quellabruf in `var/source-archive/` und `source_documents` und trägt das Bild in `member_image_candidates` ein. Freie Lizenzen (z. B. CC-BY, CC-BY-SA, CC0, Public Domain) werden geprüft (`license_approved = true`) und erhalten bei Erstzuordnung den Status `approved`.

## Namentliche Abstimmungen

```bash
make vote-import URL=https://www.bundestag.de/resource/blob/1194616/20260710_8-xls.xlsx
```

Der XLSX-Importer erfasst Wahlperiode, Sitzung, Abstimmung und jede amtliche Namenszeile. Er bewahrt die Rohangabe und normalisiert nur explizite Markierungen zu `yes`, `no`, `abstained`, `invalid` oder `not_voted`; unklare Werte werden `unknown`.

Die aktuelle XLSX-Struktur enthaelt keine MDB-ID. Daher bleiben `member_id`-Beziehungen leer, bis eine verifizierte amtliche Identifikatorquelle vorhanden ist. `nichtabgegeben` ist ein offizielles Ergebnis und keine Aussage ueber den Grund einer Nichtteilnahme.

## Plenarreden

```bash
make speeches-import URL=https://www.bundestag.de/resource/blob/1194732/21090.xml
```

Der XML-Importer speichert Wahlperiode, Sitzung, amtliche Rede-ID, Sprecher-ID, Name, Fraktion und Wortlaut. Die Sprecher-ID des Protokolls ist noch nicht als MDB-ID verifiziert; deshalb wird auch hier keine Namenszuordnung geraten.

Eine Sprecher-ID kann nach manueller Pruefung mit einem Abgeordneten verknuepft werden:

```bash
make speaker-verify \
	MDB_ID=1043330 \
	SPEAKER_ID=11004011 \
	BIOGRAPHY_URL=https://www.bundestag.de/abgeordnete/biografien/... \
	PROTOCOL_URL=https://www.bundestag.de/resource/blob/...xml \
	VERIFIED_BY=name
```

Der Befehl prueft die MDB-ID gegen die Biografie und die Sprecher-ID gegen das Protokoll. Beide abgerufenen Quellen werden als Belege gespeichert. Danach verbindet der Importer alle schon gespeicherten Reden derselben Sprecher-ID mit dem Abgeordneten. Eine Sprecher-ID, die bereits einer anderen Person zugeordnet ist, wird abgelehnt.

## Noch nicht automatisiert

Vollstaendige Mitgliederdiscovery, Drucksachen, weitere Gremien und veroeffentlichungspflichtige Angaben sind noch keine produktiven Importer. Insbesondere der Drucksachen-API-Endpunkt verlangt einen DIP-API-Key; ein Schluessel wird erst in einer ignorierten Umgebungsdatei konfiguriert, nicht im Repository.

Zurueck zur [Dokumentationsuebersicht](README.md).