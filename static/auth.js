class Auth {
    constructor() {
        this.users = JSON.parse(localStorage.getItem('sc_users')) || [
            { username: 'admin', password: 'admin123', name: 'المدير العام', email: 'admin@shamcash.com' }
        ];
    }

    save() { localStorage.setItem('sc_users', JSON.stringify(this.users)); }

    login(username, password) {
        const user = this.users.find(u => u.username === username && u.password === password);
        if (user) {
            localStorage.setItem('sc_session', JSON.stringify(user));
            return true;
        }
        return false;
    }

    register(username, password, email, name) {
        if (this.users.find(u => u.username === username)) return false;
        this.users.push({ username, password, email, name, role: 'user' });
        this.save();
        return true;
    }

    logout() {
        localStorage.removeItem('sc_session');
        window.location.href = 'login.html';
    }

    getCurrentUser() { return JSON.parse(localStorage.getItem('sc_session')); }
    isAuthenticated() { return !!this.getCurrentUser(); }
}
const auth = new Auth();