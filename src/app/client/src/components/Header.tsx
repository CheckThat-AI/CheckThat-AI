import React, { useState } from 'react';
import { MessageSquareDashed, Github, Star, User, LogOut, ChevronDown } from 'lucide-react';
import { useAppContext } from '@/contexts/AppContext';
import { Switch } from '@/components/ui/switch';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function Header() {
  const { mode, setMode, user, signOut } = useAppContext();

  const handleLogoClick = () => {
    setMode('landing');
  };

  const toggleMode = () => {
    setMode(mode === 'chat' ? 'extraction' : 'chat');
  };

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <header className="bg-black/95 backdrop-blur-sm border-b border-gray-800/50 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <button 
              onClick={handleLogoClick}
              className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
            >
              <MessageSquareDashed className="h-8 w-8 text-blue-500" />
              <span className="text-xl font-bold text-white">CheckThat AI</span>
            </button>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-gray-300 hover:text-white transition-colors font-medium">
              Products
            </a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors font-medium">
              Blog
            </a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors font-medium">
              Documentation
            </a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors font-medium">
              Pricing
            </a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors font-medium">
              Careers
            </a>
          </nav>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* GitHub Stars */}
            <div className="hidden sm:flex items-center gap-2 bg-gray-800/50 border border-gray-700 rounded-full px-3 py-1.5 backdrop-blur-sm">
              <Github className="w-4 h-4 text-gray-300" />
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="text-white font-medium text-sm">7.0k+</span>
              <span className="text-gray-400 text-sm">CheckThat</span>
            </div>

            {/* Mode Switch */}
            <div className="flex items-center space-x-2 bg-gray-800/30 rounded-full px-3 py-1.5 border border-gray-700">
              <span className="text-gray-300 text-sm font-medium">
                {mode === 'chat' ? 'Chat' : 'Batch'}
              </span>
              <Switch
                checked={mode === 'extraction'}
                onCheckedChange={toggleMode}
                title="Toggle between Chat and Batch modes"
                className="data-[state=checked]:bg-purple-600"
              />
            </div>

            {/* User Avatar with Dropdown or Home Button */}
            {user && user.picture ? (
              <DropdownMenu>
                <DropdownMenuTrigger className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
                  <img 
                    src={user.picture} 
                    alt={`${user.firstName} ${user.lastName}`}
                    className="w-8 h-8 rounded-full border-2 border-gray-600 hover:border-blue-500 transition-colors cursor-pointer"
                  />
                  <span className="hidden sm:block text-gray-300 text-sm">
                    {user.firstName}
                  </span>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56 bg-gray-900 border-gray-700">
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-white">
                      {user.firstName} {user.lastName}
                    </p>
                    <p className="text-xs text-gray-400 truncate">
                      {user.email}
                    </p>
                  </div>
                  <DropdownMenuSeparator className="bg-gray-700" />
                  <DropdownMenuItem 
                    onClick={handleSignOut}
                    className="text-red-400 hover:text-red-300 hover:bg-gray-800 cursor-pointer"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <button 
                onClick={handleLogoClick}
                className="bg-white text-black font-semibold px-6 py-2 rounded-full hover:bg-gray-100 transition-colors"
              >
                Home
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
