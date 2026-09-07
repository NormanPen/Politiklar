---
name: rag-evidence-review
description: >-
  Prüft native RAG-Retrieval-, Chunking-, Embedding-, Ranking-, Zitations- und Antwortgenerierungslogiken
  auf Belegevidenz, Reproduzierbarkeit und Halluzinationsresistenz. Nutze diesen Skill beim Entwerfen
  oder Reviewen der RAG-Pipeline, von Vektorsuchen, Prompt-Templates oder Zitationsmechanismen.
---

# RAG & Evidenz-Review für Politiklar

Politiklar vermittelt politische Fakten. Eine RAG-Pipeline darf daher niemals spekulieren, extrapolieren oder unbelegte Behauptungen aufstellen. Dieser Skill leitet das Design und Review von Retrieval-, Kontextbau- und Generierungsfunktionen an.

## Wann zu verwenden

- Beim Entwurf oder der Erweiterung der RAG- und Vektordatenbank-Architektur (z. B. mit `pgvector` oder Qdrant).
- Beim Ändern von Chunking-Strategien für parlamentarische Protokolle, Drucksachen oder Biografien.
- Bei der Gestaltung von Prompt-Templates und Antwortschemata für generative Modelle.
- Bei der Implementierung von Zitations- und Quellenverlinkungen in der Webanwendung oder Backend-API.

---

## Prüf- und Entwurfsrichtlinien

### 1. Chunking mit Erhalt des politischen Kontexts
- **Metadaten nicht verlieren**: Ein Textabschnitt aus einem Plenarprotokoll oder einer Drucksache darf beim Chunking nicht aus dem Zusammenhang gerissen werden.
- Jeder Chunk muss mindestens folgende Metadaten tragen:
  - `source_document_id`: Fremdschlüssel auf die amtliche Primärquelle.
  - `document_title` / `source_url`: Direkte Nachvollziehbarkeit für den Nutzer.
  - `electoral_term` / `sitting_number` / `date`: Zeitliche und parlamentarische Verortung.
  - `speaker_name` / `speaker_role`: Wer hat gesprochen (bzw. wer hat den Antrag eingebracht).
  - `section_heading`: Kontext der Debatte oder Tagesordnungspunkt (TOP).

### 2. Striktes Insufficient-Evidence-Handling
- Wenn keine relevanten Chunks gefunden werden oder die gefundenen Belege die Frage nicht eindeutig beantworten, **muss** das System ablehnen:
  - *"Auf Basis der amtlichen Quellen des Deutschen Bundestages liegen hierzu keine ausreichenden Belege vor."*
- Prompts müssen so instruiert sein, dass Allgemeinwissen aus den Modellgewichten **nicht** zur Ergänzung politischer Aussagen herangezogen wird, sofern kein Beleg im Kontext vorhanden ist.

### 3. Zitationsgenauigkeit (Claim-Level Grounding)
- Jede Tatsachenbehauptung in einer generierten Antwort muss mit einem konkreten Quellenverweis versehen sein (z. B. `[Plenarprotokoll 21/90, S. 1234]`).
- Reine Zitationsanhänge am Ende des Textes reichen nicht aus; die Verbindung zwischen Behauptung und Nachweis muss eindeutig sein.

### 4. Politische Neutralität & Tonalität
- Keine Partei-Bias oder bewertende Adjektive ("skandalös", "überraschend", "erfolgreich").
- Sachliche Wiedergabe von Reden und Abstimmungen im Konjunktiv bzw. mit klarer Urheberzuordnung ("Abgeordneter X argumentierte...", "Die Fraktion Y stimmte mit Nein").

### 5. Reproduzierbare Evaluation
- Evaluierung von RAG-Änderungen über feste Testdatensätze (Ground-Truth-Fragen mit definierten Belegstellen).
- Überprüfung von Edge Cases:
  - Fangfragen ohne Quellengrundlage.
  - Fragen zu widersprüchlichen Aussagen verschiedener Fraktionen.
  - Fragen zu noch nicht verifizierten Sprecherzuordnungen.

