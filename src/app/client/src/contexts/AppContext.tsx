import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { supabase } from '@/lib/supabase';
import type { User as SupabaseUser } from '@supabase/supabase-js';

export type AppMode = 'landing' | 'chat' | 'extraction';

export interface User {
  firstName: string;
  lastName: string;
  email: string;
  picture: string;
  sessionId: string;
}

interface AppContextType {
  mode: AppMode;
  setMode: (mode: AppMode) => void;
  user: User | null;
  setUser: (user: User | null) => void;
  loading: boolean;
  signOut: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<AppMode>('landing');
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    checkSession();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session);
        
        if (event === 'SIGNED_IN' && session) {
          const supabaseUser = session.user;
          const userInfo = extractUserInfo(supabaseUser);
          setUser(userInfo);
          localStorage.setItem('supabase_user', JSON.stringify(userInfo));
          setMode('chat'); // Redirect to chat after login
        } else if (event === 'SIGNED_OUT') {
          setUser(null);
          localStorage.removeItem('supabase_user');
          setMode('landing'); // Redirect to landing after logout
        }
        
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const checkSession = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session) {
        const userInfo = extractUserInfo(session.user);
        setUser(userInfo);
        setMode('chat');
      } else {
        // Check localStorage for persisted user info (fallback)
        const savedUser = localStorage.getItem('supabase_user');
        if (savedUser) {
          try {
            const parsedUser = JSON.parse(savedUser);
            setUser(parsedUser);
            setMode('chat');
          } catch (e) {
            console.error('Error parsing saved user:', e);
            localStorage.removeItem('supabase_user');
          }
        }
      }
    } catch (error) {
      console.error('Error checking session:', error);
    } finally {
      setLoading(false);
    }
  };

  const extractUserInfo = (supabaseUser: SupabaseUser): User => {
    return {
      firstName: supabaseUser.user_metadata?.given_name || supabaseUser.user_metadata?.name?.split(' ')[0] || '',
      lastName: supabaseUser.user_metadata?.family_name || supabaseUser.user_metadata?.name?.split(' ')[1] || '',
      email: supabaseUser.email || '',
      picture: supabaseUser.user_metadata?.avatar_url || supabaseUser.user_metadata?.picture || '',
      sessionId: supabaseUser.id // Use Supabase user ID as session ID
    };
  };

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
      setUser(null);
      localStorage.removeItem('supabase_user');
      setMode('landing');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const value: AppContextType = {
    mode,
    setMode,
    user,
    setUser,
    loading,
    signOut
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}
