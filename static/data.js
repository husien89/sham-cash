class DataManager {
    constructor() {
        this.transactions = JSON.parse(localStorage.getItem('sc_transactions')) || [];
        this.notifications = JSON.parse(localStorage.getItem('sc_notifications')) || [];
    }

    save() {
        localStorage.setItem('sc_transactions', JSON.stringify(this.transactions));
        localStorage.setItem('sc_notifications', JSON.stringify(this.notifications));
    }

    addTransaction(amount, type, description) {
        const tx = {
            id: Date.now(),
            amount,
            type,
            description,
            date: new Date().toISOString()
        };
        this.transactions.unshift