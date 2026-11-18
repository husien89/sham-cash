class Auth {
    constructor() {
        this.users = JSON.parse(localStorage.getItem('sc_users')) || [
            { username: 'admin', password: 'admin123', role: 'admin', name: 'Super Admin' }
        ];
    }

    saveUsers() {
        localStorage.setItem('sc_users', JSON.stringify(this.users));
    }

    login(username, password) {
        const user = this.users.find(u => u.username === username && u.password === password);
        if (user) {
            localStorage.setItem('sc_current_user', JSON.stringify(user));
            return true;
        }
        return false;
    }

    register(username, password, name) {
        if (this.users.find(u => u.username === username)) return false;
        const newUser = { username, password, role: 'user', name };
        this.users.push(newUser);
        this.saveUsers();
        return true;
    }

    logout() {
        localStorage.removeItem('sc_current_user');
        window.location.href = 'index.html';
    }

    getCurrentUser() {
        return JSON.parse(localStorage.getItem('sc_current_user'));
    }

    isAuthenticated() {
        return !!this.getCurrentUser();
    }

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'login.html';
        }
    }
}

const auth = new Auth();