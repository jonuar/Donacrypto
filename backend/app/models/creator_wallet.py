from datetime import datetime
from typing import Dict, Any

class CreatorWallet:
    """Modelo para gestionar las direcciones de wallet de los creadores"""

    SUPPORTED_CURRENCIES: list[str] = [
        # Layer 1 Blockchains principales
        "BTC",    # Bitcoin
        "ETH",    # Ethereum
        "BNB",    # Binance Smart Chain
        "ADA",    # Cardano
        "SOL",    # Solana
        "DOT",    # Polkadot
        "AVAX",   # Avalanche
        "MATIC",  # Polygon
        "ATOM",   # Cosmos
        "LTC",    # Litecoin
        "XRP",    # Ripple
        "TRX",    # Tron
        
        # Stablecoins
        "USDT",   # Tether
        "USDC",   # USD Coin
        "BUSD",   # Binance USD
        "DAI",    # Dai
        
        # DeFi Tokens populares
        "UNI",    # Uniswap
        "LINK",   # Chainlink
        "AAVE",   # Aave
        "COMP",   # Compound
        
        # Layer 2 y Scaling
        "ARB",    # Arbitrum
        "OP",     # Optimism
        
        # Meme Coins populares
        "DOGE",   # Dogecoin
        "SHIB",   # Shiba Inu
    ]

    def __init__(self, creator_email: str, wallet_address: str, currency_type: str) -> None:
        if currency_type not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Tipo de moneda no soportada. Use: {self.SUPPORTED_CURRENCIES}")
        
        self.creator_email: str = creator_email
        self.wallet_address: str = wallet_address
        self.currency_type: str = currency_type
        self.created_at: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario para persistencia"""
        return {
            "creator_email": self.creator_email,
            "wallet_address": self.wallet_address,
            "currency_type": self.currency_type,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreatorWallet':
        """Crea una instancia desde un diccionario"""
        return cls(
            creator_email=data['creator_email'],
            wallet_address=data['wallet_address'],
            currency_type=data['currency_type']
        )