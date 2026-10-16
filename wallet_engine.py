import json
import os
from eth_account import Account

# BIP-39 Mnemonic desteğini etkinleştir
Account.enable_unaudited_hdwallet_features()

KEYSTORE_FILE = "keystore.json"

class CryptoWalletEngine:
    @staticmethod
    def create_wallet(password: str) -> dict:
        """Yeni 12 kelimelik tohum üretir, adresi çıkarır ve parolayla şifreleyip kaydeder."""
        account, mnemonic = Account.create_with_mnemonic()
        
        # Private key'i kullanıcı şifresiyle şifrele (Keystore V3 standardı)
        keystore_data = Account.encrypt(account.key.hex(), password)
        
        with open(KEYSTORE_FILE, "w", encoding="utf-8") as f:
            json.dump(keystore_data, f, indent=4)
            
        return {
            "address": account.address,
            "mnemonic": mnemonic,
            "private_key": account.key.hex()
        }

    @staticmethod
    def unlock_wallet(password: str):
        """Diskteki keystore dosyasını parola ile çözer ve Account nesnesini döner."""
        if not os.path.exists(KEYSTORE_FILE):
            raise FileNotFoundError("Kayıtlı cüzdan bulunamadı. Önce cüzdan oluşturun.")
            
        with open(KEYSTORE_FILE, "r", encoding="utf-8") as f:
            keystore_data = json.load(f)
            
        private_key = Account.decrypt(keystore_data, password)
        return Account.from_key(private_key)

    @staticmethod
    def wallet_exists() -> bool:
        """Diskte kayıtlı bir cüzdan dosyası olup olmadığını kontrol eder."""
        return os.path.exists(KEYSTORE_FILE)