/**
 * Utility functions for making authenticated API calls
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-railway-app.railway.app';

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

export interface DocumentsResponse {
  documents: any[];
  total: number;
  limit: number;
  offset: number;
}

export class AuthApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Authentication endpoints
  async login(username: string, password: string) {
    return this.makeRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async register(userData: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
    bio?: string;
  }) {
    return this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser() {
    return this.makeRequest('/auth/me');
  }

  async updateUser(userData: {
    full_name?: string;
    bio?: string;
    avatar_url?: string;
    preferred_language?: string;
    timezone?: string;
  }) {
    return this.makeRequest('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async changePassword(oldPassword: string, newPassword: string) {
    return this.makeRequest('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
      }),
    });
  }

  // Document endpoints
  async uploadDocument(file: File, forceUpload = false) {
    const formData = new FormData();
    formData.append('file', file);
    if (forceUpload) {
      formData.append('force_upload', 'true');
    }

    const url = `${API_BASE_URL}/api/v1/documents/upload`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async getDocuments(limit = 100, offset = 0): Promise<ApiResponse<DocumentsResponse>> {
    return this.makeRequest<DocumentsResponse>(`/api/v1/documents?limit=${limit}&offset=${offset}`);
  }

  async deleteDocument(documentId: string) {
    return this.makeRequest(`/api/v1/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  async getDocumentContent(documentId: string) {
    return this.makeRequest(`/api/v1/documents/${documentId}/content`);
  }

  async downloadDocument(documentId: string) {
    const url = `${API_BASE_URL}/api/v1/documents/${documentId}/download`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return {
        data: response,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Chat endpoints
  async sendMessage(message: string) {
    return this.makeRequest(`/api/v1/learning/chat?query=${encodeURIComponent(message)}`, {
      method: 'POST',
    });
  }

  // OpenAI endpoints
  async testOpenAI() {
    return this.makeRequest('/api/v1/learning/openai/test');
  }

  async configureOpenAI(model: string, maxTokens?: number, temperature?: number) {
    return this.makeRequest('/api/v1/learning/openai/configure', {
      method: 'POST',
      body: JSON.stringify({
        model,
        max_tokens: maxTokens,
        temperature,
      }),
    });
  }
}

// Create a singleton instance
export const authApi = new AuthApiClient();
