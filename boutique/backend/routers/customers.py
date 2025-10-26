"""
API d'authentification et gestion des clients
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from boutique.backend.models.customer import StoreCustomer
from boutique.backend.schemas.customer import (
    CustomerRegister,
    CustomerLogin,
    CustomerResponse,
    CustomerUpdate,
    TokenResponse
)
from boutique.backend.utils.auth import (
    hash_password,
    verify_password,
    create_customer_token,
    get_current_customer
)

router = APIRouter(prefix="/api/store/customers", tags=["store-customers"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_customer(
    customer_data: CustomerRegister,
    db: Session = Depends(get_db)
):
    """
    Inscription d'un nouveau client
    """
    # Vérifier si l'email existe déjà
    existing_customer = db.query(StoreCustomer).filter(
        StoreCustomer.email == customer_data.email
    ).first()
    
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Créer le nouveau client
    new_customer = StoreCustomer(
        email=customer_data.email,
        password_hash=hash_password(customer_data.password),
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        phone=customer_data.phone,
        newsletter_subscribed=customer_data.newsletter_subscribed,
        is_active=True,
        email_verified=False
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Créer le token JWT
    access_token = create_customer_token(new_customer.customer_id, new_customer.email)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        customer=CustomerResponse.from_orm(new_customer)
    )


@router.post("/login", response_model=TokenResponse)
async def login_customer(
    credentials: CustomerLogin,
    db: Session = Depends(get_db)
):
    """
    Connexion d'un client
    """
    # Trouver le client
    customer = db.query(StoreCustomer).filter(
        StoreCustomer.email == credentials.email
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Vérifier le mot de passe
    if not verify_password(credentials.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Vérifier si le compte est actif
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte a été désactivé. Contactez le support."
        )
    
    # Mettre à jour la date de dernière connexion
    customer.last_login = datetime.now()
    db.commit()
    
    # Créer le token JWT
    access_token = create_customer_token(customer.customer_id, customer.email)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        customer=CustomerResponse.from_orm(customer)
    )


@router.get("/me", response_model=CustomerResponse)
async def get_current_customer_info(
    current_customer: StoreCustomer = Depends(get_current_customer)
):
    """
    Obtenir les informations du client connecté
    """
    return CustomerResponse.from_orm(current_customer)


@router.put("/me", response_model=CustomerResponse)
async def update_customer_profile(
    update_data: CustomerUpdate,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour le profil du client
    """
    # Mettre à jour les champs fournis
    if update_data.first_name is not None:
        current_customer.first_name = update_data.first_name
    if update_data.last_name is not None:
        current_customer.last_name = update_data.last_name
    if update_data.phone is not None:
        current_customer.phone = update_data.phone
    if update_data.address is not None:
        current_customer.address = update_data.address
    if update_data.city is not None:
        current_customer.city = update_data.city
    if update_data.postal_code is not None:
        current_customer.postal_code = update_data.postal_code
    if update_data.country is not None:
        current_customer.country = update_data.country
    if update_data.newsletter_subscribed is not None:
        current_customer.newsletter_subscribed = update_data.newsletter_subscribed
    
    current_customer.updated_at = datetime.now()
    
    db.commit()
    db.refresh(current_customer)
    
    return CustomerResponse.from_orm(current_customer)


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Changer le mot de passe du client
    """
    # Vérifier l'ancien mot de passe
    if not verify_password(old_password, current_customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect"
        )
    
    # Valider le nouveau mot de passe
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit contenir au moins 8 caractères"
        )
    
    # Mettre à jour le mot de passe
    current_customer.password_hash = hash_password(new_password)
    current_customer.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès"}
