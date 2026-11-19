class App {
    async init() {
        try {
            this.currentUser = await auth.getCurrentUser();
        } catch (_error) {
            window.location.replace('/');
            return;
        }

        this.renderBalance();
        await this.loadTransactions();

        document.querySelector('.btn-receive')?.addEventListener('click', () => this.showQR());
        document.querySelector('.btn-send')?.addEventListener('click', () => this.showSend());
        document.getElementById('logout-button')?.addEventListener('click', () => auth.logout());
        document.getElementById('close-qr')?.addEventListener('click', () => this.hideQR());
        document.getElementById('close-send')?.addEventListener('click', () => this.hideSend());
        document.getElementById('send-form')?.addEventListener('submit', (event) => this.sendMoney(event));

        document.querySelectorAll('.modal').forEach((modal) => {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) modal.hidden = true;
            });
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') document.querySelectorAll('.modal').forEach((modal) => { modal.hidden = true; });
        });
    }

    renderBalance() {
        const balance = document.getElementById('balance-display');
        if (!balance) return;
        const amount = Number(this.currentUser?.balance);
        balance.textContent = `$ ${Number.isFinite(amount) ? amount.toFixed(2) : '0.00'}`;
    }

    async loadTransactions() {
        try {
            const response = await fetch('/api/transactions', { credentials: 'same-origin' });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'تعذر تحميل التحويلات');
            this.renderTransactions(result.transactions);
        } catch (error) {
            this.renderTransactions([], error.message);
        }
    }

    renderTransactions(transactions, errorMessage = '') {
        const list = document.getElementById('transactions-list');
        if (!list) return;
        if (errorMessage) return this.showListMessage(errorMessage);
        if (!transactions.length) return this.showListMessage('لا توجد تحويلات بعد');

        list.replaceChildren(...transactions.map((transaction) => {
            const item = document.createElement('div');
            item.className = `transaction ${transaction.direction === 'in' ? 'in' : 'out'}`;
            const details = document.createElement('div');
            const name = document.createElement('span');
            name.textContent = transaction.name;
            const date = document.createElement('div');
            date.className = 'meta';
            date.textContent = transaction.created_at;
            details.append(name, date);

            const amount = document.createElement('strong');
            amount.className = 'amount';
            amount.textContent = `${transaction.direction === 'out' ? '-' : '+'}$${Number(transaction.amount).toFixed(2)}`;
            item.append(details, amount);
            return item;
        }));
    }

    showListMessage(text) {
        const list = document.getElementById('transactions-list');
        if (!list) return;
        const message = document.createElement('p');
        message.className = 'empty';
        message.textContent = text;
        list.replaceChildren(message);
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

        try {
            await QRCode.toCanvas(canvas, `shamcash://pay?user=${encodeURIComponent(this.currentUser.username)}`, { width: 200, margin: 2 });
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

    showSend() {
        const modal = document.getElementById('send-modal');
        if (modal) {
            modal.hidden = false;
            document.getElementById('recipient')?.focus();
        }
    }

    hideSend() {
        const modal = document.getElementById('send-modal');
        if (modal) modal.hidden = true;
    }

    async sendMoney(event) {
        event.preventDefault();
        const form = event.currentTarget;
        const values = new FormData(form);
        const recipient = String(values.get('recipient') || '').trim();
        const amount = Number(String(values.get('amount') || '').trim());
        const errorBox = document.getElementById('send-error');
        const submit = form.querySelector('[type="submit"]');
        errorBox.hidden = true;

        if (!recipient || recipient.length > 32) {
            errorBox.textContent = 'أدخل اسم مستخدم صحيحاً للمستلم';
            errorBox.hidden = false;
            return;
        }
        if (!Number.isFinite(amount) || amount <= 0 || amount > 100000) {
            errorBox.textContent = 'المبلغ غير صالح';
            errorBox.hidden = false;
            return;
        }

        submit.disabled = true;
        try {
            const response = await fetch('/api/transactions', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recipient, amount }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'تعذر تنفيذ التحويل');
            this.currentUser.balance = result.balance;
            this.renderBalance();
            form.reset();
            this.hideSend();
            await this.loadTransactions();
        } catch (error) {
            errorBox.textContent = error.message;
            errorBox.hidden = false;
        } finally {
            submit.disabled = false;
        }
    }
}

const app = new App();
app.init();
