import React from 'react';
import { MessageSquareDashed } from 'lucide-react';
import { useAppContext } from '@/contexts/AppContext';
import { Switch } from '@/components/ui/switch';

export default function Header() {
  const { mode, toggleMode } = useAppContext();

  return (
    <header className="bg-gray-800 shadow-sm">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <MessageSquareDashed className="h-6 w-6 text-slate-200" />
          <h1 className="text-xl font-semibold text-slate-200">Claim Normalization</h1>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-slate-200">
            {mode === 'chat' ? 'Chat Mode' : 'Evaluation Mode'}
          </span>
          <Switch 
            checked={mode === 'evaluation'}
            onCheckedChange={toggleMode}
            title="Toggle between Chat and Evaluation modes"
          />
        </div>
      </div>
    </header>
  );
}
