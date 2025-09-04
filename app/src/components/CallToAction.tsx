import { Button } from '@/components/ui/button';
import { ArrowRight, Zap, Shield, Rocket } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface CTAProps {
  onStartGuestSession: () => void;
}

const CTA = ({ onStartGuestSession }: CTAProps) => {
  const navigate = useNavigate();
  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement> | React.MouseEvent<HTMLButtonElement>, href: string) => {
    e.preventDefault();
    if (href.startsWith('/')) {
      // For internal routes, use window.location.href
      window.location.href = href;
    } else if (href.startsWith('#')) {
      // For anchor links, scroll to the element
      const targetElement = document.querySelector(href);
      if (targetElement) {
        const offset = -85; // Account for fixed navbar
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.scrollY + offset;

        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth",
        });
      }
    } else {
      window.location.href = href;
    }
  };

  const handleTryForFree = () => {
    onStartGuestSession();
    navigate('/chat');
  };

  return (
    <section id="cta" className="w-full py-20 bg-gradient-to-b from-primary/10 to-background">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          {/* Header */}
          <div className="mb-12">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-6">
              Ready to Transform Your
              <span className="bg-gradient-to-r from-purple-400 to-violet-400 bg-clip-text text-transparent">
                {" "}Claim Normalization{" "}
              </span>
              Workflow?
            </h2>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
              Join engineering teams using CheckThat AI to build more reliable, 
              accurate, and efficient claim normalization pipelines.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-card/30 border rounded-xl p-6 backdrop-blur-sm">
              <Zap className="w-8 h-8 text-yellow-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-card-foreground mb-2">Lightning Fast</h3>
              <p className="text-muted-foreground text-sm">
                Get started in minutes with our intuitive platform
              </p>
            </div>
            <div className="bg-card/30 border rounded-xl p-6 backdrop-blur-sm">
              <Shield className="w-8 h-8 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-card-foreground mb-2">Enterprise Secure</h3>
              <p className="text-muted-foreground text-sm">
                Your data is protected with enterprise-grade security
              </p>
            </div>
            <div className="bg-card/30 border rounded-xl p-6 backdrop-blur-sm">
              <Rocket className="w-8 h-8 text-purple-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-card-foreground mb-2">Scale Effortlessly</h3>
              <p className="text-muted-foreground text-sm">
                From prototype to production, we scale with you
              </p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              size="lg"
              onClick={handleTryForFree}
              className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-8 py-4 rounded-full transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center gap-2"
            >
              Try for Free
              <ArrowRight className="w-4 h-4" />
            </Button>
            
            <Button 
              variant="outline"
              size="lg"
              className="font-semibold px-8 py-4 rounded-full transition-all duration-200 dark:text-slate-300 text-white"
              onClick={(e) => handleLinkClick(e, '#contact')}
            >
              Schedule Demo
            </Button>
          </div>

          {/* Trust Indicators */}
          {/* <div className="mt-12 pt-8 border-t">
            <p className="text-muted-foreground text-sm mb-4">Trusted by engineering teams at</p>
            <div className="flex justify-center items-center gap-8 opacity-60">
              <div className="text-muted-foreground font-semibold">CLEF 2025</div>
              <div className="text-muted-foreground font-semibold">CheckThat Lab</div>
              <div className="text-muted-foreground font-semibold">Task 2</div>
            </div>
          </div> */}
        </div>
      </div>
    </section>
  );
};

export default CTA;