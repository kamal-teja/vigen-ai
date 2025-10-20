import api from '../lib/api';

export const authService = {
  async register(email, fullName, password) {
    const response = await api.post('/auth/register', {
      email,
      full_name: fullName,
      password,
      role: 'creator',
    });
    return response.data;
  },

  async login(email, password) {
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    // Get user info
    const userResponse = await api.get('/auth/me');
    localStorage.setItem('user', JSON.stringify(userResponse.data));
    
    return { token: access_token, user: userResponse.data };
  },

  async refreshToken() {
    const refresh_token = localStorage.getItem('refresh_token');
    if (!refresh_token) {
      throw new Error('No refresh token available');
    }

    const response = await api.post('/auth/refresh', {
      refresh_token,
    });
    
    const { access_token, refresh_token: new_refresh_token } = response.data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('refresh_token', new_refresh_token);
    
    return access_token;
  },

  async getMe() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
};
