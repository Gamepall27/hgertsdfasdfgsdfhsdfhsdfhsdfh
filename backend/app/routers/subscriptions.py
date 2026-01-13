from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import require_role
from ..models import ClubSettings, RoleEnum, Subscription, SubscriptionPlan, SubscriptionStatus, User

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=list[SubscriptionPlan])
def list_plans(session: Session = Depends(get_session)) -> list[SubscriptionPlan]:
    return session.exec(select(SubscriptionPlan)).all()


@router.post("/plans", response_model=SubscriptionPlan, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan: SubscriptionPlan,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin,))),
) -> SubscriptionPlan:
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


@router.post("", response_model=Subscription, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription: Subscription,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> Subscription:
    plan = session.get(SubscriptionPlan, subscription.plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription


@router.post("/{subscription_id}/cancel", response_model=Subscription)
def cancel_subscription(
    subscription_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin,))),
) -> Subscription:
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    subscription.status = SubscriptionStatus.canceled
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription


@router.get("/settings", response_model=ClubSettings)
def get_settings(session: Session = Depends(get_session)) -> ClubSettings:
    settings = session.exec(select(ClubSettings)).first()
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club settings missing")
    return settings


@router.put("/settings", response_model=ClubSettings)
def update_settings(
    settings: ClubSettings,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> ClubSettings:
    existing = session.get(ClubSettings, settings.id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club settings missing")
    for field, value in settings.dict(exclude_unset=True).items():
        setattr(existing, field, value)
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing
