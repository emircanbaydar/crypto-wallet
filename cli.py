import getpass
from wallet_engine import CryptoWalletEngine
from blockchain import BlockchainService

def main():
    service = BlockchainService()
    active_account = None

    print("\n" + "="*45)
    print("🔒 GÜVENLİ KRİPTO CÜZDANI (SEPOLIA TESTNET)")
    print("="*45)

    if not service.is_connected():
        print("⚠️ Sepolia test ağına bağlanılamadı. İnternet bağlantınızı kontrol edin.")
    else:
        print("🌐 Sepolia test ağına başarıyla bağlanıldı.")

    while True:
        status = f"[{active_account.address[:6]}...{active_account.address[-4:]}]" if active_account else "[Kilitli]"
        print(f"\nDurum: {status}")
        print("1. Yeni Cüzdan Oluştur (12 Kelimelik Kurtarma İfadesi)")
        print("2. Cüzdan Kilidini Aç (Şifre ile)")
        print("3. Bakiye Sorgula")
        print("4. ETH Gönder (Transfer)")
        print("5. Çıkış")

        choice = input("\nSeçiminiz (1-5): ").strip()

        if choice == "1":
            if CryptoWalletEngine.wallet_exists():
                confirm = input("⚠️ Zaten kayıtlı bir cüzdan var. Üzerine yazılsın mı? (e/H): ")
                if confirm.lower() != "e":
                    continue

            pwd = getpass.getpass("Cüzdanı korumak için güçlü bir şifre girin: ")
            wallet_info = CryptoWalletEngine.create_wallet(pwd)
            print("\n✅ Cüzdan başarıyla oluşturuldu ve 'keystore.json' olarak şifrelendi!")
            print(f"📍 Adresiniz: {wallet_info['address']}")
            print(f"🔑 12 Kelimelik Kurtarma İfadeniz (Bunu Güvenli Yere Yazın!):\n   {wallet_info['mnemonic']}")

        elif choice == "2":
            pwd = getpass.getpass("Cüzdan şifrenizi girin: ")
            try:
                active_account = CryptoWalletEngine.unlock_wallet(pwd)
                print(f"\n🔓 Kilit açıldı! Aktif Adres: {active_account.address}")
            except Exception as e:
                print(f"\n❌ Hata: {e}")

        elif choice == "3":
            if not active_account:
                print("❌ Önce cüzdan kilidini açmalısınız (Seçenek 2).")
                continue
            balance = service.get_balance(active_account.address)
            print(f"\n💰 Mevcut Bakiye: {balance} SepoliaETH")

        elif choice == "4":
            if not active_account:
                print("❌ Önce cüzdan kilidini açmalısınız (Seçenek 2).")
                continue
            to_addr = input("Alıcı Adresi (0x...): ").strip()
            amount = float(input("Gönderilecek Tutar (ETH): ").strip())
            
            try:
                print("⏳ İşlem imzalanıyor ve ağa gönderiliyor...")
                tx_hash = service.send_eth(active_account, to_addr, amount)
                print(f"✅ Transfer Gönderildi! Tx Hash: {tx_hash}")
                print(f"🔗 Etherscan Takip: https://sepolia.etherscan.io/tx/{tx_hash}")
            except Exception as e:
                print(f"❌ Transfer başarısız: {e}")

        elif choice == "5":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim.")

if __name__ == "__main__":
    main()