import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  BarChart3, 
  Shield, 
  Zap, 
  Globe, 
  Database,
  MessageSquare,
  FileText,
  Settings,
  Clock
} from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: Brain,
      title: "Multi-Model AI Integration",
      description: "Support for OpenAI GPT-4, Claude, Gemini, and other SOTA LLMs with seamless model switching",
      badge: "AI Powered",
      color: "text-purple-400"
    },
    {
      icon: BarChart3,
      title: "Advanced Evaluation Metrics",
      description: "Comprehensive metrics including BLEU, ROUGE, BERTScore, faithfulness, and hallucination detection",
      badge: "Analytics",
      color: "text-blue-400"
    },
    {
      icon: MessageSquare,
      title: "Real-time Chat Interface",
      description: "Interactive chat with streaming responses, conversation history, and context-aware discussions",
      badge: "Interactive",
      color: "text-green-400"
    },
    {
      icon: FileText,
      title: "Document Processing",
      description: "Upload and process documents with intelligent claim extraction and normalization capabilities",
      badge: "Processing",
      color: "text-yellow-400"
    },
    {
      icon: Database,
      title: "Secure Data Management",
      description: "Google Drive integration with encrypted API key storage and user data protection",
      badge: "Security",
      color: "text-red-400"
    },
    {
      icon: Globe,
      title: "CLEF 2025 Compliant",
      description: "Built specifically for CheckThat Lab Task 2 with standardized evaluation protocols",
      badge: "Standards",
      color: "text-indigo-400"
    }
  ];

  const additionalFeatures = [
    {
      icon: Zap,
      title: "Lightning Fast Performance",
      description: "Optimized for speed with efficient processing and minimal latency"
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "SOC 2 compliant with end-to-end encryption and secure authentication"
    },
    {
      icon: Settings,
      title: "Customizable Workflows",
      description: "Flexible configuration options to match your specific use cases"
    },
    {
      icon: Clock,
      title: "24/7 Availability",
      description: "Reliable uptime with global infrastructure and redundancy"
    }
  ];

  return (
    <section id="features" className="w-full py-20 bg-gradient-to-b from-background to-muted">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-6">
            Powerful Features for
            <span className="bg-gradient-to-r from-purple-400 to-violet-400 bg-clip-text text-transparent">
              {" "}Modern AI{" "}
            </span>
            Development
          </h2>
          <p className="text-lg sm:text-xl text-muted-foreground">
            Everything you need to build, evaluate, and deploy claim normalization 
            applications with confidence
          </p>
        </div>

        {/* Main Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="bg-card/50 border hover:bg-card/70 transition-all duration-300 hover:scale-105">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between mb-3">
                  <feature.icon className={`w-8 h-8 ${feature.color}`} />
                  <Badge variant="secondary">
                    {feature.badge}
                  </Badge>
                </div>
                <CardTitle className="text-xl font-semibold text-card-foreground">
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional Features */}
        <div className="max-w-4xl mx-auto">
          <h3 className="text-2xl font-bold text-foreground text-center mb-8">
            Built for Scale & Security
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {additionalFeatures.map((feature, index) => (
              <div key={index} className="flex items-start space-x-4 p-6 bg-card/30 rounded-xl border">
                <feature.icon className="w-6 h-6 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h4 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h4>
                  <p className="text-muted-foreground text-sm">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Integration Showcase */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold text-foreground mb-8">
            Seamless Integrations
          </h3>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-70">
            <div className="bg-card/50 px-6 py-3 rounded-lg border">
              <span className="text-card-foreground font-medium">OpenAI GPT-4</span>
            </div>
            <div className="bg-card/50 px-6 py-3 rounded-lg border">
              <span className="text-card-foreground font-medium">Claude 3</span>
            </div>
            <div className="bg-card/50 px-6 py-3 rounded-lg border">
              <span className="text-card-foreground font-medium">Google Gemini</span>
            </div>
            <div className="bg-card/50 px-6 py-3 rounded-lg border">
              <span className="text-card-foreground font-medium">Supabase</span>
            </div>
            <div className="bg-card/50 px-6 py-3 rounded-lg border">
              <span className="text-card-foreground font-medium">Google Drive</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;