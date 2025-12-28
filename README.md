# Vereins-App (Backend-Prototyp)

Dieses Repository enthält einen leichtgewichtigen API-Prototypen, der die Kernfunktionen der beschriebenen Vereins-App (ähnlich SpielerPlus, aber erweitert) demonstriert. Der Server ist vollständig in Node.js (ohne externe Abhängigkeiten) implementiert und stellt einfache Endpunkte für Benutzer‑, Termin‑, Getränke‑, Kassen‑, Straf‑ und Live‑Ticker-Workflows bereit.

> Hinweis: Dies ist ein lauffähiger Prototyp mit In-Memory-Daten. Beim Neustart des Servers gehen Daten verloren. Er eignet sich als Ausgangspunkt für die Weiterentwicklung (Persistenz, Auth, Mobile-App-Anbindung).

## Quickstart

```bash
# Server starten
node src/server.js
# Standard-Port: 3000
```

Gesundheitscheck:
```bash
curl http://localhost:3000/api/health
```

## Wichtige Endpunkte (Auszug)

- **Benutzer & Rollen**
  - `GET /api/users` – alle Nutzer
  - `POST /api/users` – neuen Nutzer anlegen (`name`, `email`, `playerNumber`, optional `role`)
  - `PATCH /api/users/:id/role` – Rolle setzen (player, admin, treasurer)
  - `POST /api/auth/login` – Dummy-Login über E-Mail oder Spielernummer
  - `GET /api/roles` – verfügbare Rollen

- **Termine & Aufstellungen**
  - `GET /api/events` – Liste aller Termine (Training/Spiel/Event)
  - `POST /api/events` – Termin anlegen (`type`, `title`, `location`, `dateTime`)
  - `POST /api/events/:id/rsvp` – Rückmeldung setzen (`userId`, `status`, optional `note`)
  - `POST /api/events/:id/lineup` – Aufstellung pflegen (`lineup: [userId, ...]`)

- **Getränke & Kasse**
  - `GET /api/drinks` – Getränkeprodukte
  - `POST /api/drinks` – Produkt anlegen (`name`, `price`, optional `stock`)
  - `POST /api/drinks/:id/book` – Buchung (`userId`, `quantity`), reduziert Bestand & schreibt Kassenbuch
  - `GET /api/ledger` – Kassenbuch-Einträge
  - `POST /api/ledger` – manueller Kassenbucheintrag (`userId`, `kind`, `description`, `amount`)
  - `GET /api/wallet/:userId` – Nutzer-Guthaben & dessen Einträge

- **Strafen**
  - `GET /api/fines` – Strafenkatalog
  - `POST /api/fines/:id/assign` – Strafe einem Spieler zuordnen (`userId`)

- **Live-Ticker & Statistik**
  - `GET /api/live/:matchId` – Live-Daten eines Spiels
  - `POST /api/live/:matchId` – Ereignis protokollieren (z. B. `{ type: "goal", team: "home", minute: 12, player: "Müller" }`)
  - `GET /api/stats` – Attendance-, Getränke- und Guthabenstatistiken
  - `GET /api/dashboard` – Kompakte Übersicht (nächster Termin, offene Rückmeldungen, Kassenstand, Live-Spiel)

- **Subscriptions**
  - `GET /api/subscriptions` – gebuchte Vereinsabos
  - `POST /api/subscriptions` – neues Abo anlegen (`club`, `plan`, `interval`, optional `seats`)

## Datenmodell (In-Memory)

Alle Daten liegen in `src/data.js` und können dort als Startbefüllung angepasst werden:
- Nutzer inkl. Spielernummer, Rolle und Guthaben
- Termine mit Responses und Aufstellung
- Getränkekatalog inkl. Beständen und Buchungen
- Kassenbuch (Einnahmen/Ausgaben inkl. Strafen und Getränke)
- Strafenkatalog
- Live-Ticker-Ereignisse
- Abonnements

## Nächste Schritte

- Persistenzschicht (z. B. SQLite/PostgreSQL + ORM) ergänzen
- Echte Authentifizierung (Tokens, Passwörter, Rollenrechte)
- Mobile-Client (React Native/Flutter) anbinden
- Hintergrundjobs (Zahlungserinnerungen, Spiel-Importe) implementieren
- Testsuite & CI-Linting hinzufügen
