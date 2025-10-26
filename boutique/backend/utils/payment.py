"""
Utilitaires pour les paiements Mobile Money et cartes bancaires
"""
import uuid
import requests
from typing import Optional, Dict
from decimal import Decimal
import os
import logging

logger = logging.getLogger(__name__)


def generate_payment_reference() -> str:
    """Générer une référence de paiement unique"""
    return f"PAY-{uuid.uuid4().hex[:12].upper()}"


# ==================== ORANGE MONEY ====================

def initiate_orange_money_payment(
    amount: Decimal,
    phone_number: str,
    reference: str,
    description: str = "Paiement boutique en ligne"
) -> Dict:
    """
    Initier un paiement Orange Money
    
    Note: Ceci est un exemple. Vous devez adapter selon l'API Orange Money de votre pays.
    Documentation: https://developer.orange.com/apis/orange-money-webpay/
    """
    api_url = os.getenv("ORANGE_MONEY_API_URL", "https://api.orange.com/orange-money-webpay/...")
    merchant_key = os.getenv("ORANGE_MONEY_MERCHANT_KEY", "")
    
    if not merchant_key:
        logger.warning("Orange Money merchant key not configured")
        return {
            "success": False,
            "error": "Configuration Orange Money manquante",
            "ussd_code": "*144*4*6#",  # Code USSD générique
            "instructions": "Composez *144*4*6# et suivez les instructions"
        }
    
    try:
        payload = {
            "merchant_key": merchant_key,
            "amount": float(amount),
            "currency": "XOF",
            "phone_number": phone_number,
            "reference": reference,
            "description": description,
            "return_url": os.getenv("PAYMENT_RETURN_URL", ""),
            "cancel_url": os.getenv("PAYMENT_CANCEL_URL", ""),
            "notif_url": os.getenv("PAYMENT_NOTIF_URL", "")
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "transaction_id": data.get("transaction_id"),
            "payment_url": data.get("payment_url"),
            "ussd_code": data.get("ussd_code", "*144*4*6#"),
            "instructions": "Composez le code USSD et suivez les instructions"
        }
        
    except Exception as e:
        logger.error(f"Orange Money payment error: {e}")
        return {
            "success": False,
            "error": str(e),
            "ussd_code": "*144*4*6#",
            "instructions": "Composez *144*4*6# et suivez les instructions"
        }


# ==================== MTN MONEY ====================

def initiate_mtn_money_payment(
    amount: Decimal,
    phone_number: str,
    reference: str,
    description: str = "Paiement boutique en ligne"
) -> Dict:
    """
    Initier un paiement MTN Mobile Money
    
    Note: Ceci est un exemple. Vous devez adapter selon l'API MTN MoMo.
    Documentation: https://momodeveloper.mtn.com/
    """
    api_url = os.getenv("MTN_MOMO_API_URL", "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay")
    api_key = os.getenv("MTN_MOMO_API_KEY", "")
    subscription_key = os.getenv("MTN_MOMO_SUBSCRIPTION_KEY", "")
    
    if not api_key or not subscription_key:
        logger.warning("MTN MoMo credentials not configured")
        return {
            "success": False,
            "error": "Configuration MTN MoMo manquante",
            "ussd_code": "*133#",
            "instructions": "Composez *133# et suivez les instructions"
        }
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Reference-Id": reference,
            "X-Target-Environment": os.getenv("MTN_MOMO_ENVIRONMENT", "sandbox"),
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": str(amount),
            "currency": "XOF",
            "externalId": reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": description,
            "payeeNote": description
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        return {
            "success": True,
            "transaction_id": reference,
            "ussd_code": "*133#",
            "instructions": "Composez *133# et suivez les instructions pour valider le paiement"
        }
        
    except Exception as e:
        logger.error(f"MTN MoMo payment error: {e}")
        return {
            "success": False,
            "error": str(e),
            "ussd_code": "*133#",
            "instructions": "Composez *133# et suivez les instructions"
        }


# ==================== MOOV MONEY ====================

def initiate_moov_money_payment(
    amount: Decimal,
    phone_number: str,
    reference: str,
    description: str = "Paiement boutique en ligne"
) -> Dict:
    """
    Initier un paiement Moov Money
    
    Note: Adaptez selon l'API Moov Money de votre pays
    """
    return {
        "success": False,
        "error": "Moov Money non configuré",
        "ussd_code": "*155#",
        "instructions": "Composez *155# et suivez les instructions"
    }


# ==================== WAVE ====================

def initiate_wave_payment(
    amount: Decimal,
    phone_number: str,
    reference: str,
    description: str = "Paiement boutique en ligne"
) -> Dict:
    """
    Initier un paiement Wave
    
    Note: Adaptez selon l'API Wave
    """
    return {
        "success": False,
        "error": "Wave non configuré",
        "instructions": "Ouvrez l'application Wave et effectuez le paiement"
    }


# ==================== VÉRIFICATION ====================

def verify_payment_status(payment_reference: str, provider: str) -> Dict:
    """
    Vérifier le statut d'un paiement auprès du fournisseur
    
    Args:
        payment_reference: Référence du paiement
        provider: Fournisseur (orange_money, mtn_money, etc.)
    
    Returns:
        Dict avec le statut du paiement
    """
    # TODO: Implémenter la vérification selon chaque provider
    logger.info(f"Verifying payment {payment_reference} with provider {provider}")
    
    return {
        "status": "pending",
        "message": "Vérification en cours"
    }
