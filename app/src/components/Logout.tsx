import React, { useState, useRef, useEffect } from 'react';
import { LogOut, Settings } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import { useSidebar } from '@/components/ui/sidebar';
import { UserAvatar } from '@/components/ui/UserAvatar';

interface LogoutDropdownProps {
  user: {
    firstName?: string;
    lastName?: string;
    email?: string;
    picture?: string;
    sessionId?: string;
  };
}

export const LogoutDropdown: React.FC<LogoutDropdownProps> = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    try {
      // Sign out from Supabase
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        console.error('Error signing out:', error);
        alert('Error signing out. Please try again.');
        return;
      }
      
      // Clear user data from localStorage
      localStorage.removeItem('supabase_user');
      localStorage.removeItem('user_info');
      
      // Close dropdown
      setIsOpen(false);
      
      console.log('User logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      alert('Error signing out. Please try again.');
    }
  };

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Avatar Button */}
      <button
        onClick={toggleDropdown}
        className="w-full flex items-center space-x-3 p-2 rounded-lg hover:bg-zinc-700/50 transition-colors focus:outline-none"
      >
        <UserAvatar 
          user={user} 
          className="w-8 h-8 rounded-full"
          showGuestIcon={true}
        />
        {!isCollapsed && (
          <>
            <div className="flex-1 min-w-0 text-left">
              <div className="text-sm font-medium text-white truncate">
                {user.firstName || 'User'} {user.lastName || ''}
              </div>
              <div className="text-xs text-zinc-400 truncate">
                {user.email || 'No email'}
              </div>
            </div>
            <svg className="w-4 h-4 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
            </svg>
          </>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && user && (
        <div className="absolute bottom-full left-0 mb-2 w-56 bg-zinc-800/95 backdrop-blur-sm border border-zinc-700/50 rounded-xl shadow-xl z-50">
          {/* Menu Items */}
          <div className="p-2">
            <button
              onClick={() => {
                setIsOpen(false);
                // Add settings functionality here if needed
              }}
              className="w-full flex items-center px-3 py-2.5 text-sm font-medium text-zinc-200 hover:bg-zinc-700/50 rounded-lg transition-colors"
            >
              <Settings className="w-4 h-4 mr-3 text-zinc-400" />
              Settings
            </button>
            
            <hr className="my-2 border-zinc-700/50" />
            
            <button
              onClick={handleLogout}
              className="w-full flex items-center px-3 py-2.5 text-sm font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4 mr-3" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogoutDropdown; 