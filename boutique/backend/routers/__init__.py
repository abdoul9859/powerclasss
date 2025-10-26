"""
Routers API pour la boutique en ligne
"""
from .products import router as products_router
from .customers import router as customers_router
from .cart import router as cart_router
from .orders import router as orders_router
from .payments import router as payments_router

__all__ = [
    'products_router',
    'customers_router',
    'cart_router',
    'orders_router',
    'payments_router',
]
