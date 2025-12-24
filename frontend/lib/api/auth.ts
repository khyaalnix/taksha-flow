import { apiClient } from './client';
import type { AuthCheckResponse, LoginResponse, LogoutResponse } from '@/types/auth';

export const authApi = {
  async checkAuth(): Promise<AuthCheckResponse> {
    return apiClient.get<AuthCheckResponse>('/auth/check');
  },

  async getLoginUrl(): Promise<LoginResponse> {
    return apiClient.get<LoginResponse>('/auth/login');
  },

  async logout(): Promise<LogoutResponse> {
    return apiClient.post<LogoutResponse>('/auth/logout');
  },
};
