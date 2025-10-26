"""
Schémas Pydantic pour les commandes
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class ShippingAddress(BaseModel):
    """Adresse de livraison"""
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=8, max_length=20)
    address: str = Field(..., min_length=10)
    city: str = Field(..., min_length=2, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    country: str = Field(default="Côte d'Ivoire", max_length=50)


class BillingAddress(BaseModel):
    """Adresse de facturation (optionnelle)"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=50)


class OrderItemCreate(BaseModel):
    """Article à commander"""
    product_id: int
    quantity: int = Field(..., ge=1)
    variant_id: Optional[int] = None


class OrderCreate(BaseModel):
    """Créer une nouvelle commande"""
    items: List[OrderItemCreate] = Field(..., min_items=1)
    shipping_address: ShippingAddress
    billing_address: Optional[BillingAddress] = None
    customer_notes: Optional[str] = None
    coupon_code: Optional[str] = None
    payment_method: str = Field(..., description="orange_money, mtn_money, moov_money, wave, credit_card, cash_on_delivery")


class OrderItemResponse(BaseModel):
    """Article d'une commande"""
    order_item_id: int
    product_id: int
    product_name: str
    product_sku: Optional[str]
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    variant_info: Optional[str]
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Détail complet d'une commande"""
    order_id: int
    order_number: str
    status: str
    payment_status: str
    
    # Livraison
    shipping_first_name: str
    shipping_last_name: str
    shipping_email: str
    shipping_phone: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: Optional[str]
    shipping_country: str
    
    # Montants
    subtotal: Decimal
    shipping_cost: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    
    # Items
    items: List[OrderItemResponse]
    
    # Dates
    created_at: datetime
    confirmed_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    # Suivi
    tracking_number: Optional[str]
    carrier: Optional[str]
    
    # Notes
    customer_notes: Optional[str]
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Commande dans la liste (vue simplifiée)"""
    order_id: int
    order_number: str
    status: str
    payment_status: str
    total_amount: Decimal
    items_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Mettre à jour le statut d'une commande (admin uniquement)"""
    status: Optional[str] = Field(None, pattern="^(pending|confirmed|processing|shipped|delivered|cancelled|refunded)$")
    payment_status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed|refunded)$")
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    admin_notes: Optional[str] = None
