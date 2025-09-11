import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { supabase } from '@/lib/supabase';
import { ThemeProvider } from '@/components/theme-provider';

// Landing Page Components
import { Layout } from './Layout';
import Hero from '@/components/Hero';
import CTA from '@/components/CallToAction';
import Features from '@/components/Features';
//import DocsPage from '@/pages/DocsPage';
//import BlogPage from '@/pages/BlogPage';
import ContactPage from '@/pages/ContactPage';
import NotFound from '@/pages/NotFound';
import AuthCallback from '@/pages/AuthCallback';

// Chat Interface Components
import ChatInterface from '@/components/ChatInterface';



interface UserInfo {
  id: string;
  email?: string;
  firstName: string;
  lastName: string;
  picture?: string;
  sessionId: string;
  isGuest?: boolean;
}

function App() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app load
    const checkSession = async () => {
      try {
        // First, try to restore from localStorage
        const storedUserInfo = localStorage.getItem('user_info');
        if (storedUserInfo) {
          try {
            const parsedUserInfo = JSON.parse(storedUserInfo);
            // Temporarily set user from localStorage
            setUser(parsedUserInfo);
          } catch (parseError) {
            console.error('Error parsing stored user info:', parseError);
            localStorage.removeItem('user_info');
          }
        }

        // Then check current Supabase session
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          const userInfo: UserInfo = {
            id: session.user.id,
            email: session.user.email,
            firstName: session.user.user_metadata?.given_name || session.user.user_metadata?.name?.split(' ')[0] || 'User',
            lastName: session.user.user_metadata?.family_name || session.user.user_metadata?.name?.split(' ').slice(1).join(' ') || '',
            picture: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture,
            sessionId: session.access_token
          };
          
          setUser(userInfo);
          localStorage.setItem('user_info', JSON.stringify(userInfo));
        } else if (!storedUserInfo) {
          // Only check for guest session if no stored user info and no Supabase session
          const guestSession = localStorage.getItem('guest_session');
          if (guestSession) {
            try {
              const guestUser = JSON.parse(guestSession);
              setUser(guestUser);
            } catch (parseError) {
              console.error('Error parsing guest session:', parseError);
              localStorage.removeItem('guest_session');
            }
          }
        }
      } catch (error) {
        console.error('Session check error:', error);
        // If there's an error with Supabase but we have stored user info, keep the user logged in
        const storedUserInfo = localStorage.getItem('user_info');
        if (storedUserInfo && !user) {
          try {
            const parsedUserInfo = JSON.parse(storedUserInfo);
            setUser(parsedUserInfo);
          } catch (parseError) {
            console.error('Error parsing stored user info after error:', parseError);
            localStorage.removeItem('user_info');
          }
        }
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state change:', event, session ? 'Session exists' : 'No session');
        
        if (event === 'SIGNED_IN' && session?.user) {
          const userInfo: UserInfo = {
            id: session.user.id,
            email: session.user.email,
            firstName: session.user.user_metadata?.given_name || session.user.user_metadata?.name?.split(' ')[0] || 'User',
            lastName: session.user.user_metadata?.family_name || session.user.user_metadata?.name?.split(' ').slice(1).join(' ') || '',
            picture: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture,
            sessionId: session.access_token
          };
          
          setUser(userInfo);
          localStorage.setItem('user_info', JSON.stringify(userInfo));
        } else if (event === 'SIGNED_OUT') {
          // Only clear user state if it was an authenticated user (not guest)
          const currentUser = localStorage.getItem('user_info');
          if (currentUser) {
            try {
              const parsedUser = JSON.parse(currentUser);
              if (!parsedUser.isGuest) {
                setUser(null);
                localStorage.removeItem('user_info');
              }
            } catch (error) {
              console.error('Error parsing user info during sign out:', error);
              setUser(null);
              localStorage.removeItem('user_info');
            }
          }
        } else if (event === 'TOKEN_REFRESHED' && session?.user) {
          // Update the session token when refreshed
          const currentUserInfo = localStorage.getItem('user_info');
          if (currentUserInfo) {
            try {
              const parsedUserInfo = JSON.parse(currentUserInfo);
              const updatedUserInfo = {
                ...parsedUserInfo,
                sessionId: session.access_token
              };
              setUser(updatedUserInfo);
              localStorage.setItem('user_info', JSON.stringify(updatedUserInfo));
            } catch (error) {
              console.error('Error updating session token:', error);
            }
          }
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [user]);

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      setUser(null);
      localStorage.removeItem('user_info');
      localStorage.removeItem('guest_session');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const createGuestSession = () => {
    const guestId = `guest_${Date.now()}`;
    const guestUser: UserInfo = {
      id: guestId,
      email: undefined,
      firstName: 'Guest',
      lastName: 'User',
      picture: undefined,
      sessionId: guestId,
      isGuest: true
    };
    
    setUser(guestUser);
    localStorage.setItem('guest_session', JSON.stringify(guestUser));
    return guestUser;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <Router>
        <Routes>
          {/* Public Routes - Landing Page */}
          <Route 
            path="/" 
            element={
              <Layout title="CheckThat AI - Fact Checking Made Easy">
                <Hero onStartGuestSession={createGuestSession} />
                <CTA onStartGuestSession={createGuestSession} />
                <Features />
                {/*<DocsPage />*/}
                <ContactPage />
              </Layout>
            } 
          />
          
          {/* Auth Callback Route */}
          <Route 
            path="/auth/callback" 
            element={
              <AuthCallback 
                onAuthSuccess={(userInfo) => {
                  setUser(userInfo);
                  localStorage.setItem('user_info', JSON.stringify(userInfo));
                }} 
              />
            } 
          />

          {/* Docs Page Route */}
          {/* <Route path="/" element={
            <Layout title="CheckThat AI">
              <Hero />
            </Layout>
          } /> */}

          {/* Blog Page Route */}
          {/* <Route path="/blog" element={
            <Layout title="Blog - CheckThat AI">
              <BlogPage />
            </Layout>
          } /> */}

          {/* Features Page Route */}
          <Route 
            path="/features" 
            element={
              <Layout title="Features - CheckThat AI">
                <Features />
              </Layout>
            } 
          />

          {/* Protected Route - Chat Interface */}
          <Route 
            path="/chat" 
            element={
              user ? (
                <ChatInterface user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          
          {/* Catch all - redirect to 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;