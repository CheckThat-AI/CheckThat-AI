import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

interface HeroProps {
  onStartGuestSession: () => void;
}

const Hero = ({ onStartGuestSession }: HeroProps) => {
  const navigate = useNavigate();
  // const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement> | React.MouseEvent<HTMLButtonElement>, href: string) => {
  //   e.preventDefault();
  //   window.location.href = href;
  // };

  const handleTryForFree = () => {
    onStartGuestSession();
    navigate('/chat');
  };

  return (
    <div id="hero" className="w-full min-h-screen bg-gradient-to-b from-slate-900 to-background">
      {/* Hero Section */}
      <section className="w-full min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-6xl mx-auto text-center">
          {/* Y Combinator Badge */}
          {/* <div className="flex justify-center mb-8">
            <div className="flex items-center gap-2 bg-muted/50 border rounded-full px-4 py-2 backdrop-blur-sm hover:bg-muted/70 transition-colors">
              <div className="w-6 h-6 bg-orange-500 rounded-sm flex items-center justify-center">
                <span className="text-white font-bold text-sm">Y</span>
              </div>
              <span className="text-muted-foreground text-sm font-medium">Backed by</span>
              <span className="text-foreground font-semibold text-sm">Y Combinator</span>
            </div>
          </div> */}

          {/* Main Heading */}
          <div className="w-full">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold leading-tight mb-6 text-foreground">
              The LLM powered Claim {' '}
              <span className="bg-gradient-to-r from-purple-400 via-violet-400 to-blue-400 bg-clip-text text-transparent">
                Normalization
              </span>{' '}
              <br />
              Platform for{' '}
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                Fact-Checking
              </span>
            </h1>
            
            <div className="w-full max-w-4xl mx-auto">
              <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground mb-12 leading-relaxed">
                Built for the large scale fact-checking applications, our platform helps engineering teams 
                extract, normalize, and evaluate claims, with best-in-class LLM Evaluation metrics and tracing in real-time.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              {/* <button 
                onClick={(e) => handleLinkClick(e, '/chat')}
                className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-8 py-4 rounded-full transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                Request a Demo
              </button> */}
              <Button 
                size="lg"
                onClick={handleTryForFree}
                className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-8 py-4 rounded-full transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center gap-2"
              >
                Try for Free
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Hero; 