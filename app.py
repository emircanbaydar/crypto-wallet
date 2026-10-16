import customtkinter as ctk
import qrcode
from PIL import Image
import pyperclip
import threading

from wallet_engine import CryptoWalletEngine
from blockchain import BlockchainService

# Görsel Stil Ayarları
ctk.set_appearance_mode("dark")

# Renk Paleti (Glassmorphic / Koyu Mavi & Neon)
BG_COLOR = "#0f172a"          # Derin Gece Mavisi
CARD_BG = "#1e293b"           # Grafit Mavi
ACCENT_BLUE = "#0ea5e9"       # Neon Parlak Mavi
TEXT_MUTED = "#94a3b8"        # Mat Gri
BORDER_COLOR = "#334155"      # Sınır Grisi

class CryptoWalletApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WEB3 CRYPTO WALLET")
        self.geometry("520x720")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        self.service = BlockchainService(rpc_url="https://ethereum-sepolia-rpc.publicnode.com")
        self.active_account = None

        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color=BG_COLOR, border_color=BORDER_COLOR, border_width=1)
        self.container.pack(fill="both", expand=True, padx=15, pady=15)

        if CryptoWalletEngine.wallet_exists():
            self.show_unlock_view()
        else:
            self.show_create_view()

    def clear_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ----------------- GÖRÜNÜM 1: CÜZDAN OLUŞTURMA -----------------
    def show_create_view(self):
        self.clear_view()

        title = ctk.CTkLabel(self.container, text="Yeni Cüzdan Oluştur", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#ffffff")
        title.pack(pady=(40, 10))

        desc = ctk.CTkLabel(self.container, text="Cüzdanınızı korumak için güçlü bir şifre belirleyin.\nBu şifre özel anahtarınızı (private key) güvenle şifreler.", text_color=TEXT_MUTED, font=ctk.CTkFont(family="Inter", size=13), justify="center")
        desc.pack(pady=(0, 30))

        self.entry_create_pwd = ctk.CTkEntry(self.container, placeholder_text="Şifre belirleyin", show="*", width=340, height=45, fg_color=CARD_BG, border_color=BORDER_COLOR, text_color="#ffffff")
        self.entry_create_pwd.pack(pady=10)

        btn_create = ctk.CTkButton(self.container, text="Cüzdanı Oluştur ve Şifrele", fg_color=ACCENT_BLUE, hover_color="#0284c7", text_color="#ffffff", width=340, height=45, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), corner_radius=10, command=self.handle_create_wallet)
        btn_create.pack(pady=25)

        self.lbl_create_status = ctk.CTkLabel(self.container, text="", font=ctk.CTkFont(size=12))
        self.lbl_create_status.pack(pady=5)

    def handle_create_wallet(self):
        pwd = self.entry_create_pwd.get().strip()
        if not pwd or len(pwd) < 4:
            self.lbl_create_status.configure(text="Şifre en az 4 karakter olmalıdır!", text_color="#ef4444")
            return

        wallet_info = CryptoWalletEngine.create_wallet(pwd)
        self.show_mnemonic_popup(wallet_info["mnemonic"], pwd)

    def show_mnemonic_popup(self, mnemonic, pwd):
        self.clear_view()

        title = ctk.CTkLabel(self.container, text="⚠️ Kurtarma İfadeniz (BIP-39)", font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color="#f59e0b")
        title.pack(pady=(35, 10))

        warning = ctk.CTkLabel(self.container, text="Bu 12 kelimeyi kimseyle paylaşmayın ve güvenli bir yere kaydedin!\nCüzdanınızı kurtarmanın tek yolu budur.", text_color=TEXT_MUTED, font=ctk.CTkFont(family="Inter", size=12), justify="center")
        warning.pack(pady=(0, 20))

        mnemonic_box = ctk.CTkTextbox(self.container, width=380, height=120, fg_color=CARD_BG, border_color=BORDER_COLOR, border_width=1, font=ctk.CTkFont(family="Consolas", size=14, weight="bold"), corner_radius=12)
        mnemonic_box.pack(pady=10)
        mnemonic_box.insert("0.0", mnemonic)
        mnemonic_box.configure(state="disabled")

        btn_copied = ctk.CTkButton(self.container, text="12 Kelimeyi Kopyala", fg_color="#334155", hover_color="#475569", text_color="#ffffff", width=200, height=36, corner_radius=8, command=lambda: pyperclip.copy(mnemonic))
        btn_copied.pack(pady=10)

        btn_continue = ctk.CTkButton(self.container, text="Kaydettim, Cüzdana Giriş Yap", fg_color=ACCENT_BLUE, hover_color="#0284c7", text_color="#ffffff", width=340, height=45, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), corner_radius=10, command=lambda: self.login_with_password(pwd))
        btn_continue.pack(pady=(20, 10))

    # ----------------- GÖRÜNÜM 2: KİLİT AÇMA (LOGIN) -----------------
    def show_unlock_view(self):
        self.clear_view()

        title = ctk.CTkLabel(self.container, text="🔒 Cüzdan Kilidini Aç", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#ffffff")
        title.pack(pady=(50, 10))

        desc = ctk.CTkLabel(self.container, text="Keystore dosyasını açmak için şifrenizi girin.", text_color=TEXT_MUTED, font=ctk.CTkFont(family="Inter", size=13))
        desc.pack(pady=(0, 35))

        self.entry_unlock_pwd = ctk.CTkEntry(self.container, placeholder_text="Cüzdan Şifreniz", show="*", width=340, height=45, fg_color=CARD_BG, border_color=BORDER_COLOR, text_color="#ffffff")
        self.entry_unlock_pwd.pack(pady=10)

        btn_unlock = ctk.CTkButton(self.container, text="Kilidi Aç", fg_color=ACCENT_BLUE, hover_color="#0284c7", text_color="#ffffff", width=340, height=45, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), corner_radius=10, command=self.handle_unlock_wallet)
        btn_unlock.pack(pady=20)

        self.lbl_unlock_status = ctk.CTkLabel(self.container, text="", font=ctk.CTkFont(size=12))
        self.lbl_unlock_status.pack(pady=5)

    def handle_unlock_wallet(self):
        pwd = self.entry_unlock_pwd.get().strip()
        self.login_with_password(pwd)

    def login_with_password(self, pwd):
        try:
            self.active_account = CryptoWalletEngine.unlock_wallet(pwd)
            self.show_dashboard_view()
        except Exception:
            if hasattr(self, "lbl_unlock_status"):
                self.lbl_unlock_status.configure(text="❌ Hatalı şifre veya bozuk dosya!", text_color="#ef4444")

    # ----------------- GÖRÜNÜM 3: ANA CÜZDAN PANELİ (DASHBOARD) -----------------
    def show_dashboard_view(self):
        self.clear_view()

        # Üst Bilgi Barı
        top_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=(15, 5))

        network_badge = ctk.CTkLabel(top_frame, text="● Sepolia Testnet", text_color="#10b981", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
        network_badge.pack(side="left")

        btn_lock = ctk.CTkButton(top_frame, text="Kilitle", width=70, height=28, fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), corner_radius=6, command=self.show_unlock_view)
        btn_lock.pack(side="right")

        # Bakiye Kartı (Makyajlı Cam Efektli)
        bal_card = ctk.CTkFrame(self.container, fg_color=CARD_BG, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        bal_card.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(bal_card, text="Toplam Bakiye", text_color=TEXT_MUTED, font=ctk.CTkFont(family="Inter", size=13)).pack(pady=(16, 2))
        self.lbl_balance = ctk.CTkLabel(bal_card, text="-- SepoliaETH", font=ctk.CTkFont(family="Inter", size=28, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_balance.pack(pady=(0, 2))
        
        self.lbl_balance_usd = ctk.CTkLabel(bal_card, text="≈ $--,00 USD", font=ctk.CTkFont(family="Inter", size=14), text_color=TEXT_MUTED)
        self.lbl_balance_usd.pack(pady=(0, 16))

        # Adres Kopyalama ve QR Kod Alanı
        middle_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        middle_frame.pack(pady=5)

        # QR Kod
        qr_img = self.generate_qr(self.active_account.address)
        ctk_qr = ctk.CTkImage(light_image=qr_img, dark_image=qr_img, size=(130, 130))
        qr_label = ctk.CTkLabel(middle_frame, image=ctk_qr, text="")
        qr_label.pack(pady=10)

        # Kopyalanabilir Adres
        short_addr = f"{self.active_account.address[:10]}...{self.active_account.address[-8:]}"
        btn_copy_addr = ctk.CTkButton(self.container, text=f"{short_addr}  📋", width=260, height=38, fg_color="#1e293b", hover_color="#334155", border_color=BORDER_COLOR, border_width=1, text_color="#ffffff", font=ctk.CTkFont(family="Consolas", size=13), corner_radius=8, command=self.copy_address)
        btn_copy_addr.pack(pady=5)

        # Tablar: Transfer Gönder
        tabview = ctk.CTkTabview(self.container, width=440, height=220, fg_color="transparent")
        tabview.pack(pady=15)
        tab_send = tabview.add("ETH Gönder")

        self.entry_to = ctk.CTkEntry(tab_send, placeholder_text="Alıcı Adresi (0x...)", width=380, height=42, fg_color=CARD_BG, border_color=BORDER_COLOR, text_color="#ffffff")
        self.entry_to.pack(pady=(15, 5))

        self.entry_amount = ctk.CTkEntry(tab_send, placeholder_text="Miktar (ETH, örn: 0.05)", width=380, height=42, fg_color=CARD_BG, border_color=BORDER_COLOR, text_color="#ffffff")
        self.entry_amount.pack(pady=5)

        self.btn_send = ctk.CTkButton(tab_send, text="İmzala ve Gönder", fg_color=ACCENT_BLUE, hover_color="#0284c7", text_color="#ffffff", width=380, height=42, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), corner_radius=10, command=self.handle_send_tx)
        self.btn_send.pack(pady=12)

        self.lbl_tx_status = ctk.CTkLabel(tab_send, text="", font=ctk.CTkFont(family="Inter", size=12), wraplength=360)
        self.lbl_tx_status.pack(pady=2)

        self.refresh_balance_async()

    def generate_qr(self, data: str) -> Image.Image:
        qr = qrcode.QRCode(box_size=3, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white").convert("RGB")

    def copy_address(self):
        pyperclip.copy(self.active_account.address)

    def refresh_balance_async(self):
        def _fetch():
            try:
                bal = self.service.get_balance(self.active_account.address)
                self.lbl_balance.configure(text=f"{bal:.4f} SepoliaETH")
                # Basit fiktif kur hesabı (1 ETH = ~2500 USD)
                usd_val = float(bal) * 2780.00
                self.lbl_balance_usd.configure(text=f"≈ ${usd_val:,.2f} USD")
            except Exception:
                self.lbl_balance.configure(text="0.0000 SepoliaETH")
                self.lbl_balance_usd.configure(text="≈ $0.00 USD")
        threading.Thread(target=_fetch, daemon=True).start()

    def handle_send_tx(self):
        to_addr = self.entry_to.get().strip()
        amount_str = self.entry_amount.get().strip()

        if not to_addr or not amount_str:
            self.lbl_tx_status.configure(text="Adres ve miktar girilmelidir!", text_color="#ef4444")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            self.lbl_tx_status.configure(text="Geçersiz miktar formatı!", text_color="#ef4444")
            return

        self.btn_send.configure(state="disabled", text="İşlem Gönderiliyor...")
        self.lbl_tx_status.configure(text="⏳ İşlem imzalanıyor...", text_color="#f59e0b")

        def _send():
            try:
                tx_hash = self.service.send_eth(self.active_account, to_addr, amount)
                self.lbl_tx_status.configure(text=f"✅ Başarılı!\nTx: {tx_hash[:22]}...", text_color="#10b981")
                self.refresh_balance_async()
            except Exception as e:
                err_msg = str(e)
                if "insufficient funds" in err_msg.lower():
                    err_msg = "Yetersiz bakiye (Gaz veya ETH eksik)!"
                self.lbl_tx_status.configure(text=f"❌ {err_msg[:60]}", text_color="#ef4444")
            finally:
                self.btn_send.configure(state="normal", text="İmzala ve Gönder")

        threading.Thread(target=_send, daemon=True).start()

if __name__ == "__main__":
    app = CryptoWalletApp()
    app.mainloop()