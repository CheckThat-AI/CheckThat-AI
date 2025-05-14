import React from 'react';
import { useAppContext } from '@/contexts/AppContext';

export default function LoadingOverlay() {
  const { isLoading } = useAppContext();
  
  if (!isLoading) return null;
  
  return (
    <div className="fixed inset-0 bg-slate-900 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
        <p className="text-slate-800 font-medium">Processing...</p>
      </div>
    </div>
  );
}
