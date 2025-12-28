# Vereins-App Backend (MVP Skeleton)

Dieses Repository enthält ein initiales Backend-Grundgerüst (FastAPI + SQLModel) für eine Vereins-App ähnlich SpielerPlus mit erweiterten Funktionen. Der Fokus liegt auf klaren Domänen-Modellen, sinnvollen API-Endpunkten und einer einfachen lokalen Ausführbarkeit. Ein mobiles Frontend ist noch nicht enthalten; das Backend ist so aufgebaut, dass es von einer React Native / Flutter App genutzt werden kann.

## Features (MVP)
- **Benutzer- & Rollenverwaltung**: Spieler, Admin, Kassenwart. Zuordnung über einfache API.
- **Terminverwaltung**: Erstellung von Terminen (Training/Spiel/Event), Rückmeldungen (Zusage/Vielleicht/Absage) inkl. optionaler Notiz.
- **Aufstellungen**: Zuordnung von Spielern zu einem Spiel inkl. Formation-Label.
- **Getränkeverwaltung**: Katalog und Buchungen; Kassenwart sieht bestellte Mengen.
- **Kassenverwaltung**: Einnahmen/Ausgaben, Salden pro Spieler, Historie über Ledger-Einträge.
- **Strafenverwaltung**: Katalog an Strafen, Zuordnung zu Spielern, automatische Verbuchung in der Kasse.
- **Live-Ticker**: Events wie Tor, Karte, Wechsel; Spielstand-Aggregation pro Spiel.
- **Abomodelle & Vereinseinstellungen**: Basis-Modelle für Pläne und konfigurierbare Regeln (Pflicht-Rückmeldung, Beitragsintervalle etc.).

## Schnellstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn backend.app.main:app --reload
```

Öffne dann `http://127.0.0.1:8000/docs` für die automatisch erzeugte Swagger-UI.

## Tests
```bash
pytest
```

## Projektstruktur
```
backend/
  app/
    main.py            # FastAPI-Instanz, Router-Registrierung
    database.py        # Engine & Session-Handling
    models.py          # SQLModel-Domänen-Modelle & Enums
    seed.py            # Beispiel-Daten
    routers/
      users.py         # Benutzer & Rollen
      events.py        # Termine & Rückmeldungen
      drinks.py        # Getränke & Buchungen
      ledger.py        # Kassen-Einträge & Salden
      fines.py         # Strafen & automatische Verbuchung
      lineups.py       # Aufstellungs-Planung
      ticker.py        # Live-Ticker-Events & Spielstände
      subscriptions.py # Abo & Vereinseinstellungen
  tests/
    test_flows.py      # Basis-Ende-zu-Ende-Flows
```

## Annahmen & nächste Schritte
- Authentifizierung ist als einfacher Header (`X-User-Id`) gelöst; echte JWT/OAuth sollten nachgerüstet werden.
- SQLite wird lokal genutzt; für Produktion Postgres + Migrationen (z. B. Alembic) einführen.
- Frontend fehlt noch; Schnittstellen sind für mobile Clients ausgelegt.
- Für Fußball-spezifische Felder (Liga, Gegner, Halbzeiten) sind Platzhalter enthalten und können erweitert werden.

## Lizenz
MIT
