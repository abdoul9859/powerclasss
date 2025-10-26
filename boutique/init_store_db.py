"""
Script pour initialiser les tables de la boutique en ligne
"""
from app.database import Base, engine
from boutique.backend.models import (
    StoreCustomer,
    StoreOrder,
    StoreOrderItem,
    StorePayment
)


def init_store_database():
    """Créer toutes les tables de la boutique"""
    print("🛍️ Création des tables de la boutique en ligne...")
    
    try:
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables de la boutique créées avec succès!")
        print("   - store_customers")
        print("   - store_orders")
        print("   - store_order_items")
        print("   - store_payments")
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        raise


if __name__ == "__main__":
    init_store_database()
