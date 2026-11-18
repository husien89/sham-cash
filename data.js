class DataManager {
    constructor() {
        this.notifications = JSON.parse(localStorage.getItem('sc_notifications')) || [];
        this.transactions = JSON.parse(localStorage.getItem('sc_transactions')) || [];
    }

    save() {
        localStorage.setItem('sc_notifications', JSON.stringify(this.notifications));
        localStorage.setItem('sc_transactions', JSON.stringify(this.transactions));
    }

    addNotification(title, message, type = 'info') {
        const notif = {
            id: Date.now(),
            title,
            message,
            type,
            date: new Date().toISOString(),
            read: false
        };
        this.notifications.unshift(notif);
        this.save();
    }

    markAsRead(id) {
        const n = this.notifications.find(n => n.id === id);
        if (n) n.read = true;
        this.save();
    }

    getNotifications(query = '') {
        return this.notifications.filter(n => 
            n.title.toLowerCase().includes(query.toLowerCase()) || 
            n.message.toLowerCase().includes(query.toLowerCase())
        );
    }

    addTransaction(amount, type, desc) {
        const tx = {
            id: Date.now(),
            amount,
            type, // 'in' or 'out'
            desc,
            date: new Date().toISOString()
        };
        this.transactions.unshift(tx);
        this.save();
        this.addNotification('New Transaction', `You have a new ${type === 'in' ? 'deposit' : 'withdrawal'} of ${amount}`, 'success');
    }

    getTransactions() {
        return this.transactions;
    }
}

const dataManager = new DataManager();