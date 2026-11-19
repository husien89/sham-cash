class Auth {
    async request(path, options = {}) {
        const response = await fetch(path, {
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options,
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(result.error || 'تعذر إكمال الطلب');
        }
        return result;
    }

    async login(username, password) {
        const result = await this.request('/api/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        return result.user;
    }

    async register(username, password, name, email = '') {
        const result = await this.request('/api/register', {
            method: 'POST',
            body: JSON.stringify({ username, password, name, email }),
        });
        return result.user;
    }

    async getCurrentUser() {
        const result = await this.request('/api/me', { method: 'GET' });
        return result.user;
    }

    async logout() {
        await this.request('/api/logout', { method: 'POST', body: '{}' });
        window.location.assign('/');
    }
}

const auth = new Auth();
