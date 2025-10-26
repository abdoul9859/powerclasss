"""
API de gestion des paiements
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from boutique.backend.models.customer import StoreCustomer
from boutique.backend.models.order import StoreOrder, OrderStatus, PaymentStatus
from boutique.backend.models.payment import StorePayment, PaymentMethod
from boutique.backend.schemas.payment import (
    PaymentInitiate,
    PaymentResponse,
    PaymentCallback,
    PaymentVerify
)
from boutique.backend.utils.auth import get_current_customer
from boutique.backend.utils.payment import (
    generate_payment_reference,
    initiate_orange_money_payment,
    initiate_mtn_money_payment,
    initiate_moov_money_payment,
    initiate_wave_payment,
    verify_payment_status
)

router = APIRouter(prefix="/api/store/payments", tags=["store-payments"])


@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(
    payment_data: PaymentInitiate,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Initier un paiement pour une commande
    """
    # Vérifier que la commande existe et appartient au client
    order = db.query(StoreOrder).filter(
        StoreOrder.order_id == payment_data.order_id,
        StoreOrder.customer_id == current_customer.customer_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Vérifier que la commande n'est pas déjà payée
    if order.payment_status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette commande est déjà payée"
        )
    
    # Générer une référence de paiement unique
    payment_reference = generate_payment_reference()
    
    # Créer l'enregistrement de paiement
    payment = StorePayment(
        payment_reference=payment_reference,
        order_id=order.order_id,
        payment_method=PaymentMethod(payment_data.payment_method),
        amount=order.total_amount,
        currency="XOF",
        status="pending",
        payer_phone=payment_data.phone_number,
        payer_email=current_customer.email,
        payer_name=f"{current_customer.first_name} {current_customer.last_name}"
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Initier le paiement selon la méthode
    payment_result = {}
    
    if payment_data.payment_method == "orange_money":
        payment_result = initiate_orange_money_payment(
            amount=order.total_amount,
            phone_number=payment_data.phone_number or "",
            reference=payment_reference,
            description=f"Commande {order.order_number}"
        )
    elif payment_data.payment_method == "mtn_money":
        payment_result = initiate_mtn_money_payment(
            amount=order.total_amount,
            phone_number=payment_data.phone_number or "",
            reference=payment_reference,
            description=f"Commande {order.order_number}"
        )
    elif payment_data.payment_method == "moov_money":
        payment_result = initiate_moov_money_payment(
            amount=order.total_amount,
            phone_number=payment_data.phone_number or "",
            reference=payment_reference,
            description=f"Commande {order.order_number}"
        )
    elif payment_data.payment_method == "wave":
        payment_result = initiate_wave_payment(
            amount=order.total_amount,
            phone_number=payment_data.phone_number or "",
            reference=payment_reference,
            description=f"Commande {order.order_number}"
        )
    elif payment_data.payment_method == "credit_card":
        # TODO: Intégrer une passerelle de paiement par carte (Stripe, PayPal, etc.)
        payment_result = {
            "success": False,
            "error": "Paiement par carte non encore configuré",
            "instructions": "Veuillez utiliser Mobile Money pour le moment"
        }
    elif payment_data.payment_method == "cash_on_delivery":
        # Paiement à la livraison
        payment.status = "pending"
        order.payment_status = PaymentStatus.PENDING
        db.commit()
        
        return PaymentResponse(
            payment_id=payment.payment_id,
            payment_reference=payment_reference,
            status="pending",
            amount=order.total_amount,
            currency="XOF",
            payment_method=payment_data.payment_method,
            instructions="Vous paierez à la livraison",
            created_at=payment.created_at
        )
    
    # Mettre à jour le paiement avec les infos du provider
    if payment_result.get("success"):
        payment.provider_transaction_id = payment_result.get("transaction_id")
        payment.status = "processing"
        order.payment_status = PaymentStatus.PROCESSING
    else:
        payment.error_message = payment_result.get("error")
        payment.status = "failed"
        payment.failed_at = datetime.now()
    
    db.commit()
    db.refresh(payment)
    
    return PaymentResponse(
        payment_id=payment.payment_id,
        payment_reference=payment_reference,
        status=payment.status,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment_data.payment_method,
        payment_url=payment_result.get("payment_url"),
        ussd_code=payment_result.get("ussd_code"),
        instructions=payment_result.get("instructions"),
        created_at=payment.created_at
    )


@router.post("/callback")
async def payment_callback(
    callback_data: PaymentCallback,
    db: Session = Depends(get_db)
):
    """
    Callback du fournisseur de paiement (webhook)
    
    Cette endpoint est appelée par le fournisseur de paiement (Orange Money, MTN, etc.)
    pour notifier du statut du paiement
    """
    # Trouver le paiement
    payment = db.query(StorePayment).filter(
        StorePayment.payment_reference == callback_data.payment_reference
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    # Mettre à jour le statut du paiement
    payment.provider_transaction_id = callback_data.provider_transaction_id
    payment.status = callback_data.status
    
    if callback_data.status == "completed":
        payment.completed_at = datetime.now()
        
        # Mettre à jour la commande
        order = db.query(StoreOrder).filter(
            StoreOrder.order_id == payment.order_id
        ).first()
        
        if order:
            order.payment_status = PaymentStatus.COMPLETED
            order.status = OrderStatus.CONFIRMED
            order.confirmed_at = datetime.now()
    
    elif callback_data.status == "failed":
        payment.failed_at = datetime.now()
        payment.error_message = "Paiement échoué"
    
    db.commit()
    
    return {"message": "Callback traité avec succès"}


@router.post("/verify")
async def verify_payment(
    verify_data: PaymentVerify,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Vérifier le statut d'un paiement
    """
    # Trouver le paiement
    payment = db.query(StorePayment).filter(
        StorePayment.payment_reference == verify_data.payment_reference
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    # Vérifier que le paiement appartient au client
    order = db.query(StoreOrder).filter(
        StoreOrder.order_id == payment.order_id,
        StoreOrder.customer_id == current_customer.customer_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Vérifier auprès du fournisseur si le paiement est en attente
    if payment.status == "pending" or payment.status == "processing":
        provider_status = verify_payment_status(
            payment.payment_reference,
            payment.payment_method.value
        )
        
        if provider_status.get("status") == "completed":
            payment.status = "completed"
            payment.completed_at = datetime.now()
            order.payment_status = PaymentStatus.COMPLETED
            order.status = OrderStatus.CONFIRMED
            order.confirmed_at = datetime.now()
            db.commit()
    
    return {
        "payment_reference": payment.payment_reference,
        "status": payment.status,
        "amount": payment.amount,
        "currency": payment.currency,
        "payment_method": payment.payment_method.value,
        "created_at": payment.created_at,
        "completed_at": payment.completed_at
    }


@router.get("/{payment_reference}", response_model=PaymentResponse)
async def get_payment_status(
    payment_reference: str,
    current_customer: StoreCustomer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Obtenir le statut d'un paiement
    """
    payment = db.query(StorePayment).filter(
        StorePayment.payment_reference == payment_reference
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    # Vérifier que le paiement appartient au client
    order = db.query(StoreOrder).filter(
        StoreOrder.order_id == payment.order_id,
        StoreOrder.customer_id == current_customer.customer_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return PaymentResponse(
        payment_id=payment.payment_id,
        payment_reference=payment.payment_reference,
        status=payment.status,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method.value,
        created_at=payment.created_at
    )
