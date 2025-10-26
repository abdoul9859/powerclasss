"""
API de gestion des commandes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime
import uuid

from app.database import get_db, Product
from boutique.backend.models.customer import StoreCustomer
from boutique.backend.models.order import StoreOrder, StoreOrderItem, OrderStatus, PaymentStatus
from boutique.backend.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderItemResponse,
    OrderListResponse,
    OrderStatusUpdate
)
from boutique.backend.utils.auth import get_current_customer

router = APIRouter(prefix="/api/store/orders", tags=["store-orders"])


def generate_order_number() -> str:
    """Générer un numéro de commande unique"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"CMD-{timestamp}-{random_part}"


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle commande
    """
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La commande doit contenir au moins un article"
        )
    
    # Vérifier la disponibilité des produits et calculer les montants
    order_items_data = []
    subtotal = Decimal("0")
    
    for item in order_data.items:
        product = db.query(Product).filter(
            Product.product_id == item.product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Produit {item.product_id} non trouvé"
            )
        
        # Vérifier le stock
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuffisant pour {product.name}. Disponible: {product.stock_quantity}"
            )
        
        # Calculer le sous-total de l'article
        item_subtotal = product.price * item.quantity
        subtotal += item_subtotal
        
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price,
            "subtotal": item_subtotal,
            "variant_id": item.variant_id
        })
    
    # Calculer les frais de livraison
    shipping_cost = Decimal("0")
    if subtotal < 50000:  # Livraison gratuite au-dessus de 50000 FCFA
        shipping_cost = Decimal("2000")
    
    # Calculer les taxes (si applicable)
    tax_amount = Decimal("0")
    
    # Appliquer les réductions (code promo)
    discount_amount = Decimal("0")
    # TODO: Implémenter la logique des codes promo
    
    # Total final
    total_amount = subtotal + shipping_cost + tax_amount - discount_amount
    
    # Créer la commande
    new_order = StoreOrder(
        order_number=generate_order_number(),
        customer_id=current_customer.customer_id,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        
        # Adresse de livraison
        shipping_first_name=order_data.shipping_address.first_name,
        shipping_last_name=order_data.shipping_address.last_name,
        shipping_email=order_data.shipping_address.email,
        shipping_phone=order_data.shipping_address.phone,
        shipping_address=order_data.shipping_address.address,
        shipping_city=order_data.shipping_address.city,
        shipping_postal_code=order_data.shipping_address.postal_code,
        shipping_country=order_data.shipping_address.country,
        
        # Adresse de facturation (si différente)
        billing_first_name=order_data.billing_address.first_name if order_data.billing_address else None,
        billing_last_name=order_data.billing_address.last_name if order_data.billing_address else None,
        billing_address=order_data.billing_address.address if order_data.billing_address else None,
        billing_city=order_data.billing_address.city if order_data.billing_address else None,
        billing_postal_code=order_data.billing_address.postal_code if order_data.billing_address else None,
        billing_country=order_data.billing_address.country if order_data.billing_address else None,
        
        # Montants
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        
        # Notes
        customer_notes=order_data.customer_notes,
        coupon_code=order_data.coupon_code
    )
    
    db.add(new_order)
    db.flush()  # Pour obtenir l'order_id
    
    # Créer les items de commande
    for item_data in order_items_data:
        product = item_data["product"]
        
        order_item = StoreOrderItem(
            order_id=new_order.order_id,
            product_id=product.product_id,
            product_name=product.name,
            product_sku=product.sku,
            product_image=product.image,
            unit_price=item_data["unit_price"],
            quantity=item_data["quantity"],
            subtotal=item_data["subtotal"],
            variant_info=None  # TODO: Sérialiser les infos de variante
        )
        
        db.add(order_item)
        
        # Réserver le stock (décrémenter)
        product.stock_quantity -= item_data["quantity"]
    
    db.commit()
    db.refresh(new_order)
    
    # Charger les items pour la réponse
    items_response = []
    for item in new_order.items:
        items_response.append(OrderItemResponse.from_orm(item))
    
    return OrderResponse(
        order_id=new_order.order_id,
        order_number=new_order.order_number,
        status=new_order.status.value,
        payment_status=new_order.payment_status.value,
        shipping_first_name=new_order.shipping_first_name,
        shipping_last_name=new_order.shipping_last_name,
        shipping_email=new_order.shipping_email,
        shipping_phone=new_order.shipping_phone,
        shipping_address=new_order.shipping_address,
        shipping_city=new_order.shipping_city,
        shipping_postal_code=new_order.shipping_postal_code,
        shipping_country=new_order.shipping_country,
        subtotal=new_order.subtotal,
        shipping_cost=new_order.shipping_cost,
        tax_amount=new_order.tax_amount,
        discount_amount=new_order.discount_amount,
        total_amount=new_order.total_amount,
        items=items_response,
        created_at=new_order.created_at,
        confirmed_at=new_order.confirmed_at,
        shipped_at=new_order.shipped_at,
        delivered_at=new_order.delivered_at,
        tracking_number=new_order.tracking_number,
        carrier=new_order.carrier,
        customer_notes=new_order.customer_notes
    )


@router.get("/", response_model=List[OrderListResponse])
async def get_customer_orders(
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Liste des commandes du client connecté
    """
    orders = db.query(StoreOrder).filter(
        StoreOrder.customer_id == current_customer.customer_id
    ).order_by(StoreOrder.created_at.desc()).all()
    
    orders_response = []
    for order in orders:
        orders_response.append(OrderListResponse(
            order_id=order.order_id,
            order_number=order.order_number,
            status=order.status.value,
            payment_status=order.payment_status.value,
            total_amount=order.total_amount,
            items_count=len(order.items),
            created_at=order.created_at
        ))
    
    return orders_response


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Détail d'une commande
    """
    order = db.query(StoreOrder).filter(
        StoreOrder.order_id == order_id,
        StoreOrder.customer_id == current_customer.customer_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Charger les items
    items_response = []
    for item in order.items:
        items_response.append(OrderItemResponse.from_orm(item))
    
    return OrderResponse(
        order_id=order.order_id,
        order_number=order.order_number,
        status=order.status.value,
        payment_status=order.payment_status.value,
        shipping_first_name=order.shipping_first_name,
        shipping_last_name=order.shipping_last_name,
        shipping_email=order.shipping_email,
        shipping_phone=order.shipping_phone,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_postal_code=order.shipping_postal_code,
        shipping_country=order.shipping_country,
        subtotal=order.subtotal,
        shipping_cost=order.shipping_cost,
        tax_amount=order.tax_amount,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount,
        items=items_response,
        created_at=order.created_at,
        confirmed_at=order.confirmed_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at,
        tracking_number=order.tracking_number,
        carrier=order.carrier,
        customer_notes=order.customer_notes
    )


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Annuler une commande (seulement si en attente)
    """
    order = db.query(StoreOrder).filter(
        StoreOrder.order_id == order_id,
        StoreOrder.customer_id == current_customer.customer_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Vérifier que la commande peut être annulée
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette commande ne peut plus être annulée"
        )
    
    # Annuler la commande
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.now()
    
    # Restaurer le stock
    for item in order.items:
        product = db.query(Product).filter(
            Product.product_id == item.product_id
        ).first()
        if product:
            product.stock_quantity += item.quantity
    
    db.commit()
    
    return {"message": "Commande annulée avec succès"}
