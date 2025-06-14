import React from 'react';
import { MessageSquareDashed } from 'lucide-react';
import { useAppContext } from '@/contexts/AppContext';
import { Switch } from '@/components/ui/switch';

export default function Header() {
  const { mode, toggleMode } = useAppContext();

  return (
    <header 
      className="bg-gradient-to-b from-black to-black
      shadow-xl border-b border-slate-800">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <MessageSquareDashed className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-semibold text-blue-800">Claim Normalization</h1>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-blue-600">
            {mode === 'chat' ? 'Chat Mode' : 'Batch Mode'}
          </span>
          <Switch
            checked={mode === 'evaluation'}
            onCheckedChange={toggleMode}
            title="Toggle between Chat and Batch modes"
          />
        </div>
      </div>
    </header>
  );
}
