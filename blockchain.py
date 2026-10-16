from web3 import Web3
from decimal import Decimal

# Herkese açık güvenilir Sepolia test ağı RPC adresi
SEPOLIA_RPC_URL = "https://rpc.sepolia.org"

class BlockchainService:
    def __init__(self, rpc_url: str = SEPOLIA_RPC_URL):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

    def is_connected(self) -> bool:
        return self.w3.is_connected()

    def get_balance(self, address: str) -> Decimal:
        """Adresin Sepolia ETH bakiyesini sorgular."""
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.from_wei(balance_wei, "ether")
        return Decimal(str(balance_eth))

    def send_eth(self, account, to_address: str, amount_eth: float) -> str:
        """Çevrimdışı işlem oluşturur, private key ile imzalar ve ağa yayar."""
        to_checksum = Web3.to_checksum_address(to_address)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        tx = {
            "nonce": nonce,
            "to": to_checksum,
            "value": self.w3.to_wei(amount_eth, "ether"),
            "gas": 21000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": 11155111  # Sepolia Testnet Chain ID
        }

        # İşlemi lokalde güvenli bir şekilde imzala
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=account.key)
        
        # İmzalanmış veriyi blokzincire ilet
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.w3.to_hex(tx_hash)