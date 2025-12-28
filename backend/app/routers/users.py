from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import get_current_user, require_role
from ..database import get_session
from ..models import RoleEnum, User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[User])
def list_users(session: Session = Depends(get_session)) -> list[User]:
    return session.exec(select(User)).all()


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, session: Session = Depends(get_session)) -> User:
    if user.email:
        existing_email = session.exec(select(User).where(User.email == user.email)).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if user.player_number:
        existing_number = session.exec(select(User).where(User.player_number == user.player_number)).first()
        if existing_number:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Player number already registered")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/assign-role/{user_id}", response_model=User)
def assign_role(
    user_id: int,
    role: RoleEnum,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin,))),
) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_user.role = role
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/me", response_model=User)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/lookup/{identifier}", response_model=User)
def lookup(identifier: str, session: Session = Depends(get_session)) -> User:
    stmt = select(User).where((User.email == identifier) | (User.player_number == identifier))
    user = session.exec(stmt).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
