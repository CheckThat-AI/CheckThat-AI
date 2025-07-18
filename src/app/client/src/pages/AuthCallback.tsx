import React, { useEffect, useState } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import { supabase } from '@/lib/supabase';

const AuthCallback: React.FC = () => {
  const { setUser, setMode } = useAppContext();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Get the session from the URL hash
        const { data, error } = await supabase.auth.getSession();

        if (error) {
          console.error('Auth callback error:', error);
          setError(error.message);
          return;
        }

        if (data.session) {
          const user = data.session.user;
          
          // Extract user info from Supabase user
          const userInfo = {
            firstName: user.user_metadata?.given_name || user.user_metadata?.name?.split(' ')[0] || '',
            lastName: user.user_metadata?.family_name || user.user_metadata?.name?.split(' ')[1] || '',
            email: user.email || '',
            picture: user.user_metadata?.avatar_url || user.user_metadata?.picture || '',
            sessionId: data.session.access_token // Use access token as session ID
          };

          // Store user information in context
          setUser(userInfo);
          
          // Store user info in localStorage for persistence
          localStorage.setItem('supabase_user', JSON.stringify(userInfo));
          
          console.log('User logged in successfully:', userInfo);
          
          // Redirect to chat interface
          setMode('chat');
        } else {
          setError('No session found');
        }
      } catch (err: any) {
        console.error('Error in auth callback:', err);
        setError(err.message || 'Authentication failed');
      } finally {
        setLoading(false);
      }
    };

    handleAuthCallback();
  }, [setUser, setMode]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-black to-gray-900">
        <div className="bg-gray-800 p-8 rounded-lg shadow-xl max-w-md w-full mx-4 text-center">
          <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Completing sign in...</h2>
          <p className="text-gray-300">Please wait while we finish setting up your account.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-black to-gray-900">
        <div className="bg-gray-800 p-8 rounded-lg shadow-xl max-w-md w-full mx-4 text-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Authentication Error</h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <button
            onClick={() => window.location.href = '/'}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // This shouldn't be reached, but just in case
  return null;
};

export default AuthCallback; 