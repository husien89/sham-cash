class App {
    async init() {
        try {
            this.currentUser = await auth.getCurrentUser();
        } catch (_error) {
            window.location.replace('/');
            return;
        }

        const balance = document.getElementById('balance-display');
        if (balance) {
            const amount = Number(this.currentUser.balance);
            balance.textContent = `$ ${Number.isFinite(amount) ? amount.toFixed(2) : '0.00'}`;
        }

        document.querySelector('.btn-receive')?.addEventListener('click', () => this.showQR());
        document.getElementById('logout-button')?.addEventListener('click', () => auth.logout());
        document.getElementById('close-qr')?.addEventListener('click', () => this.hideQR());
        document.getElementById('qr-modal')?.addEventListener('click', (event) => {
            if (event.target.id === 'qr-modal') this.hideQR();
        });
    }

    async showQR() {
        const modal = document.getElementById('qr-modal');
        const canvas = document.getElementById('qr-canvas');
        const usernameDisplay = document.getElementById('qr-username');
        if (!modal || !canvas || !usernameDisplay || !this.currentUser) return;
        if (!window.QRCode?.toCanvas) {
            usernameDisplay.textContent = 'تعذر تحميل خدمة رمز QR. حاول تحديث الصفحة.';
            modal.hidden = false;
            return;
        }

        const qrData = `shamcash://pay?user=${encodeURIComponent(this.currentUser.username)}`;
        try {
            await QRCode.toCanvas(canvas, qrData, { width: 200, margin: 2 });
            usernameDisplay.textContent = `اسم المستخدم: ${this.currentUser.username}`;
        } catch (error) {
            console.error('QR generation failed:', error);
            usernameDisplay.textContent = 'تعذر إنشاء رمز QR.';
        }
        modal.hidden = false;
    }

    hideQR() {
        const modal = document.getElementById('qr-modal');
        if (modal) modal.hidden = true;
    }
}

const app = new App();
app.init();
