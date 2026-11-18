import QRCode from 'qrcode';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

class App {
    constructor() {
        this.currentView = 'index';
        this.init();
    }

    init() {
        // Navigation
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('href').split('/')[1];
                this.navigate(page);
            });
        });

        // QR Scanner Simulation
        document.getElementById('btn-scan')?.addEventListener('click', () => {
            const canvas = document.getElementById('qr-canvas');
            QRCode.toCanvas(canvas, 'Sham-Cash-User-123', (error) => {
                if (error) console.error(error);
                document.getElementById('qr-container').classList.remove('hidden');
            });
        });

        // PDF Export
        document.getElementById('btn-export')?.addEventListener('click', () => this.exportPDF());
        
        // Notification Refresh
        this.updateNotificationBadge();
    }

    navigate(page) {
        document.querySelectorAll('.view').forEach(el => el.classList.add('hidden'));
        document.getElementById(page)?.classList.remove('hidden');
        this.currentView = page;
        
        if (page === 'notifications') this.renderNotifications();
        if (page === 'settings') this.renderSettings();
    }

    updateNotificationBadge() {
        const unread = dataManager.notifications.filter(n => !n.read).length;
        const badge = document.getElementById('notif-badge');
        if (badge) {
            badge.textContent = unread;
            badge.style.display = unread > 0 ? 'inline-block' : 'none';
        }
    }

    renderNotifications() {
        const list = document.getElementById('notif-list');
        const items = dataManager.getNotifications(document.getElementById('search-notif')?.value || '');
        list.innerHTML = items.map(n => `
            <div class="notification-item ${n.read ? 'read' : 'unread'}">
                <strong>${n.title}</strong>
                <p>${n.message}</p>
                <small>${new Date(n.date).toLocaleString()}</small>
            </div>
        `).join('');
    }

    exportPDF() {
        const doc = new jsPDF();
        const user = auth.getCurrentUser();
        
        doc.setFontSize(18);
        doc.text("Sham Cash - Account Statement", 10, 10);
        doc.setFontSize(12);
        doc.text(`User: ${user.name}`, 10, 20);
        doc.text(`Date: ${new Date().toLocaleDateString()}`, 10, 28);

        const txs = dataManager.getTransactions().map(t => [
            new Date(t.date).toLocaleDateString(),
            t.desc,
            t.type === 'in' ? `+ ${t.amount}` : `- ${t.amount}`
        ]);

        doc.autoTable({
            head: [['Date', 'Description', 'Amount']],
            body: txs,
            startY: 35
        });

        doc.save('sham-cash-statement.pdf');
    }
}

const app = new App();