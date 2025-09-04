import { supabase } from './supabase';
import { apiService } from './apiService';

export interface UserInfo {
  id: string;
  email?: string;
  firstName: string;
  lastName: string;
  picture?: string;
  sessionId: string;
  isGuest?: boolean;
}

/**
 * Synchronizes Google OAuth provider tokens with the backend
 * This should be called after successful OAuth authentication
 */
export async function syncGoogleTokensWithBackend(userInfo: UserInfo): Promise<void> {
  try {
    console.log('Starting Google token sync...');
    
    // Get the current session to access provider tokens
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.error('Error getting session:', sessionError);
      throw new Error('Failed to get session for token sync');
    }

    if (!session?.user) {
      console.error('No user session found');
      throw new Error('No user session found for token sync');
    }

    // Extract Google provider tokens from the session
    const providerToken = session.provider_token; // Google access token
    const providerRefreshToken = session.provider_refresh_token; // Google refresh token

    if (!providerToken) {
      console.warn('No Google provider token found in session');
      // This might happen if the user didn't authenticate with Google OAuth
      // or if the tokens are not included in the session
      return;
    }

    console.log('Found Google provider tokens, syncing with backend...');

    // Prepare user data for backend sync
    const userData = {
      supabaseUserId: userInfo.id,
      email: userInfo.email || '',
      firstName: userInfo.firstName,
      lastName: userInfo.lastName,
      picture: userInfo.picture,
      googleProviderToken: providerToken,
      googleProviderRefreshToken: providerRefreshToken || undefined,
    };

    // Sync with backend
    const response = await apiService.syncGoogleTokens(userData);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend sync failed:', errorText);
      throw new Error(`Failed to sync tokens with backend: ${errorText}`);
    }

    const result = await response.json();
    console.log('Google tokens synced successfully:', result);

  } catch (error) {
    console.error('Error syncing Google tokens:', error);
    // Don't throw here - we don't want to block the login process
    // The user can still use the app, just won't have Drive integration until tokens are manually synced
  }
}

/**
 * Checks if the current user has Google Drive access
 */
export async function checkGoogleDriveAccess(): Promise<boolean> {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) {
      return false;
    }

    const response = await apiService.makeAuthenticatedRequest(`/auth/google-drive-access/${session.user.id}`, {
      method: 'GET',
    });

    return response.ok;
  } catch (error) {
    console.error('Error checking Google Drive access:', error);
    return false;
  }
}

/**
 * Request user to re-authenticate with Google if Drive access is needed
 */
export async function requestGoogleDriveAccess(): Promise<void> {
  console.log('Requesting Google Drive access...');
  
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      scopes: 'openid https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
      redirectTo: `${window.location.origin}/auth/callback`,
      queryParams: {
        access_type: 'offline',
        prompt: 'consent'
      }
    }
  });

  if (error) {
    console.error('Error requesting Google Drive access:', error);
    throw error;
  }

  console.log('Google Drive access request initiated:', data);
}
