"""
Schémas Pydantic pour les clients de la boutique
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class CustomerRegister(BaseModel):
    """Inscription d'un nouveau client"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 caractères")
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    newsletter_subscribed: bool = False
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une lettre')
        if not re.search(r'\d', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[0-9\s\-\(\)]{8,20}$', v):
            raise ValueError('Numéro de téléphone invalide')
        return v


class CustomerLogin(BaseModel):
    """Connexion client"""
    email: EmailStr
    password: str


class CustomerUpdate(BaseModel):
    """Mise à jour du profil client"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=50)
    newsletter_subscribed: Optional[bool] = None


class CustomerResponse(BaseModel):
    """Réponse avec les données du client"""
    customer_id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    newsletter_subscribed: bool
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Réponse avec le token JWT"""
    access_token: str
    token_type: str = "bearer"
    customer: CustomerResponse
