"""
API de gestion du panier
Note: Le panier est géré côté client (localStorage) pour les visiteurs non connectés.
Cette API sert principalement à valider les données et calculer les totaux.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.database import get_db, Product
from boutique.backend.schemas.cart import (
    CartItem,
    CartResponse,
    AddToCartRequest
)

router = APIRouter(prefix="/api/store/cart", tags=["store-cart"])


@router.post("/validate", response_model=CartResponse)
async def validate_cart(
    items: List[AddToCartRequest],
    db: Session = Depends(get_db)
):
    """
    Valider un panier et calculer les totaux
    
    Cette endpoint vérifie:
    - Que les produits existent
    - Que les quantités sont disponibles
    - Calcule les prix actuels
    - Retourne le panier validé avec les totaux
    """
    if not items:
        return CartResponse(
            items=[],
            subtotal=Decimal("0"),
            shipping_cost=Decimal("0"),
            tax_amount=Decimal("0"),
            discount_amount=Decimal("0"),
            total=Decimal("0"),
            items_count=0
        )
    
    cart_items = []
    subtotal = Decimal("0")
    
    for item in items:
        # Récupérer le produit
        product = db.query(Product).filter(
            Product.product_id == item.product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Produit {item.product_id} non trouvé"
            )
        
        # Vérifier la disponibilité
        available_quantity = product.stock_quantity
        in_stock = available_quantity > 0
        
        # Limiter la quantité à ce qui est disponible
        quantity = min(item.quantity, available_quantity) if in_stock else 0
        
        if quantity == 0 and item.quantity > 0:
            # Produit en rupture de stock
            pass  # On l'ajoute quand même mais avec quantity=0
        
        # Calculer le sous-total de l'article
        item_subtotal = product.price * quantity
        subtotal += item_subtotal
        
        cart_items.append(CartItem(
            product_id=product.product_id,
            product_name=product.name,
            product_image=product.image,
            sku=product.sku,
            unit_price=product.price,
            quantity=quantity,
            subtotal=item_subtotal,
            variant_id=item.variant_id,
            variant_info=None,  # TODO: Charger les infos de variante
            in_stock=in_stock,
            available_quantity=available_quantity
        ))
    
    # Calculer les frais de livraison (exemple: gratuit au-dessus de 50000 FCFA)
    shipping_cost = Decimal("0")
    if subtotal > 0 and subtotal < 50000:
        shipping_cost = Decimal("2000")  # 2000 FCFA de frais de livraison
    
    # Calculer les taxes (exemple: pas de TVA en Côte d'Ivoire pour les produits)
    tax_amount = Decimal("0")
    
    # Réductions (à implémenter avec les codes promo)
    discount_amount = Decimal("0")
    
    # Total final
    total = subtotal + shipping_cost + tax_amount - discount_amount
    
    return CartResponse(
        items=cart_items,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total=total,
        items_count=len([item for item in cart_items if item.quantity > 0])
    )


@router.post("/check-availability/{product_id}")
async def check_product_availability(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    """
    Vérifier la disponibilité d'un produit
    """
    product = db.query(Product).filter(
        Product.product_id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    available = product.stock_quantity >= quantity
    
    return {
        "product_id": product_id,
        "requested_quantity": quantity,
        "available_quantity": product.stock_quantity,
        "available": available,
        "in_stock": product.stock_quantity > 0
    }
