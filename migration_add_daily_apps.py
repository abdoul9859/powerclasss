#!/usr/bin/env python3
"""
Script de migration pour ajouter les nouvelles applications :
- Demandes quotidiennes des clients
- Ventes quotidiennes

Ce script ajoute les nouvelles tables à la base de données existante.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, DATABASE_URL

def run_migration():
    """Exécute la migration pour ajouter les nouvelles tables"""
    print("🚀 Début de la migration pour les applications quotidiennes...")
    
    try:
        # Créer les nouvelles tables
        print("📋 Création des tables...")
        
        # Tables pour les demandes quotidiennes des clients
        daily_requests_table = """
        CREATE TABLE IF NOT EXISTS daily_client_requests (
            request_id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(client_id) ON DELETE SET NULL,
            client_name VARCHAR(100) NOT NULL,
            client_phone VARCHAR(20),
            product_description TEXT NOT NULL,
            request_date DATE NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_daily_client_requests_client_id ON daily_client_requests(client_id);
        CREATE INDEX IF NOT EXISTS idx_daily_client_requests_request_date ON daily_client_requests(request_date);
        CREATE INDEX IF NOT EXISTS idx_daily_client_requests_status ON daily_client_requests(status);
        """
        
        # Tables pour les ventes quotidiennes
        daily_sales_table = """
        CREATE TABLE IF NOT EXISTS daily_sales (
            sale_id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(client_id) ON DELETE SET NULL,
            client_name VARCHAR(100) NOT NULL,
            product_id INTEGER REFERENCES products(product_id) ON DELETE SET NULL,
            product_name VARCHAR(500) NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price NUMERIC(10,2) NOT NULL,
            total_amount NUMERIC(12,2) NOT NULL,
            sale_date DATE NOT NULL,
            payment_method VARCHAR(50) DEFAULT 'espece',
            invoice_id INTEGER REFERENCES invoices(invoice_id) ON DELETE SET NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_daily_sales_client_id ON daily_sales(client_id);
        CREATE INDEX IF NOT EXISTS idx_daily_sales_product_id ON daily_sales(product_id);
        CREATE INDEX IF NOT EXISTS idx_daily_sales_sale_date ON daily_sales(sale_date);
        CREATE INDEX IF NOT EXISTS idx_daily_sales_invoice_id ON daily_sales(invoice_id);
        CREATE INDEX IF NOT EXISTS ix_daily_sales_date_client ON daily_sales(sale_date, client_id);
        """
        
        # Exécuter les requêtes
        with engine.connect() as conn:
            # Activer l'autocommit pour les DDL
            conn.execute(text("BEGIN;"))
            
            try:
                # Créer la table des demandes quotidiennes
                print("  📝 Création de la table daily_client_requests...")
                conn.execute(text(daily_requests_table))
                
                # Créer la table des ventes quotidiennes
                print("  📝 Création de la table daily_sales...")
                conn.execute(text(daily_sales_table))
                
                # Valider les changements
                conn.execute(text("COMMIT;"))
                print("✅ Migration terminée avec succès!")
                
            except Exception as e:
                # Annuler en cas d'erreur
                conn.execute(text("ROLLBACK;"))
                print(f"❌ Erreur lors de la migration: {e}")
                raise
        
        print("\n🎉 Les nouvelles applications sont maintenant disponibles :")
        print("   • Demandes quotidiennes des clients : /daily-requests")
        print("   • Ventes quotidiennes : /daily-sales")
        print("\n💡 N'oubliez pas de redémarrer l'application pour que les changements prennent effet.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    load_dotenv()
    run_migration()
