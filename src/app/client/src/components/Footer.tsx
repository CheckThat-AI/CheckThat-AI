import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-gradient-to-b from-black to-black
     border-t border-slate-800 py-4">
      <div className="container mx-auto px-4 flex flex-col sm:flex-row justify-between items-center">
        <p className="text-sm text-slate-400">&copy; 2025 Nikhil Kadapala</p>
        <div className="flex space-x-4 mt-2 sm:mt-0">
          <a href="#help" className="text-sm text-slate-400 hover:text-slate-200">Help</a>
          <a href="#about" className="text-sm text-slate-400 hover:text-slate-200">About</a>
          <a href="#api" className="text-sm text-slate-400 hover:text-slate-200">API</a>
        </div>
      </div>
    </footer>
  );
}
