from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import get_current_user, require_role
from ..models import Drink, DrinkOrder, DrinkOrderMode, RoleEnum, User

router = APIRouter(prefix="/drinks", tags=["drinks"])


@router.get("", response_model=list[Drink])
def list_drinks(session: Session = Depends(get_session)) -> list[Drink]:
    return session.exec(select(Drink)).all()


@router.post("", response_model=Drink, status_code=status.HTTP_201_CREATED)
def create_drink(
    drink: Drink,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> Drink:
    session.add(drink)
    session.commit()
    session.refresh(drink)
    return drink


@router.post("/{drink_id}/book", response_model=DrinkOrder, status_code=status.HTTP_201_CREATED)
def book_drink(
    drink_id: int,
    quantity: int = 1,
    mode: DrinkOrderMode = DrinkOrderMode.app,
    event_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DrinkOrder:
    drink = session.get(Drink, drink_id)
    if not drink:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drink not found")
    if drink.stock < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")

    drink.stock -= quantity
    order = DrinkOrder(drink_id=drink_id, user_id=current_user.id, quantity=quantity, mode=mode, event_id=event_id)
    session.add(order)
    session.add(drink)
    session.commit()
    session.refresh(order)
    return order


@router.get("/stats", response_model=dict)
def drink_stats(session: Session = Depends(get_session)) -> dict:
    orders = session.exec(select(DrinkOrder)).all()
    stats: dict[int, int] = {}
    for order in orders:
        stats[order.drink_id] = stats.get(order.drink_id, 0) + order.quantity
    return {"ordered": stats}
