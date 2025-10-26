"""
Modèle Paiement de la boutique en ligne
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    """Méthodes de paiement"""
    ORANGE_MONEY = "orange_money"
    MTN_MONEY = "mtn_money"
    MOOV_MONEY = "moov_money"
    WAVE = "wave"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"


class StorePayment(Base):
    """Paiement d'une commande"""
    __tablename__ = "store_payments"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    payment_reference = Column(String(100), unique=True, nullable=False, index=True)
    
    # Commande associée
    order_id = Column(Integer, ForeignKey("store_orders.order_id"), nullable=False, index=True)
    order = relationship("StoreOrder", backref="payments")
    
    # Méthode de paiement
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    
    # Montant
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="XOF")                  # Franc CFA
    
    # Statut
    status = Column(String(20), default="pending")               # pending, completed, failed, refunded
    
    # Informations du fournisseur de paiement
    provider_transaction_id = Column(String(200))                # ID transaction du provider (Orange, MTN, etc.)
    provider_response = Column(Text)                             # Réponse complète du provider (JSON)
    
    # Informations du payeur
    payer_phone = Column(String(20))                             # Numéro Mobile Money
    payer_email = Column(String(100))
    payer_name = Column(String(100))
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), index=True)
    completed_at = Column(DateTime)
    failed_at = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    error_message = Column(Text)                                 # Message d'erreur si échec
    
    def __repr__(self):
        return f"<StorePayment {self.payment_reference} - {self.status}>"
