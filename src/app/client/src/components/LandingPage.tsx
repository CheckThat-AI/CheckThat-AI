import React from 'react';
import { Github, Star, MessageSquareDashed } from 'lucide-react';
import { useAppContext } from '@/contexts/AppContext';
import LoginButton from './login';

const LandingPage = () => {
  const { setMode } = useAppContext();

  const handleTryNow = () => {
    setMode('chat');
  };

  const handleRequestDemo = () => {
    setMode('extraction');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-black text-white">
      {/* Header */}
      <header className="bg-black/95 backdrop-blur-sm border-b border-gray-800/50 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <MessageSquareDashed className="h-8 w-8 text-blue-500" />
                <span className="text-xl font-bold text-white">CheckThat AI</span>
              </div>
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

              {/* Google Login Button */}
              <LoginButton />
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center px-6 py-20 lg:py-32">
        {/* Y Combinator Badge */}
        <div className="mb-8">
          <div className="flex items-center gap-2 bg-gray-800/50 border border-gray-700 rounded-full px-4 py-2 backdrop-blur-sm">
            <div className="w-6 h-6 bg-orange-500 rounded-sm flex items-center justify-center">
              <span className="text-white font-bold text-sm">Y</span>
            </div>
            <span className="text-gray-300 text-sm">Backed by</span>
            <span className="text-white font-semibold text-sm">Y Combinator</span>
          </div>
        </div>

        {/* Main Heading */}
        <div className="text-center max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold leading-tight mb-6">
            The LLM{' '}
            <span className="bg-gradient-to-r from-purple-400 via-violet-400 to-blue-400 bg-clip-text text-transparent">
              Evaluation
            </span>{' '}
            & Observability
            <br />
            Platform for{' '}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              CheckThat
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
            Built for the CLEF 2025 CheckThat Lab Task 2, our platform helps engineering teams 
            benchmark, safeguard, and improve claim normalization applications, with best-in-class 
            metrics and tracing.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button 
              onClick={handleRequestDemo}
              className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 text-white font-semibold px-8 py-4 rounded-full transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-purple-500/25"
            >
              Request a Demo
            </button>
            <button 
              onClick={handleTryNow}
              className="bg-white/10 hover:bg-white/20 text-white font-semibold px-8 py-4 rounded-full transition-all duration-200 border border-white/20 hover:border-white/30 backdrop-blur-sm"
            >
              Try Now For Free
            </button>
          </div>
        </div>

        {/* GitHub Stars Badge */}
        <div className="mt-16">
          <div className="flex items-center gap-2 bg-gray-800/30 border border-gray-700 rounded-full px-4 py-2 backdrop-blur-sm">
            <Github className="w-4 h-4 text-gray-300" />
            <Star className="w-4 h-4 text-yellow-400 fill-current" />
            <span className="text-white font-semibold">7.0k+</span>
            <span className="text-gray-400">CheckThat</span>
          </div>
        </div>
      </div>

      {/* Browser mockup with dots */}
      <div className="flex justify-center px-6 pb-20">
        <div className="w-full max-w-5xl">
          <div className="bg-gray-800/50 border border-gray-700 rounded-t-xl p-4 backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>
          <div className="bg-gradient-to-b from-gray-900 to-black border-x border-b border-gray-700 rounded-b-xl h-96 flex items-center justify-center">
            <div className="text-gray-400 text-lg">
              Platform Preview Coming Soon
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 