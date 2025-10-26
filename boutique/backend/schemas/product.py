"""
Schémas Pydantic pour les produits de la boutique
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class ProductImageResponse(BaseModel):
    """Image d'un produit"""
    url: str
    alt: Optional[str] = None


class ProductFilterParams(BaseModel):
    """Paramètres de filtrage des produits"""
    category: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock: Optional[bool] = True
    search: Optional[str] = None
    sort_by: Optional[str] = Field(None, pattern="^(price_asc|price_desc|name_asc|name_desc|newest)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class ProductListResponse(BaseModel):
    """Produit dans la liste (vue catalogue)"""
    product_id: int
    name: str
    description: Optional[str]
    price: Decimal
    wholesale_price: Optional[Decimal]
    image: Optional[str]
    category: Optional[str]
    stock_quantity: int
    in_stock: bool
    sku: Optional[str]
    
    class Config:
        from_attributes = True


class ProductVariantResponse(BaseModel):
    """Variante d'un produit"""
    variant_id: int
    sku: str
    price: Decimal
    stock_quantity: int
    attributes: dict  # Ex: {"Couleur": "Rouge", "Taille": "M"}
    
    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    """Détail complet d'un produit"""
    product_id: int
    name: str
    description: Optional[str]
    price: Decimal
    wholesale_price: Optional[Decimal]
    purchase_price: Optional[Decimal] = None  # Caché pour les clients
    image: Optional[str]
    images: List[str] = []  # Liste d'images supplémentaires
    category: Optional[str]
    stock_quantity: int
    in_stock: bool
    sku: Optional[str]
    barcode: Optional[str]
    weight: Optional[Decimal]
    dimensions: Optional[str]
    variants: List[ProductVariantResponse] = []
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProductSearchResponse(BaseModel):
    """Résultat de recherche de produits"""
    products: List[ProductListResponse]
    total: int
    page: int
    limit: int
    total_pages: int
