from datetime import datetime, timedelta

from sqlmodel import Session, select

from .models import (
    ClubSettings,
    Drink,
    Event,
    EventType,
    Fine,
    RoleEnum,
    SubscriptionInterval,
    SubscriptionPlan,
    User,
)


def seed(session: Session) -> None:
    if session.exec(select(User)).first():
        return

    admin = User(display_name="Admin", email="admin@example.com", role=RoleEnum.admin)
    treasurer = User(display_name="Kassenwart", email="cash@example.com", role=RoleEnum.treasurer)
    player = User(display_name="Max Mustermann", email="player@example.com", player_number="9")
    session.add_all([admin, treasurer, player])

    now = datetime.utcnow()
    training = Event(
        title="Wöchentliches Training",
        event_type=EventType.training,
        location="Sportplatz Hauptstraße",
        starts_at=now + timedelta(days=2),
        ends_at=now + timedelta(days=2, hours=2),
        requires_response=True,
        notes_allowed=True,
        created_by=1,
    )
    match = Event(
        title="Spiel gegen FC Stadtmitte",
        event_type=EventType.match,
        location="Sportpark Zentrum",
        starts_at=now + timedelta(days=5),
        ends_at=now + timedelta(days=5, hours=2),
        requires_response=True,
        notes_allowed=True,
        created_by=1,
    )
    session.add_all([training, match])

    session.add_all(
        [
            Drink(name="Wasser", price_cents=150, stock=50),
            Drink(name="Isodrink", price_cents=300, stock=30),
        ]
    )

    session.add_all(
        [
            Fine(title="Zu spät gekommen", amount_cents=500),
            Fine(title="Trainingsausfall ohne Absage", amount_cents=1000),
        ]
    )

    session.add_all(
        [
            SubscriptionPlan(
                name="Basic",
                interval=SubscriptionInterval.monthly,
                price_cents=0,
                features="Begrenzte Teams, keine Kassenstatistiken",
            ),
            SubscriptionPlan(
                name="Premium",
                interval=SubscriptionInterval.monthly,
                price_cents=1299,
                features="Alle Funktionen freigeschaltet",
            ),
        ]
    )

    session.add(ClubSettings(club_name="Verein 24", dues_amount_cents=500))

    session.commit()
