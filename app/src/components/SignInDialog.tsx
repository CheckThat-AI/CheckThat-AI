import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Login } from './Login';
import { Crown, Zap, Shield } from 'lucide-react';

interface SignInDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  modelName: string;
  onSuccess: () => void;
}

export const SignInDialog: React.FC<SignInDialogProps> = ({
  open,
  onOpenChange,
  onSuccess
}) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Crown className="w-5 h-5 text-yellow-500" />
            Premium Model Access
          </DialogTitle>
          <DialogDescription>
            Sign in to securely add your API Keys and access the premium models
          </DialogDescription>
          <p className="text-sm text-muted-foreground mb-4 text-center">
            Click <a href="/docs/api_keys" target="_blank" rel="noopener noreferrer">here</a> to learn how to add your API keys.
          </p>
        </DialogHeader>
        
        <Card className="border-yellow-200 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-950/20 dark:to-orange-950/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-600" />
              Premium Features
            </CardTitle>
            <CardDescription>
              Get access to the most powerful AI models
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-green-600" />
              <span className="text-sm">Access to latest models from OpenAI, Anthropic, Google, and xAI</span>
            </div>
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-green-600" />
              <span className="text-sm">Use your personal API Keys with usage based pricing</span>
            </div>
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-green-600" />
              <span className="text-sm">Advanced conversation management</span>
            </div>
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-green-600" />
              <span className="text-sm">File upload and analysis</span>
            </div>
          </CardContent>
        </Card>

        <div className="mt-4">
          
          <div className="space-y-3">
            <Login onSuccess={onSuccess} />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};