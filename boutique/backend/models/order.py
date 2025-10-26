"""
Modèles Commande de la boutique en ligne
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Statuts de commande"""
    PENDING = "pending"              # En attente de paiement
    CONFIRMED = "confirmed"          # Confirmée et payée
    PROCESSING = "processing"        # En préparation
    SHIPPED = "shipped"              # Expédiée
    DELIVERED = "delivered"          # Livrée
    CANCELLED = "cancelled"          # Annulée
    REFUNDED = "refunded"            # Remboursée


class PaymentStatus(str, enum.Enum):
    """Statuts de paiement"""
    PENDING = "pending"              # En attente
    PROCESSING = "processing"        # En cours de traitement
    COMPLETED = "completed"          # Complété
    FAILED = "failed"                # Échoué
    REFUNDED = "refunded"            # Remboursé


class StoreOrder(Base):
    """Commande de la boutique en ligne"""
    __tablename__ = "store_orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Client
    customer_id = Column(Integer, ForeignKey("store_customers.customer_id"), nullable=False, index=True)
    customer = relationship("StoreCustomer", backref="orders")
    
    # Statuts
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Informations de livraison
    shipping_first_name = Column(String(50), nullable=False)
    shipping_last_name = Column(String(50), nullable=False)
    shipping_email = Column(String(100), nullable=False)
    shipping_phone = Column(String(20), nullable=False)
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(50), nullable=False)
    shipping_postal_code = Column(String(10))
    shipping_country = Column(String(50), default="Côte d'Ivoire")
    
    # Informations de facturation (optionnel, peut être identique à la livraison)
    billing_first_name = Column(String(50))
    billing_last_name = Column(String(50))
    billing_address = Column(Text)
    billing_city = Column(String(50))
    billing_postal_code = Column(String(10))
    billing_country = Column(String(50))
    
    # Montants
    subtotal = Column(Numeric(10, 2), nullable=False)           # Sous-total produits
    shipping_cost = Column(Numeric(10, 2), default=0)           # Frais de livraison
    tax_amount = Column(Numeric(10, 2), default=0)              # Taxes
    discount_amount = Column(Numeric(10, 2), default=0)         # Réduction
    total_amount = Column(Numeric(10, 2), nullable=False)       # Total final
    
    # Code promo
    coupon_code = Column(String(50))
    
    # Notes
    customer_notes = Column(Text)                                # Notes du client
    admin_notes = Column(Text)                                   # Notes internes admin
    
    # Suivi de livraison
    tracking_number = Column(String(100))
    carrier = Column(String(50))                                 # Transporteur
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed_at = Column(DateTime)                              # Date de confirmation
    shipped_at = Column(DateTime)                                # Date d'expédition
    delivered_at = Column(DateTime)                              # Date de livraison
    
    # Relation avec les items
    items = relationship("StoreOrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<StoreOrder {self.order_number}>"


class StoreOrderItem(Base):
    """Article d'une commande"""
    __tablename__ = "store_order_items"
    
    order_item_id = Column(Integer, primary_key=True, index=True)
    
    # Commande parente
    order_id = Column(Integer, ForeignKey("store_orders.order_id"), nullable=False, index=True)
    order = relationship("StoreOrder", back_populates="items")
    
    # Produit (référence au produit de l'inventaire)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
    product = relationship("Product")
    
    # Détails du produit au moment de la commande (snapshot)
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100))
    product_image = Column(String(500))
    
    # Prix et quantité
    unit_price = Column(Numeric(10, 2), nullable=False)         # Prix unitaire au moment de l'achat
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)           # unit_price * quantity
    
    # Variante (si applicable)
    variant_info = Column(Text)                                  # JSON avec les attributs de variante
    
    def __repr__(self):
        return f"<StoreOrderItem {self.product_name} x{self.quantity}>"
