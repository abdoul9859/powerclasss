"""
Service d'intégration Google Sheets pour l'importation de produits
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
import os
import json
import re
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import Product, ProductVariant, ProductVariantAttribute, Category, StockMovement
from app.schemas import ProductCreate


class GoogleSheetsService:
    """Service pour synchroniser les produits depuis Google Sheets"""

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',  # Accès en lecture ET écriture
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    # Mapping des colonnes Google Sheets vers les champs Product
    # Support des noms avec et sans accents
    COLUMN_MAPPING = {
        'Nom du produit': 'name',
        'Categorie': 'category',
        'Catégorie': 'category',  # Version avec accent
        'Etat': 'condition',
        'État': 'condition',  # Version avec accent
        'Marque': 'brand',
        'Modele': 'model',
        'Modèle': 'model',  # Version avec accent
        "Prix d'achat (FCFA)": 'purchase_price',
        'Prix en gros (FCFA)': 'wholesale_price',
        'Prix unitaire (FCFA)': 'price',
        'Code-barres produit': 'barcode',
        'Quantite en stock': 'quantity',
        'Quantité en stock': 'quantity',  # Version avec accent
        'Description': 'description',
        'Notes': 'notes',
        'Lieu ou Image du produit': 'image_path'
    }

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialise le service Google Sheets

        Args:
            credentials_path: Chemin vers le fichier JSON des credentials Google
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        self.client = None

    def authenticate(self) -> bool:
        """
        Authentifie le service avec Google Sheets API

        Returns:
            True si l'authentification réussit, False sinon
        """
        try:
            if not self.credentials_path or not os.path.exists(self.credentials_path):
                raise ValueError(f"Fichier credentials non trouvé: {self.credentials_path}")

            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            self.client = gspread.authorize(creds)
            return True
        except Exception as e:
            print(f"Erreur d'authentification Google Sheets: {str(e)}")
            return False

    def get_sheet_data(self, spreadsheet_id: str, worksheet_name: str = 'Tableau1') -> List[Dict]:
        """
        Récupère les données d'une feuille Google Sheets

        Args:
            spreadsheet_id: ID du Google Spreadsheet
            worksheet_name: Nom de la feuille (par défaut 'Tableau1')

        Returns:
            Liste de dictionnaires représentant les lignes
        """
        if not self.client:
            if not self.authenticate():
                raise Exception("Impossible de s'authentifier avec Google Sheets")

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)

            # Récupère toutes les données avec les en-têtes
            data = worksheet.get_all_records()
            return data
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des données: {str(e)}")

    def _normalize_value(self, value: any, field_type: str) -> any:
        """
        Normalise une valeur selon le type de champ

        Args:
            value: Valeur à normaliser
            field_type: Type de champ (price, integer, text, etc.)

        Returns:
            Valeur normalisée
        """
        if value is None or value == '':
            return None

        try:
            if field_type == 'price':
                # Convertit en string et nettoie
                value_str = str(value).strip()

                # Si vide après strip, retourne 0
                if not value_str:
                    return Decimal('0.00')

                # Supprime d'abord les suffixes de devise
                value_str = value_str.replace('F CFA', '').replace('FCFA', '').replace('CFA', '')
                # Supprime les espaces et remplace virgules par points
                value_str = value_str.replace(' ', '').replace(',', '.')
                # Nettoie les caractères non numériques sauf le point et le tiret (pour les négatifs)
                value_str = re.sub(r'[^\d.-]', '', value_str)

                # Si vide après nettoyage, retourne 0
                if not value_str or value_str == '-':
                    return Decimal('0.00')

                try:
                    return Decimal(value_str)
                except Exception:
                    print(f"⚠️ Impossible de convertir '{value}' en prix, utilisation de 0.00")
                    return Decimal('0.00')

            elif field_type == 'integer':
                value_str = str(value).replace(' ', '').replace(',', '.')
                # Nettoie les caractères non numériques
                value_str = re.sub(r'[^\d.-]', '', value_str)
                if not value_str or value_str == '-':
                    return 0
                return int(float(value_str)) if value_str else 0

            elif field_type == 'text':
                result = str(value).strip() if value else ''
                return result if result else None
            else:
                return value
        except (ValueError, TypeError) as e:
            print(f"⚠️ Erreur de normalisation pour '{value}' ({field_type}): {str(e)}")
            if field_type == 'price':
                return Decimal('0.00')
            elif field_type == 'integer':
                return 0
            return None

    def map_sheet_row_to_product(self, row: Dict) -> Dict:
        """
        Mappe une ligne Google Sheets vers un dict de produit

        Args:
            row: Dictionnaire représentant une ligne du Google Sheet

        Returns:
            Dictionnaire avec les champs mappés pour Product
        """
        product_data = {}

        for sheet_col, db_field in self.COLUMN_MAPPING.items():
            value = row.get(sheet_col)

            # Normalisation selon le type de champ
            if db_field in ['price', 'wholesale_price', 'purchase_price']:
                product_data[db_field] = self._normalize_value(value, 'price')
            elif db_field == 'quantity':
                product_data[db_field] = self._normalize_value(value, 'integer')
            else:
                product_data[db_field] = self._normalize_value(value, 'text')

        # Valeurs par défaut
        if 'quantity' not in product_data or product_data['quantity'] is None:
            product_data['quantity'] = 0
        if 'price' not in product_data or product_data['price'] is None:
            product_data['price'] = Decimal('0.00')
        if 'purchase_price' not in product_data or product_data['purchase_price'] is None:
            product_data['purchase_price'] = Decimal('0.00')
        if 'condition' not in product_data or not product_data['condition']:
            product_data['condition'] = 'neuf'

        # Ajout de la date d'entrée
        product_data['entry_date'] = datetime.now()

        return product_data

    def sync_products(self, db: Session, spreadsheet_id: str, worksheet_name: str = 'Tableau1',
                     update_existing: bool = False) -> Dict[str, int]:
        """
        Synchronise les produits depuis Google Sheets vers la base de données

        Args:
            db: Session SQLAlchemy
            spreadsheet_id: ID du Google Spreadsheet
            worksheet_name: Nom de la feuille
            update_existing: Si True, met à jour les produits existants (par code-barres)

        Returns:
            Statistiques de synchronisation (created, updated, errors)
        """
        stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }

        try:
            # Récupère les données du Google Sheet
            rows = self.get_sheet_data(spreadsheet_id, worksheet_name)
            stats['total'] = len(rows)

            for idx, row in enumerate(rows, start=1):
                try:
                    # Mappe la ligne vers un dict de produit
                    product_data = self.map_sheet_row_to_product(row)

                    # Ignore les lignes sans nom de produit
                    if not product_data.get('name'):
                        print(f"⚠️ Ligne {idx}: Ignorée (pas de nom de produit)")
                        stats['skipped'] += 1
                        continue

                    # Vérifie si le produit existe déjà (par code-barres ou nom)
                    existing_product = None
                    if product_data.get('barcode'):
                        existing_product = db.query(Product).filter(
                            Product.barcode == product_data['barcode']
                        ).first()

                    if existing_product:
                        if update_existing:
                            # Met à jour le produit existant
                            for key, value in product_data.items():
                                if value is not None and key != 'barcode':
                                    setattr(existing_product, key, value)
                            db.commit()
                            stats['updated'] += 1
                        else:
                            stats['skipped'] += 1
                    else:
                        # Crée un nouveau produit
                        new_product = Product(**product_data)
                        db.add(new_product)
                        db.commit()
                        db.refresh(new_product)

                        # Crée un mouvement de stock IN si quantité > 0
                        if new_product.quantity > 0:
                            stock_movement = StockMovement(
                                product_id=new_product.product_id,
                                quantity=new_product.quantity,
                                movement_type='IN',
                                reference_type='GOOGLE_SHEETS_IMPORT',
                                notes=f'Import initial depuis Google Sheets',
                                unit_price=new_product.purchase_price or Decimal('0.00')
                            )
                            db.add(stock_movement)
                            db.commit()

                        stats['created'] += 1

                except Exception as e:
                    stats['errors'] += 1
                    error_msg = f"Ligne {idx}: {str(e)}"
                    stats['error_details'].append(error_msg)
                    print(error_msg)
                    db.rollback()
                    continue

            return stats

        except Exception as e:
            error_msg = f"Erreur globale de synchronisation: {str(e)}"
            stats['errors'] += 1
            stats['error_details'].append(error_msg)
            print(error_msg)
            return stats

    def test_connection(self, spreadsheet_id: str) -> Dict[str, any]:
        """
        Test la connexion au Google Sheet

        Args:
            spreadsheet_id: ID du Google Spreadsheet

        Returns:
            Dict avec le statut de connexion et les infos
        """
        try:
            if not self.client:
                if not self.authenticate():
                    return {
                        'success': False,
                        'error': 'Impossible de s\'authentifier avec Google Sheets'
                    }

            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheets = [ws.title for ws in spreadsheet.worksheets()]

            return {
                'success': True,
                'spreadsheet_title': spreadsheet.title,
                'worksheets': worksheets
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update_product_stock_in_sheet(self, spreadsheet_id: str, worksheet_name: str,
                                     product_barcode: str, new_quantity: int) -> bool:
        """
        Met à jour le stock d'un produit dans Google Sheets par son code-barres

        Args:
            spreadsheet_id: ID du Google Spreadsheet
            worksheet_name: Nom de la feuille
            product_barcode: Code-barres du produit
            new_quantity: Nouvelle quantité en stock

        Returns:
            True si la mise à jour réussit, False sinon
        """
        try:
            if not self.client:
                if not self.authenticate():
                    print("❌ Impossible de s'authentifier avec Google Sheets")
                    return False

            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)

            # Récupère toutes les données
            all_data = worksheet.get_all_values()

            if not all_data:
                print("❌ Aucune donnée trouvée dans le Google Sheet")
                return False

            # Trouve l'index des colonnes
            headers = all_data[0]
            barcode_col_idx = None
            quantity_col_idx = None

            # Chercher les colonnes de code-barres et quantité
            for idx, header in enumerate(headers):
                if header == 'Code-barres produit':
                    barcode_col_idx = idx
                elif header in ['Quantite en stock', 'Quantité en stock']:
                    quantity_col_idx = idx

            if barcode_col_idx is None or quantity_col_idx is None:
                print(f"❌ Colonnes requises non trouvées (barcode:{barcode_col_idx}, qty:{quantity_col_idx})")
                return False

            # Chercher la ligne du produit
            for row_idx, row in enumerate(all_data[1:], start=2):  # start=2 car ligne 1 = headers
                if len(row) > barcode_col_idx:
                    row_barcode = str(row[barcode_col_idx]).strip()
                    if row_barcode == str(product_barcode).strip():
                        # Mise à jour de la cellule (colonne + ligne)
                        # Convertir l'index en lettre de colonne (A, B, C, etc.)
                        col_letter = self._column_index_to_letter(quantity_col_idx + 1)
                        cell_address = f"{col_letter}{row_idx}"

                        worksheet.update(cell_address, [[new_quantity]])
                        print(f"✅ Stock mis à jour dans Google Sheets: {product_barcode} → {new_quantity}")
                        return True

            print(f"⚠️ Produit non trouvé dans Google Sheets: {product_barcode}")
            return False

        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du stock dans Google Sheets: {str(e)}")
            return False

    def _column_index_to_letter(self, col_idx: int) -> str:
        """
        Convertit un index de colonne (1-indexed) en lettre Excel (A, B, C, ..., Z, AA, AB, ...)

        Args:
            col_idx: Index de colonne (1 = A, 2 = B, etc.)

        Returns:
            Lettre de colonne
        """
        result = ""
        while col_idx > 0:
            col_idx -= 1
            result = chr(65 + (col_idx % 26)) + result
            col_idx //= 26
        return result

    def sync_stock_to_sheets(self, db: Session, spreadsheet_id: str,
                            worksheet_name: str) -> Dict[str, int]:
        """
        Synchronise tous les stocks de la base de données vers Google Sheets

        Args:
            db: Session SQLAlchemy
            spreadsheet_id: ID du Google Spreadsheet
            worksheet_name: Nom de la feuille

        Returns:
            Statistiques de synchronisation (updated, errors)
        """
        stats = {
            'total': 0,
            'updated': 0,
            'not_found': 0,
            'errors': 0,
            'error_details': []
        }

        try:
            # Récupère tous les produits avec un code-barres
            products = db.query(Product).filter(Product.barcode.isnot(None)).all()
            stats['total'] = len(products)

            for product in products:
                try:
                    success = self.update_product_stock_in_sheet(
                        spreadsheet_id=spreadsheet_id,
                        worksheet_name=worksheet_name,
                        product_barcode=product.barcode,
                        new_quantity=product.quantity or 0
                    )

                    if success:
                        stats['updated'] += 1
                    else:
                        stats['not_found'] += 1

                except Exception as e:
                    stats['errors'] += 1
                    error_msg = f"Produit {product.name} ({product.barcode}): {str(e)}"
                    stats['error_details'].append(error_msg)
                    print(f"❌ {error_msg}")
                    continue

            return stats

        except Exception as e:
            stats['errors'] += 1
            stats['error_details'].append(f"Erreur globale: {str(e)}")
            return stats
