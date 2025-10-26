"""
Authentification JWT pour les clients de la boutique
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

from app.database import get_db
from boutique.backend.models.customer import StoreCustomer

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-please-use-strong-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours

# Context pour le hashing des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hasher un mot de passe"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)


def create_customer_token(customer_id: int, email: str) -> str:
    """Créer un token JWT pour un client"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(customer_id),
        "email": email,
        "type": "customer",  # Pour différencier des tokens admin
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_customer_token(token: str) -> Optional[dict]:
    """Vérifier et décoder un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id: str = payload.get("sub")
        email: str = payload.get("email")
        token_type: str = payload.get("type")
        
        if customer_id is None or email is None or token_type != "customer":
            return None
            
        return {"customer_id": int(customer_id), "email": email}
    except JWTError:
        return None


async def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> StoreCustomer:
    """Obtenir le client actuellement connecté"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = verify_customer_token(token)
    
    if token_data is None:
        raise credentials_exception
    
    customer = db.query(StoreCustomer).filter(
        StoreCustomer.customer_id == token_data["customer_id"]
    ).first()
    
    if customer is None:
        raise credentials_exception
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    return customer


async def get_current_customer_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[StoreCustomer]:
    """Obtenir le client actuellement connecté (optionnel, ne lève pas d'erreur)"""
    if not credentials:
        return None
    
    try:
        return await get_current_customer(credentials, db)
    except HTTPException:
        return None
