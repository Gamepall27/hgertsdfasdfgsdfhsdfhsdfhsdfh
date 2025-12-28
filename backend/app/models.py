from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class RoleEnum(str, Enum):
    player = "player"
    admin = "admin"
    treasurer = "treasurer"


class EventType(str, Enum):
    training = "training"
    match = "match"
    event = "event"


class ResponseStatus(str, Enum):
    accepted = "accepted"
    tentative = "tentative"
    declined = "declined"


class DrinkOrderMode(str, Enum):
    qr = "qr"
    kiosk = "kiosk"
    app = "app"


class LedgerEntryType(str, Enum):
    credit = "credit"
    debit = "debit"


class SubscriptionInterval(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


class SubscriptionStatus(str, Enum):
    active = "active"
    canceled = "canceled"
    trial = "trial"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[EmailStr] = Field(default=None, index=True, unique=True)
    player_number: Optional[str] = Field(default=None, index=True, unique=True)
    display_name: str
    role: RoleEnum = Field(default=RoleEnum.player, index=True)
    balance_cents: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    event_type: EventType
    location: Optional[str] = None
    starts_at: datetime
    ends_at: Optional[datetime] = None
    requires_response: bool = False
    notes_allowed: bool = True
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")


class EventResponse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    user_id: int = Field(foreign_key="user.id")
    response: ResponseStatus
    note: Optional[str] = None
    responded_at: datetime = Field(default_factory=datetime.utcnow)


class Drink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price_cents: int = 0
    stock: int = 0


class DrinkOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    drink_id: int = Field(foreign_key="drink.id")
    user_id: int = Field(foreign_key="user.id")
    event_id: Optional[int] = Field(default=None, foreign_key="event.id")
    quantity: int = 1
    mode: DrinkOrderMode = Field(default=DrinkOrderMode.app)
    ordered_at: datetime = Field(default_factory=datetime.utcnow)


class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    amount_cents: int
    entry_type: LedgerEntryType
    category: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Fine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    amount_cents: int
    description: Optional[str] = None


class AssignedFine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fine_id: int = Field(foreign_key="fine.id")
    user_id: int = Field(foreign_key="user.id")
    event_id: Optional[int] = Field(default=None, foreign_key="event.id")
    assigned_by: Optional[int] = Field(default=None, foreign_key="user.id")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)


class Lineup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    name: str
    formation: Optional[str] = None
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")


class LineupSlot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lineup_id: int = Field(foreign_key="lineup.id")
    user_id: int = Field(foreign_key="user.id")
    position_label: Optional[str] = None


class LiveTickerEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    minute: int
    event_type: str
    description: Optional[str] = None
    team_for: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    interval: SubscriptionInterval
    price_cents: int
    features: Optional[str] = None


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    plan_id: int = Field(foreign_key="subscriptionplan.id")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.trial)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class ClubSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    club_name: str
    default_response_required: bool = True
    allow_notes_on_responses: bool = True
    dues_interval: SubscriptionInterval = Field(default=SubscriptionInterval.monthly)
    dues_amount_cents: int = 0
