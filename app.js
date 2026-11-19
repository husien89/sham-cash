// app.js (نسخة مكتملة)
class App {
    constructor() {
        this.currentUser = auth.getCurrentUser();
        this.init();
    }

    init() {
        // عرض اسم المستخدم في الصفحة الرئيسية
        if (this.currentUser) {
            document.getElementById('balance-display').textContent = `$ ${this.currentUser.balance || 500.00}`;
        }

        // عرض QR Code
        document.querySelector('.btn-receive')?.addEventListener('click', () => this.showQR());
    }

    showQR() {
        const user = auth.getCurrentUser();
        if (!user) return;

        const modal = document.getElementById('qr-modal');
        const canvas = document.getElementById('qr-canvas');
        const usernameDisplay = document.getElementById('qr-username');

        // توليد QR Code
        const qrData = `shamcash://pay?user=${user.username}`;
        QRCode.toCanvas(canvas, qrData, { width: 200 }, (error) => {
            if (error) console.error(error);
        });

        usernameDisplay.textContent = `اسم المستخدم: ${user.username}`;
        modal.style.display = 'block';
    }
}

const app = new App();
