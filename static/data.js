class DataManager {
    constructor() {
        this.transactions = JSON.parse(localStorage.getItem('sc_transactions')) || [
            { id: 1, name: 'أحمد عيسى حسين', amount: -17, date: '2026-09-01 18:16:02', type: 'out' },
            { id: 2, name: 'منهل خليل العمر', amount: -6, date: '2026-08-31 15:49:28', type: 'out' },
            { id: 3, name: 'عبدالله محمد عمر', amount: 25, date: '2026-08-30 18:09:33', type: 'in' }
        ];
    }

    save() { localStorage.setItem('sc_transactions', JSON.stringify(this.transactions)); }

    addTransaction(name, amount, type) {
        const tx = {
            id: Date.now(),
            name,
            amount,
            date: new Date().toISOString().slice(0,19).replace('T', ' '),
            type
        };
        this.transactions.unshift(tx);
        this.save();
    }
}
const dataManager = new DataManager();