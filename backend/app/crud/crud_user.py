from datetime import datetime, timedelta
import secrets
from typing import Any, Dict, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password, decode_token
from app.core.config import settings
from app.core.deps import get_db, oauth2_scheme
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class CRUDUser:
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()
    
    def create(self, db: Session, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            verification_token=secrets.token_urlsafe(32)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        for field, value in update_data.items():
            if field != "hashed_password" and hasattr(db_obj, field):
                setattr(db_obj, field, value)
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        return user.is_active
    
    def is_verified(self, user: User) -> bool:
        return user.is_verified

    def get_current_user(
        self, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
    ) -> User:
        """
        Get the current authenticated user.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        token_data = decode_token(token)
        if not token_data:
            raise credentials_exception
        
        user = self.get_by_id(db, int(token_data.sub))
        if not user:
            raise credentials_exception
        if not self.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user
    
    def verify_email(self, db: Session, token: str) -> Optional[User]:
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            return None
        
        user.is_verified = True
        user.verification_token = None
        db.commit()
        db.refresh(user)
        return user
    
    def create_password_reset_token(self, user: User) -> str:
        reset_token = secrets.token_urlsafe(32)
        user.reset_password_token = reset_token
        user.reset_password_expires = datetime.utcnow() + timedelta(hours=24)
        return reset_token
    
    def reset_password(self, db: Session, token: str, new_password: str) -> Optional[User]:
        user = db.query(User).filter(
            User.reset_password_token == token,
            User.reset_password_expires > datetime.utcnow()
        ).first()
        
        if not user:
            return None
        
        user.hashed_password = get_password_hash(new_password)
        user.reset_password_token = None
        user.reset_password_expires = None
        
        db.commit()
        db.refresh(user)
        return user

crud_user = CRUDUser() 