import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 py-4">
      <div className="container mx-auto px-4 flex flex-col sm:flex-row justify-between items-center">
        <p className="text-sm text-slate-500">&copy; 2025 Nikhil Kadapala</p>
        <div className="flex space-x-4 mt-2 sm:mt-0">
          <a href="#help" className="text-sm text-slate-500 hover:text-primary">Help</a>
          <a href="#about" className="text-sm text-slate-500 hover:text-primary">About</a>
          <a href="#api" className="text-sm text-slate-500 hover:text-primary">API</a>
        </div>
      </div>
    </footer>
  );
}
