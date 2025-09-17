#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier l'état des ventes quotidiennes.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, DATABASE_URL, Invoice, InvoiceItem, DailySale, Client, Product

def check_daily_sales_status():
    """Vérifie l'état des ventes quotidiennes"""
    print("🔍 Diagnostic des ventes quotidiennes...")
    
    try:
        # Créer une session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Vérifier si les tables existent
        print("\n📋 Vérification des tables...")
        
        # Vérifier la table daily_sales
        try:
            daily_sales_count = db.query(DailySale).count()
            print(f"   ✅ Table daily_sales : {daily_sales_count} entrées")
        except Exception as e:
            print(f"   ❌ Table daily_sales : {e}")
            return
        
        # Vérifier la table daily_client_requests
        try:
            from app.database import DailyClientRequest
            requests_count = db.query(DailyClientRequest).count()
            print(f"   ✅ Table daily_client_requests : {requests_count} entrées")
        except Exception as e:
            print(f"   ❌ Table daily_client_requests : {e}")
        
        # Statistiques des factures
        print("\n📊 Statistiques des factures...")
        total_invoices = db.query(Invoice).count()
        print(f"   • Total factures : {total_invoices}")
        
        # Factures d'aujourd'hui
        today = date.today()
        today_invoices = db.query(Invoice).filter(Invoice.date >= today).count()
        print(f"   • Factures d'aujourd'hui : {today_invoices}")
        
        # Factures de cette semaine
        from datetime import timedelta
        week_ago = today - timedelta(days=7)
        week_invoices = db.query(Invoice).filter(Invoice.date >= week_ago).count()
        print(f"   • Factures de cette semaine : {week_invoices}")
        
        # Statistiques des ventes quotidiennes
        print("\n🛍️ Statistiques des ventes quotidiennes...")
        total_daily_sales = db.query(DailySale).count()
        print(f"   • Total ventes quotidiennes : {total_daily_sales}")
        
        # Ventes d'aujourd'hui
        today_sales = db.query(DailySale).filter(DailySale.sale_date == today).count()
        print(f"   • Ventes d'aujourd'hui : {today_sales}")
        
        # Ventes de cette semaine
        week_sales = db.query(DailySale).filter(DailySale.sale_date >= week_ago).count()
        print(f"   • Ventes de cette semaine : {week_sales}")
        
        # Ventes liées à des factures
        invoice_sales = db.query(DailySale).filter(DailySale.invoice_id.isnot(None)).count()
        print(f"   • Ventes liées à des factures : {invoice_sales}")
        
        # Ventes directes (sans facture)
        direct_sales = db.query(DailySale).filter(DailySale.invoice_id.is_(None)).count()
        print(f"   • Ventes directes : {direct_sales}")
        
        # Vérifier les factures récentes sans ventes quotidiennes
        print("\n🔍 Vérification des factures récentes...")
        recent_invoices = db.query(Invoice).filter(Invoice.date >= week_ago).all()
        
        invoices_without_sales = 0
        for invoice in recent_invoices:
            has_daily_sales = db.query(DailySale).filter(DailySale.invoice_id == invoice.invoice_id).first()
            if not has_daily_sales:
                invoices_without_sales += 1
                print(f"   ⚠️  Facture {invoice.invoice_number} ({invoice.date}) sans ventes quotidiennes")
        
        if invoices_without_sales == 0:
            print("   ✅ Toutes les factures récentes ont des ventes quotidiennes associées")
        else:
            print(f"   ⚠️  {invoices_without_sales} factures récentes sans ventes quotidiennes")
        
        # Montant total des ventes
        print("\n💰 Montant total des ventes...")
        from sqlalchemy import func
        total_amount = db.query(func.sum(DailySale.total_amount)).scalar() or 0
        print(f"   • Montant total : {total_amount:,.0f} F CFA")
        
        # Montant des ventes d'aujourd'hui
        today_amount = db.query(func.sum(DailySale.total_amount)).filter(DailySale.sale_date == today).scalar() or 0
        print(f"   • Montant d'aujourd'hui : {today_amount:,.0f} F CFA")
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    load_dotenv()
    check_daily_sales_status()
