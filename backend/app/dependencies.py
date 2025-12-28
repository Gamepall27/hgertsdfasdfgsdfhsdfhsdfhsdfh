from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from .database import get_session
from .models import RoleEnum, User


def get_current_user(
    session: Session = Depends(get_session),
    x_user_id: int | None = Header(default=None, convert_underscores=False),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Id header required")
    user = session.get(User, x_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def require_role(required_roles: tuple[RoleEnum, ...]):
    def wrapper(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return wrapper


def ensure_user_exists(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_user_by_email_or_number(session: Session, identifier: str) -> User | None:
    stmt = select(User).where((User.email == identifier) | (User.player_number == identifier))
    return session.exec(stmt).first()
