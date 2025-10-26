"""
API publique des produits pour la boutique
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from decimal import Decimal
import math

from app.database import get_db, Product, Category
from boutique.backend.schemas.product import (
    ProductListResponse,
    ProductDetailResponse,
    ProductSearchResponse
)

router = APIRouter(prefix="/api/store/products", tags=["store-products"])


@router.get("/", response_model=ProductSearchResponse)
async def get_products(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    search: Optional[str] = Query(None, description="Rechercher dans nom et description"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Prix minimum"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Prix maximum"),
    in_stock: bool = Query(True, description="Seulement les produits en stock"),
    sort_by: Optional[str] = Query("newest", pattern="^(price_asc|price_desc|name_asc|name_desc|newest)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Liste des produits disponibles dans la boutique
    
    - **category**: Filtrer par catégorie
    - **search**: Recherche textuelle
    - **min_price** / **max_price**: Fourchette de prix
    - **in_stock**: Afficher uniquement les produits en stock
    - **sort_by**: Tri (price_asc, price_desc, name_asc, name_desc, newest)
    - **page**: Numéro de page
    - **limit**: Nombre de résultats par page
    """
    query = db.query(Product).filter(Product.is_active == True)
    
    # Filtrer par catégorie
    if category:
        query = query.filter(Product.category == category)
    
    # Recherche textuelle
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.sku.ilike(search_term)
            )
        )
    
    # Filtrer par prix
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Filtrer par stock
    if in_stock:
        query = query.filter(Product.stock_quantity > 0)
    
    # Tri
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Product.name.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    # Compter le total
    total = query.count()
    
    # Pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    # Calculer le nombre total de pages
    total_pages = math.ceil(total / limit) if total > 0 else 0
    
    # Convertir en réponse
    products_response = []
    for product in products:
        products_response.append(ProductListResponse(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            wholesale_price=product.wholesale_price,
            image=product.image,
            category=product.category,
            stock_quantity=product.stock_quantity,
            in_stock=product.stock_quantity > 0,
            sku=product.sku
        ))
    
    return ProductSearchResponse(
        products=products_response,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Détail complet d'un produit
    """
    product = db.query(Product).filter(
        and_(
            Product.product_id == product_id,
            Product.is_active == True
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Ne pas exposer le prix d'achat aux clients
    return ProductDetailResponse(
        product_id=product.product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        wholesale_price=product.wholesale_price,
        purchase_price=None,  # Caché
        image=product.image,
        images=[product.image] if product.image else [],
        category=product.category,
        stock_quantity=product.stock_quantity,
        in_stock=product.stock_quantity > 0,
        sku=product.sku,
        barcode=product.barcode,
        weight=product.weight,
        dimensions=product.dimensions,
        variants=[],  # TODO: Charger les variantes
        created_at=product.created_at,
        updated_at=product.updated_at
    )


@router.get("/categories/list", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    """
    Liste des catégories disponibles
    """
    categories = db.query(Product.category).filter(
        and_(
            Product.category.isnot(None),
            Product.is_active == True
        )
    ).distinct().all()
    
    return [cat[0] for cat in categories if cat[0]]


@router.get("/featured/list", response_model=List[ProductListResponse])
async def get_featured_products(
    db: Session = Depends(get_db),
    limit: int = Query(8, ge=1, le=50)
):
    """
    Produits mis en avant (les plus récents en stock)
    """
    products = db.query(Product).filter(
        and_(
            Product.is_active == True,
            Product.stock_quantity > 0
        )
    ).order_by(Product.created_at.desc()).limit(limit).all()
    
    return [
        ProductListResponse(
            product_id=p.product_id,
            name=p.name,
            description=p.description,
            price=p.price,
            wholesale_price=p.wholesale_price,
            image=p.image,
            category=p.category,
            stock_quantity=p.stock_quantity,
            in_stock=p.stock_quantity > 0,
            sku=p.sku
        )
        for p in products
    ]
