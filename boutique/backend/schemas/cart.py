"""
Schémas Pydantic pour le panier
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class AddToCartRequest(BaseModel):
    """Ajouter un produit au panier"""
    product_id: int
    quantity: int = Field(..., ge=1, description="Quantité doit être >= 1")
    variant_id: Optional[int] = None


class CartItem(BaseModel):
    """Article dans le panier"""
    product_id: int
    product_name: str
    product_image: Optional[str]
    sku: Optional[str]
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    variant_id: Optional[int] = None
    variant_info: Optional[dict] = None
    in_stock: bool
    available_quantity: int


class CartResponse(BaseModel):
    """Panier complet"""
    items: List[CartItem]
    subtotal: Decimal
    shipping_cost: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    total: Decimal
    items_count: int


class UpdateCartItemRequest(BaseModel):
    """Mettre à jour la quantité d'un article"""
    quantity: int = Field(..., ge=0, description="0 pour supprimer l'article")
