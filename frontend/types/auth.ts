export interface User {
  user_id: string;
  email: string;
  name: string | null;
  picture: string | null;
}

export interface AuthCheckResponse {
  authenticated: boolean;
  user: User;
}

export interface LoginResponse {
  message: string;
  auth_url: string;
}

export interface LogoutResponse {
  message: string;
}
