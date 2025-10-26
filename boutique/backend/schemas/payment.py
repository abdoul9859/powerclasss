"""
Schémas Pydantic pour les paiements
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class PaymentInitiate(BaseModel):
    """Initier un paiement"""
    order_id: int
    payment_method: str = Field(..., description="orange_money, mtn_money, moov_money, wave, credit_card")
    phone_number: Optional[str] = Field(None, description="Numéro Mobile Money")
    return_url: Optional[str] = Field(None, description="URL de retour après paiement")


class PaymentResponse(BaseModel):
    """Réponse après initiation de paiement"""
    payment_id: int
    payment_reference: str
    status: str
    amount: Decimal
    currency: str
    payment_method: str
    payment_url: Optional[str] = None  # URL de paiement (pour carte bancaire)
    ussd_code: Optional[str] = None    # Code USSD (pour Mobile Money)
    instructions: Optional[str] = None  # Instructions de paiement
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentCallback(BaseModel):
    """Callback du fournisseur de paiement"""
    payment_reference: str
    provider_transaction_id: str
    status: str
    amount: Optional[Decimal] = None
    provider_response: Optional[dict] = None


class PaymentVerify(BaseModel):
    """Vérifier le statut d'un paiement"""
    payment_reference: str
