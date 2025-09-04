import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ExternalLink, Github, Mail, FileText, Book, MessageCircle } from 'lucide-react';
import type { HyperLink } from '@/lib/utils';

const GitHubLink: HyperLink = {
  link: { url: 'https://github.com/nikhil-kadapala/clef2025-checkthat-lab-task2',
          target: '_blank', 
        },
  description: 'URL to GitHub Repository for source code and contributions',
};

const DocsPageLink: HyperLink = {
  link: { url: '/docs', target: '_blank' },
  description: 'Link to the API documentation page of the CheckThat AI platform',
};

const DocsPage = () => {
  return (
    <section id="docs" className="w-full py-20 bg-gradient-to-b from-background to-muted">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-6">
            Documentation &
            <span className="bg-gradient-to-r from-purple-400 to-violet-400 bg-clip-text text-transparent">
              {" "}Support{" "}
            </span>
          </h2>
          <p className="text-lg sm:text-xl text-muted-foreground">
            Everything you need to get started with CheckThat AI platform
          </p>
        </div>

        {/* Documentation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          <Card className="bg-card/50 border hover:bg-card/70 transition-all duration-300 hover:scale-105">
            <CardHeader className="pb-4">
              <div className="flex items-center mb-3">
                <Book className="w-8 h-8 text-blue-400 mr-3" />
                <CardTitle className="text-xl font-semibold text-card-foreground">
                  API Documentation
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Comprehensive API reference with examples and integration guides
              </p>
              <Button 
                variant="outline" 
                className="w-full text-slate-300"
                onClick={() => window.open(DocsPageLink.link.url, DocsPageLink.link.target)}
              >
                View Docs
                <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border hover:bg-card/70 transition-all duration-300 hover:scale-105">
            <CardHeader className="pb-4">
              <div className="flex items-center mb-3">
                <Github className="w-8 h-8 text-foreground mr-3" />
                <CardTitle className="text-xl font-semibold text-card-foreground">
                  GitHub Repository
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Access source code, contribute, and report issues
              </p>
              <Button 
                variant="outline" 
                className="w-full text-slate-300"
                onClick={() => window.open(GitHubLink.link.url, GitHubLink.link.target)}
              >
                View Repository
                <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border hover:bg-card/70 transition-all duration-300 hover:scale-105">
            <CardHeader className="pb-4">
              <div className="flex items-center mb-3">
                <FileText className="w-8 h-8 text-yellow-400 mr-3" />
                <CardTitle className="text-xl font-semibold text-card-foreground">
                  CLEF 2025 Task 2
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Official task documentation and evaluation guidelines
              </p>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => window.open('https://clef2025.clef-initiative.eu/', '_blank')}
              >
                View Task Details
                <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Contact Information */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-card/30 border rounded-xl p-8 text-center">
            <h3 className="text-2xl font-bold text-foreground mb-4">
              Need Help?
            </h3>
            <p className="text-muted-foreground mb-6">
              Our team is here to help you succeed with your claim normalization projects.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                className="bg-primary hover:bg-primary/90 text-primary-foreground flex items-center gap-2"
                onClick={() => window.open('mailto:support@checkthat.ai', '_blank')}
              >
                <Mail className="w-4 h-4" />
                Email Support
              </Button>
              
              <Button 
                variant="outline"
                className="flex items-center gap-2"
                onClick={() => window.open('#', '_blank')}
              >
                <MessageCircle className="w-4 h-4" />
                Join Community
              </Button>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <h4 className="text-foreground font-semibold mb-2">Platform</h4>
            <div className="space-y-1">
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Dashboard</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Analytics</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Models</p>
            </div>
          </div>
          <div>
            <h4 className="text-foreground font-semibold mb-2">Resources</h4>
            <div className="space-y-1">
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Tutorials</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Examples</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Best Practices</p>
            </div>
          </div>
          <div>
            <h4 className="text-foreground font-semibold mb-2">Support</h4>
            <div className="space-y-1">
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">FAQ</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Help Center</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Status</p>
            </div>
          </div>
          <div>
            <h4 className="text-foreground font-semibold mb-2">Company</h4>
            <div className="space-y-1">
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">About</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Privacy</p>
              <p className="text-muted-foreground text-sm hover:text-foreground cursor-pointer">Terms</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DocsPage;