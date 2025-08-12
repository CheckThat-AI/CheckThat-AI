import { supabase } from './supabase';

export class ApiService {
  private baseUrl = 'http://localhost:8000';

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('No valid session found. Please log in again.');
    }

    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json',
    };
  }

  async makeAuthenticatedRequest(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<Response> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (response.status === 401) {
      // Token might be expired, try to refresh
      const { error } = await supabase.auth.refreshSession();
      if (error) {
        throw new Error('Session expired. Please log in again.');
      }
      
      // Retry with new token
      const newHeaders = await this.getAuthHeaders();
      return fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...newHeaders,
          ...options.headers,
        },
      });
    }

    return response;
  }

  // Google Drive specific methods
  async syncGoogleTokens(userData: {
    supabaseUserId: string;
    email: string;
    firstName?: string;
    lastName?: string;
    picture?: string;
    googleProviderToken?: string;
    googleProviderRefreshToken?: string;
  }) {
    return this.makeAuthenticatedRequest('/auth/sync-user', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async transferFileFromDrive(fileId: string, fileName: string) {
    return this.makeAuthenticatedRequest('/drive/transfer-file-to-supabase', {
      method: 'POST',
      body: JSON.stringify({
        google_drive_file_id: fileId,
        file_name: fileName,
      }),
    });
  }

  async chatWithAuth(userQuery: string, model: string, conversationId?: string, conversationHistory?: Array<{role: string, content: string, timestamp?: string}>) {
    const requestBody: {
      user_query: string;
      model: string;
      conversation_id?: string;
      conversation_history?: Array<{role: string, content: string, timestamp: string}>;
    } = {
      user_query: userQuery,
      model: model,
    };

    // Add conversation context if available
    if (conversationId) {
      requestBody.conversation_id = conversationId;
    }
    
    // Include conversation history as fallback (if no conversationId)
    if (!conversationId && conversationHistory && conversationHistory.length > 0) {
      // Convert frontend message format to backend format
      requestBody.conversation_history = conversationHistory
        .filter(msg => msg.role !== 'system' && msg.role !== 'welcome') // Exclude system/welcome messages
        .map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp || new Date().toISOString()
        }));
    }

    return this.makeAuthenticatedRequest('/chat', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }
}

export const apiService = new ApiService();
