import api from '../lib/api';

export const adService = {
  async createAd(data) {
    const response = await api.post('/ads', data);
    return response.data;
  },

  async getAdStatus(advId) {
    const response = await api.get(`/ads/${advId}/status`);
    return response.data;
  },

  async getVideoUrl(advId) {
    const response = await api.get(`/ads/${advId}/video-url`);
    return response.data;
  },

  async getAd(advId) {
    const response = await api.get(`/ads/${advId}`);
    return response.data;
  },

  async updateAd(advId, data) {
    const response = await api.put(`/ads/${advId}`, data);
    return response.data;
  },

  async listAds() {
    const response = await api.get('/ads');
    return response.data;
  },
};
