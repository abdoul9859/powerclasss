"""
Modèle Client de la boutique en ligne
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class StoreCustomer(Base):
    """Client de la boutique en ligne (différent des clients B2B de l'app de gestion)"""
    __tablename__ = "store_customers"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    
    # Adresse de livraison par défaut
    address = Column(Text)
    city = Column(String(50))
    postal_code = Column(String(10))
    country = Column(String(50), default="Côte d'Ivoire")
    
    # Préférences
    newsletter_subscribed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Notes internes (pour l'admin)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<StoreCustomer {self.email}>"
