import os
import pytest
from wallet_engine import CryptoWalletEngine, KEYSTORE_FILE

def test_wallet_creation_and_unlock():
    password = "TestGucluSifre123!"
    
    # 1. Test: Cüzdan üretimi
    wallet_info = CryptoWalletEngine.create_wallet(password)
    assert "address" in wallet_info
    assert wallet_info["address"].startswith("0x")
    assert len(wallet_info["mnemonic"].split()) == 12
    assert os.path.exists(KEYSTORE_FILE)

    # 2. Test: Doğru şifre ile kilit açma
    account = CryptoWalletEngine.unlock_wallet(password)
    assert account.address == wallet_info["address"]

    # 3. Test: Yanlış şifre ile hata fırlatma
    with pytest.raises(Exception):
        CryptoWalletEngine.unlock_wallet("YanlisSifre")

    # Temizlik
    if os.path.exists(KEYSTORE_FILE):
        os.remove(KEYSTORE_FILE)