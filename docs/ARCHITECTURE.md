# Architektur-Notizen (Prototyp)

Dieses Dokument fasst zusammen, wie der Prototyp die Anforderungen der Vereins-App abbildet und welche Erweiterungen vorgesehen sind.

## Laufzeit
- **Node.js HTTP-Server** ohne externe Abhängigkeiten.
- In-Memory-Datenhaltung in `src/data.js`. Persistenz (DB) kann später angeschlossen werden.
- Start: `node src/server.js` (Port 3000).

## Domänenobjekte (In-Memory)
- **User**: `id`, `name`, `email`, `playerNumber`, `role` (player/admin/treasurer), `wallet`.
- **Events**: Trainings, Spiele, Events mit `responses` (Zusagen/Absagen/Unsicher) und `lineup`.
- **Drinks**: Produktkatalog + Buchungen -> reduzieren Bestand, schreiben Kassenbuch.
- **Ledger**: Einnahmen/Ausgaben inkl. Startbestand, Strafen, Getränke.
- **Fines**: Strafenkatalog + Zuordnung erzeugt Ledger-Eintrag.
- **LiveTicker**: Matches inkl. Ereignissen (Tor, Karte, Wechsel etc.).
- **Subscriptions**: Vereinsabos (plan, interval, seats).

## Wichtige Routen (Mapping zur Anforderung)
- **Benutzer & Rollen**: `/api/users`, `/api/roles`, `/api/auth/login`, `/api/users/:id/role`
- **Termine & Rückmeldungen**: `/api/events`, `/api/events/:id/rsvp`, `/api/events/:id/lineup`
- **Getränke**: `/api/drinks`, `/api/drinks/:id/book`
- **Kasse**: `/api/ledger`, `/api/wallet/:userId`, `/api/dashboard`
- **Strafen**: `/api/fines`, `/api/fines/:id/assign`
- **Statistik**: `/api/stats`
- **Live-Ticker**: `/api/live/:matchId`
- **Abo-Modell**: `/api/subscriptions`

## Erweiterungsideen
- **Persistenz & Modelle**: ORM (z. B. Prisma) + SQLite/PostgreSQL; Migrationen + Seeds.
- **Auth & Berechtigungen**: JWT-basierte Sessions, Rechteprüfung pro Route.
- **Importe**: Football-API-Import für Spielpläne.
- **Benachrichtigungen**: E-Mail/Push für Zusagen, Zahlungserinnerungen, Live-Ticker-Events.
- **Mobile UI**: React Native/Flutter-App, die die genannten Endpunkte konsumiert (Dashboard, Events, Team, Kasse, Profil).
- **Kioskmodus**: Spezielle Route/UI für schnelle Getränkebuchung per Spielernummer/QR.
- **Werbung**: Feature-Flag + Platzhalter-Endpoints für Ad-Konfiguration.

## Beispiel-Flows
- **Rückmeldung zu Termin**: App ruft `POST /api/events/:id/rsvp` mit `userId` und `status` auf → Status wird gespeichert, Statistik aktualisiert.
- **Getränk buchen**: App ruft `POST /api/drinks/:id/book` auf → Bestand verringert, Ledger-Eintrag erzeugt, Wallet des Spielers angepasst.
- **Strafe vergeben**: Kassenwart ruft `POST /api/fines/:id/assign` auf → Ledger-Eintrag mit negativem Betrag.
- **Live-Ticker**: Während eines Spiels ruft der Betreuer `POST /api/live/:matchId` mehrfach auf → Score aktualisiert, Ereignisliste wächst; Zuschauer lesen via `GET /api/live/:matchId`.

## Test-Hinweise
- Alle Endpunkte geben JSON zurück und erlauben CORS für einfache Frontend-Integration.
- Da keine DB genutzt wird, lassen sich Requests direkt per `curl` oder REST-Client ausprobieren.
