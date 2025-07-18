import React from 'react';
import { useAppContext } from '@/contexts/AppContext';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import LandingPage from '@/components/LandingPage';
import ChatInterface from '@/components/ChatInterface';
import ExtractionInterface from '@/components/ExtractionInterface';
import LoadingOverlay from '@/components/LoadingOverlay';
import AuthCallback from '@/pages/AuthCallback';

function AppLayout() {
  try {
    const { mode } = useAppContext();
    console.log('Current mode:', mode);
    
    const AppContent = () => {
      console.log('AppContent rendering with mode:', mode);
      
      // Handle auth callback route
      if (window.location.pathname === '/auth/callback') {
        return <AuthCallback />;
      }
      
      return (
        <div className="flex flex-col min-h-screen bg-gradient-to-b from-black to-black">
          {mode !== 'landing' && <Header />}
          <main className="flex-1 flex flex-col">
            {mode === 'landing' ? (
              <LandingPage/>
            ) : mode === 'chat' ? (
              <ChatInterface />
            ) : (
              <ExtractionInterface />
            )}
          </main>
          {mode !== 'landing' && <Footer />}
          <LoadingOverlay />
        </div>
      );
    };

    return <AppContent />;
  } catch (error) {
    console.error('Error in AppLayout:', error);
    return <div className="text-red-500 p-4">Error: {String(error)}</div>;
  }
}

export default AppLayout;
