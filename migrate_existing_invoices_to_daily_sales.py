#!/usr/bin/env python3
"""
Script pour migrer les factures existantes vers les ventes quotidiennes.
Ce script crée des entrées dans daily_sales pour toutes les factures existantes.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, DATABASE_URL, Invoice, InvoiceItem, DailySale, Client, Product

def migrate_invoices_to_daily_sales():
    """Migre toutes les factures existantes vers les ventes quotidiennes"""
    print("🚀 Début de la migration des factures vers les ventes quotidiennes...")
    
    try:
        # Créer une session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Récupérer toutes les factures avec leurs éléments
        invoices = db.query(Invoice).all()
        
        print(f"📋 {len(invoices)} factures trouvées")
        
        migrated_count = 0
        error_count = 0
        
        for invoice in invoices:
            try:
                # Récupérer le client
                client = db.query(Client).filter(Client.client_id == invoice.client_id).first()
                if not client:
                    print(f"⚠️  Client non trouvé pour la facture {invoice.invoice_number}")
                    continue
                
                # Récupérer les éléments de la facture
                items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.invoice_id).all()
                
                for item in items:
                    # Vérifier si une vente quotidienne existe déjà pour cet élément
                    existing_sale = db.query(DailySale).filter(
                        DailySale.invoice_id == invoice.invoice_id,
                        DailySale.product_id == item.product_id,
                        DailySale.quantity == item.quantity
                    ).first()
                    
                    if existing_sale:
                        print(f"⏭️  Vente quotidienne déjà existante pour {invoice.invoice_number} - {item.product_name}")
                        continue
                    
                    # Récupérer le produit si product_id existe
                    product = None
                    if item.product_id:
                        product = db.query(Product).filter(Product.product_id == item.product_id).first()
                    
                    # Créer la vente quotidienne
                    daily_sale = DailySale(
                        client_id=invoice.client_id,
                        client_name=client.name,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.price,
                        total_amount=item.total,
                        sale_date=invoice.date.date() if invoice.date else datetime.now().date(),
                        payment_method=invoice.payment_method or "espece",
                        invoice_id=invoice.invoice_id,
                        notes=f"Migration automatique depuis facture {invoice.invoice_number}"
                    )
                    
                    db.add(daily_sale)
                    migrated_count += 1
                
                # Valider les changements pour cette facture
                db.commit()
                print(f"✅ Facture {invoice.invoice_number} migrée avec succès")
                
            except Exception as e:
                print(f"❌ Erreur lors de la migration de la facture {invoice.invoice_number}: {e}")
                db.rollback()
                error_count += 1
                continue
        
        print(f"\n🎉 Migration terminée !")
        print(f"   • {migrated_count} ventes quotidiennes créées")
        print(f"   • {error_count} erreurs")
        
        # Vérifier le résultat
        total_daily_sales = db.query(DailySale).count()
        print(f"   • Total des ventes quotidiennes dans la base : {total_daily_sales}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    load_dotenv()
    migrate_invoices_to_daily_sales()
