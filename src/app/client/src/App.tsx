import React from 'react';
import { Route } from 'wouter';
import { Toaster } from '@/components/ui/toaster';
import { QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { queryClient } from './lib/queryClient';
import { AppProvider, useAppContext } from '@/contexts/AppContext';
import ChatInterface from '@/components/ChatInterface';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import LoadingOverlay from '@/components/LoadingOverlay';
import NotFound from '@/pages/not-found';
import ExtractionInterface from '@/components/ExtractionInterface';
import './components/scrollbar-hide.css';

function AppLayout() {
  const { mode } = useAppContext();
  
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-black to-black">
      <Header />
      
      <main className="flex-1 flex flex-col">
        {mode === 'chat' ? <ChatInterface /> : <ExtractionInterface />}
      </main>
      
      <Footer />
      <LoadingOverlay />
    </div>
  );
}

function AppContainer() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AppProvider>
          <Toaster />
          <AppLayout />
        </AppProvider>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

function App() {
  return (
    <Route component={AppContainer} />
  );
}

export default App;
