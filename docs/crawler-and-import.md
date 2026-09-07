# Crawler und Datenimporte

Alle bestehenden Importer verwenden offizielle Bundestag-Quellen und legen fuer jede Antwort eine Quellenprovenienz an: angefragte und aufgeloeste URL, Abrufzeit, HTTP-Status, Content-Type, SHA-256-Hash und Archivpfad.

## Installation

```bash
make crawler-install
make help
```

## Vollimport und Refresh

```bash
make bundestag-import
make bundestag-refresh
```

`bundestag-import` entdeckt und importiert alle aktuell verlinkten Bundestag-Biografien, namentlichen Abstimmungslisten und Plenarprotokolle der 21. Wahlperiode. `bundestag-refresh` verwendet denselben idempotenten Ablauf fuer neue oder veraenderte Quellen. Beide Befehle geben einen Bericht mit entdeckten, importierten und fehlgeschlagenen Quellen aus.

Vor einem grossen Lauf prueft ein begrenzter Trockenlauf die Discovery ohne Datenbankaenderung:

```bash
make bundestag-import DRY_RUN=1 LIMIT=5
```

## Quellenabruf

```bash
make crawler-fetch URL=https://www.bundestag.de/
```

Der Abruf speichert die unveraenderte Antwort in `var/source-archive/<hash-prefix>/<sha256>`. Das Verzeichnis ist lokal ignoriert und muss im Betrieb zusammen mit der Datenbank gesichert werden.

## Abgeordnetenbiografie

```bash
make member-import URL=https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330
```

Der Import nutzt die MDB-ID aus der amtlichen Biografie-URL. Er speichert Profilsnapshots, Bundestags- und Wahlkreisbuero-Adressen, Kontaktformular, externe Profil-Links, Wahlkreismandat und strukturierte Bundestagsrollen. Wiederholte Imports gleicher Fachwerte erzeugen keine doppelten Fakten.

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