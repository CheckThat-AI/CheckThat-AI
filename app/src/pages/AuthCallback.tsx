import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '@/lib/supabase';
import { syncGoogleTokensWithBackend } from '@/lib/googleAuthSync';
import { Loader2 } from 'lucide-react';

interface AuthCallbackProps {
  onAuthSuccess: (user: any) => void;
}

const AuthCallback: React.FC<AuthCallbackProps> = ({ onAuthSuccess }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        console.log('AuthCallback: Starting authentication process...');
        console.log('Current URL:', window.location.href);
        
        // Get the current session after OAuth redirect
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        console.log('Session data:', session);
        console.log('Session error:', sessionError);
        
        if (sessionError) {
          console.error('Session error:', sessionError);
          setError('Authentication failed. Please try again.');
          setLoading(false);
          return;
        }

        if (session?.user) {
          console.log('User authenticated successfully:', session.user);
          
          // Clear any existing guest session when user successfully authenticates
          localStorage.removeItem('guest_session');
          
          // Extract user information
          const userInfo = {
            id: session.user.id,
            email: session.user.email,
            firstName: session.user.user_metadata?.given_name || session.user.user_metadata?.name?.split(' ')[0] || 'User',
            lastName: session.user.user_metadata?.family_name || session.user.user_metadata?.name?.split(' ').slice(1).join(' ') || '',
            picture: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture,
            sessionId: session.access_token
          };

          console.log('Extracted user info:', userInfo);

          // Store user info in localStorage
          localStorage.setItem('supabase_user', JSON.stringify(session.user));
          localStorage.setItem('user_info', JSON.stringify(userInfo));

          // Sync Google tokens with backend (non-blocking)
          syncGoogleTokensWithBackend(userInfo).catch(error => {
            console.warn('Failed to sync Google tokens, but continuing with login:', error);
          });

          // Call the success callback
          onAuthSuccess(userInfo);
          
          // Redirect to chat interface
          navigate('/chat', { replace: true });
        } else {
          console.log('No session found after OAuth redirect');
          setError('No user session found. Please try logging in again.');
        }
      } catch (err) {
        console.error('Auth callback error:', err);
        setError('An unexpected error occurred during authentication.');
      } finally {
        setLoading(false);
      }
    };

    // Add a small delay to ensure URL parameters are processed
    const timer = setTimeout(handleAuthCallback, 100);
    return () => clearTimeout(timer);
  }, [onAuthSuccess, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">Authenticating...</h2>
          <p className="text-muted-foreground">Please wait while we set up your account.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="w-16 h-16 bg-destructive/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-destructive text-2xl">✕</span>
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">Authentication Error</h2>
          <p className="text-muted-foreground mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 py-2 rounded-lg transition-colors"
          >
            Return Home
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default AuthCallback; 