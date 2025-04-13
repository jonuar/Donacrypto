from datetime import datetime
from flask import current_app
from ..extensions import mongo

class Donation:
    """Modelo para las donaciones"""

    def __init__(self, sender_email, receiver_email, amount, tx_hash, currency="ETH"):
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.amount = amount
        self.currency = currency
        self.tx_hash = tx_hash
        self.timestamp = datetime.now()

    def save_to_db(self):
        """Guarda la donación en la base de datos"""
        # Verifica si la donación ya existe
        try:
            mongo.db.donations.insert_one({
                "sender": self.sender_email,
                "receiver": self.receiver_email,
                "amount": self.amount,
                "currency": self.currency,
                "tx_hash": self.tx_hash,
                "created_at": self.timestamp
            })
        except Exception as e:
            current_app.logger.error(f"[Donation.save_to_db] Error: {e}")
            return None
        return True
