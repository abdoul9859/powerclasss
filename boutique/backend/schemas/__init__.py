"""
Schémas Pydantic pour l'API de la boutique
"""
from .customer import (
    CustomerRegister,
    CustomerLogin,
    CustomerResponse,
    CustomerUpdate,
    TokenResponse
)
from .product import (
    ProductListResponse,
    ProductDetailResponse,
    ProductFilterParams
)
from .cart import (
    CartItem,
    CartResponse,
    AddToCartRequest
)
from .order import (
    OrderCreate,
    OrderResponse,
    OrderItemResponse,
    OrderListResponse,
    OrderStatusUpdate
)
from .payment import (
    PaymentInitiate,
    PaymentResponse,
    PaymentCallback
)

__all__ = [
    # Customer
    'CustomerRegister',
    'CustomerLogin',
    'CustomerResponse',
    'CustomerUpdate',
    'TokenResponse',
    # Product
    'ProductListResponse',
    'ProductDetailResponse',
    'ProductFilterParams',
    # Cart
    'CartItem',
    'CartResponse',
    'AddToCartRequest',
    # Order
    'OrderCreate',
    'OrderResponse',
    'OrderItemResponse',
    'OrderListResponse',
    'OrderStatusUpdate',
    # Payment
    'PaymentInitiate',
    'PaymentResponse',
    'PaymentCallback',
]
