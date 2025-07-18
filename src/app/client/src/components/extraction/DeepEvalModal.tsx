import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, Cloud, Database, BarChart3, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getApiUrl } from '@/config';
import { useAppContext } from '@/contexts/AppContext';

// Confident AI Logo Component
const ConfidentLogo: React.FC<{ className?: string }> = ({ className = "h-5 w-5" }) => (
  <svg viewBox="0 0 193 193" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <rect x="4.5" y="4.5" width="184" height="184" rx="92" fill="#10002A" stroke="#6E00FF" strokeWidth="9"/>
    <path d="M50.7031 74.4507V117.029C50.7031 117.521 51.1428 117.908 51.6613 117.877C62.339 117.23 73.7603 113.681 81.8248 106.679V98.2878H70.0753C68.6259 98.2878 67.3792 97.2328 67.3124 95.8624C67.2412 94.4005 68.4724 93.196 69.9996 93.196H81.825V84.803C73.8055 77.8378 62.3843 74.2482 51.6611 73.6033C51.1427 73.5722 50.7031 73.9592 50.7031 74.4507ZM111.175 84.8047V93.196H122.923C124.371 93.196 125.618 94.2484 125.687 95.6171C125.761 97.0791 124.529 98.2878 123 98.2878H111.175V106.681C119.194 113.646 130.616 117.236 141.339 117.88C141.857 117.912 142.296 117.525 142.296 117.033V74.4546C142.296 73.9629 141.857 73.5759 141.338 73.6072C130.633 74.2555 119.225 77.8113 111.175 84.8047ZM87.2048 85.9164V105.567H105.795V85.9164H87.2048Z" fill="white"/>
  </svg>
);

interface DeepEvalModalProps {
  isOpen: boolean;
  onClose: () => void;
  evaluationRequest: any;
  onEvaluationComplete: (result: any) => void;
}

type ModalStep = 'login' | 'dataset' | 'evaluation' | 'complete' | 'error';

interface StepStatus {
  step: ModalStep;
  title: string;
  description: string;
  progress: number;
  icon: React.ReactNode;
  isActive: boolean;
  isComplete: boolean;
  error?: string;
}

export default function DeepEvalModal({ 
  isOpen, 
  onClose, 
  evaluationRequest, 
  onEvaluationComplete 
}: DeepEvalModalProps) {
  const { toast } = useToast();
  const { sendWebSocketMessage } = useAppContext();
  const [currentStep, setCurrentStep] = useState<ModalStep>('login');
  const [progress, setProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResult, setEvaluationResult] = useState<any>(null);
  const [showLoginSuccess, setShowLoginSuccess] = useState(false);
  const [timeoutRef, setTimeoutRef] = useState<NodeJS.Timeout | null>(null);

  // Listen for WebSocket messages from AppContext
  useEffect(() => {
    const handleWebSocketMessage = (event: CustomEvent) => {
      try {
        const message = event.detail;
        
        if (message.type === 'deepeval_progress') {
          handleProgressUpdate(message);
        } else if (message.type === 'deepeval_complete') {
          handleEvaluationComplete(message);
        } else if (message.type === 'deepeval_error') {
          handleEvaluationError(message);
        }
      } catch (err) {
        console.error('Error handling WebSocket message:', err);
      }
    };

    // Add event listener if modal is open and processing
    if (isOpen && isProcessing) {
      window.addEventListener('websocket-message', handleWebSocketMessage as EventListener);
    }

    return () => {
      window.removeEventListener('websocket-message', handleWebSocketMessage as EventListener);
    };
  }, [isOpen, isProcessing]);

  // Add timeout mechanism to prevent indefinite spinning
  useEffect(() => {
    if (isProcessing && !timeoutRef) {
      // Set a 5-minute timeout for the entire evaluation process
      const timeout = setTimeout(() => {
        if (isProcessing) {
          console.warn('DeepEval evaluation timed out after 5 minutes');
          setError('Evaluation timed out. The process may have completed successfully - check logs for details.');
          setCurrentStep('error');
          setIsProcessing(false);
          
          toast({
            title: "Evaluation Timeout",
            description: "The evaluation process timed out. Check the server logs or try running 'deepeval view' to see results.",
            variant: "destructive",
          });
        }
      }, 5 * 60 * 1000); // 5 minutes
      
      setTimeoutRef(timeout);
    }
    
    // Clear timeout when processing completes
    if (!isProcessing && timeoutRef) {
      clearTimeout(timeoutRef);
      setTimeoutRef(null);
    }
    
    return () => {
      if (timeoutRef) {
        clearTimeout(timeoutRef);
        setTimeoutRef(null);
      }
    };
  }, [isProcessing, timeoutRef]);

  const handleProgressUpdate = (message: any) => {
    const { stage, progress: msgProgress, message: statusMessage } = message;
    
    // Map server stages to modal steps
    let modalStep: ModalStep;
    switch (stage) {
      case 'authentication':
        modalStep = 'login';
        if (msgProgress === 100 && evaluationRequest?.confident_api_key) {
          setShowLoginSuccess(true);
        }
        break;
      case 'dataset':
        modalStep = 'dataset';
        break;
      case 'evaluation':
        modalStep = 'evaluation';
        break;
      default:
        modalStep = currentStep;
    }
    
    setCurrentStep(modalStep);
    setProgress(msgProgress);
    
    // Update step descriptions based on server message
    if (statusMessage) {
      // You could store custom messages in state if needed
      console.log(`DeepEval Progress: ${statusMessage}`);
    }
  };

  const handleEvaluationComplete = (message: any) => {
    try {
      console.log('DeepEval completion message received:', message);
      const { data } = message;
      
      setCurrentStep('complete');
      setProgress(100);
      setEvaluationResult(data);
      setIsProcessing(false);
      
      // Clear timeout since evaluation completed successfully
      if (timeoutRef) {
        clearTimeout(timeoutRef);
        setTimeoutRef(null);
      }
      
      console.log('About to call onEvaluationComplete with data:', data);
      // Notify parent component
      onEvaluationComplete(data);
    
    // Determine appropriate success message based on data completeness
    let successTitle = "DeepEval Evaluation Complete";
    let successDescription = `Successfully evaluated ${data.test_case_count || 0} test cases`;
    
    // Check if there were any serialization issues
    if (data.evaluation_results?.serialization_warning) {
      successDescription += ". Full results available via 'deepeval view' command.";
    } else if (data.evaluation_results?.note?.includes("WebSocket communication issue")) {
      successDescription += ". Results completed successfully despite communication issues.";
    } else if (data.test_case_count > 0) {
      successDescription += ". All results captured successfully.";
    }
    
    // Show success toast
    toast({
      title: successTitle,
      description: successDescription,
      variant: "default",
    });
    
    console.log('DeepEval completion handling finished successfully');
    } catch (error) {
      console.error('Error in handleEvaluationComplete:', error);
      // Still mark as complete to prevent stuck state
      setCurrentStep('complete');
      setProgress(100);
      setIsProcessing(false);
      
      toast({
        title: "Evaluation Complete",
        description: "Evaluation finished successfully but there was an issue displaying results.",
        variant: "default",
      });
    }
  };

  const handleEvaluationError = (message: any) => {
    const { message: errorMessage, error_details } = message;
    
    setCurrentStep('error');
    setProgress(0);
    setError(sanitizeErrorMessage(errorMessage || error_details || 'Unknown error occurred'));
    setIsProcessing(false);
    
    // Clear timeout since we received an error response
    if (timeoutRef) {
      clearTimeout(timeoutRef);
      setTimeoutRef(null);
    }
    
    toast({
      title: "Evaluation Failed", 
      description: sanitizeErrorMessage(errorMessage || error_details || 'Unknown error occurred'),
      variant: "destructive",
    });
  };

  // Define steps configuration
  const getStepStatus = (step: ModalStep): StepStatus => {
    const baseSteps: Record<ModalStep, StepStatus> = {
      login: {
        step: 'login' as ModalStep,
        title: 'DeepEval Authentication',
        description: evaluationRequest?.confident_api_key 
          ? (showLoginSuccess ? 'Confident AI cloud connection verified!' : 'Verifying Confident AI cloud connection...')
          : 'Preparing local evaluation environment...',
        progress: currentStep === 'login' ? progress : (currentStep === 'dataset' || currentStep === 'evaluation' || currentStep === 'complete' ? 100 : 0),
        icon: evaluationRequest?.confident_api_key 
          ? (showLoginSuccess ? <ConfidentLogo className="h-5 w-5" /> : <Cloud className="h-5 w-5" />)
          : <BarChart3 className="h-5 w-5" />,
        isActive: currentStep === 'login',
        isComplete: currentStep !== 'login' && currentStep !== 'error'
      },
      dataset: {
        step: 'dataset' as ModalStep,
        title: 'Dataset Creation',
        description: 'Creating evaluation dataset from extraction results...',
        progress: currentStep === 'dataset' ? progress : (currentStep === 'evaluation' || currentStep === 'complete' ? 100 : 0),
        icon: <Database className="h-5 w-5" />,
        isActive: currentStep === 'dataset',
        isComplete: currentStep === 'evaluation' || currentStep === 'complete'
      },
      evaluation: {
        step: 'evaluation' as ModalStep,
        title: 'Running Evaluation',
        description: 'Performing metric evaluation with selected model...',
        progress: currentStep === 'evaluation' ? progress : (currentStep === 'complete' ? 100 : 0),
        icon: <BarChart3 className="h-5 w-5" />,
        isActive: currentStep === 'evaluation',
        isComplete: currentStep === 'complete'
      },
      complete: {
        step: 'complete' as ModalStep,
        title: 'Complete',
        description: 'Evaluation completed successfully',
        progress: 100,
        icon: <CheckCircle className="h-5 w-5" />,
        isActive: false,
        isComplete: true
      },
      error: {
        step: 'error' as ModalStep,
        title: 'Error',
        description: 'An error occurred during evaluation',
        progress: 0,
        icon: <XCircle className="h-5 w-5" />,
        isActive: false,
        isComplete: false,
        error: error || undefined
      }
    };

    return baseSteps[step];
  };

  // Dynamic steps based on whether cloud integration is enabled
  const steps: ModalStep[] = evaluationRequest?.confident_api_key 
    ? ['login', 'dataset', 'evaluation']  // Cloud: Authentication + Dataset + Evaluation
    : ['dataset', 'evaluation'];          // Local: Dataset + Evaluation only

  // Start evaluation process when modal opens
  useEffect(() => {
    if (isOpen && evaluationRequest && !isProcessing) {
      startEvaluation();
    }
  }, [isOpen, evaluationRequest]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setCurrentStep('login');
      setProgress(0);
      setIsProcessing(false);
      setError(null);
      setEvaluationResult(null);
      setShowLoginSuccess(false);
      
      // Clear any active timeout
      if (timeoutRef) {
        clearTimeout(timeoutRef);
        setTimeoutRef(null);
      }
    }
  }, [isOpen]);

  const startEvaluation = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      // For cloud evaluation, start with authentication step
      if (evaluationRequest?.confident_api_key) {
        setCurrentStep('login');
        setProgress(0);
        setShowLoginSuccess(false);
      } else {
        // For local evaluation, start with dataset step
        setCurrentStep('dataset');
        setProgress(0);
      }

      // Use async DeepEval endpoint for real-time progress
      const response = await fetch(`${getApiUrl()}/eval/deepeval/async`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(evaluationRequest),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || errorData?.message || 'Failed to start DeepEval evaluation');
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message || 'Failed to start DeepEval evaluation');
      }

      // Notify WebSocket about DeepEval start to keep connection alive
      if (sendWebSocketMessage) {
        sendWebSocketMessage({
          type: "start_deepeval",
          data: { 
            evaluation_id: result.evaluation_id,
            session_id: result.session_id
          }
        });
      }

      // Evaluation started successfully, progress will come via WebSocket
      toast({
        title: "DeepEval Started",
        description: "Evaluation started successfully, progress will be shown in real-time",
        variant: "default",
      });

    } catch (error) {
      console.error('DeepEval evaluation error:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      const sanitizedError = sanitizeErrorMessage(errorMessage);
      
      // Check if this is an authentication error
      const isAuthError = errorMessage.toLowerCase().includes('auth') || 
                         errorMessage.toLowerCase().includes('login') || 
                         errorMessage.toLowerCase().includes('api key') ||
                         errorMessage.toLowerCase().includes('failed to authenticate') ||
                         errorMessage.toLowerCase().includes('api key not found');
      
      // If it's an auth error and we're using cloud, show error at login step
      if (isAuthError && evaluationRequest?.confident_api_key) {
        setCurrentStep('login');
        setShowLoginSuccess(false);
        setProgress(0);
      } else {
        setCurrentStep('error');
      }
      
      setError(sanitizedError);
      
      toast({
        title: isAuthError ? "Authentication Failed" : "Evaluation Failed",
        description: sanitizedError,
        variant: "destructive",
      });
      
      setIsProcessing(false);
    }
  };

  const sanitizeErrorMessage = (message: string): string => {
    // Remove session IDs and other sensitive information
    const cleaned = message
      .replace(/session[_\s]+[a-zA-Z0-9]+/gi, 'session')
      .replace(/[a-zA-Z0-9]{10,}/g, '[ID]') // Replace long alphanumeric strings
      .replace(/Session\s+[a-zA-Z0-9]+\s+not\s+found/gi, 'Session expired')
      .replace(/for\s+session:\s+[a-zA-Z0-9]+/gi, 'for session')
      .trim();
    
    // Add helpful context for session-related errors
    if (cleaned.toLowerCase().includes('session expired') || 
        cleaned.toLowerCase().includes('session not found')) {
      return 'Session expired, but evaluation can still proceed using saved extraction results. Please retry.';
    }
    
    // Handle authentication errors with helpful messages
    if (cleaned.toLowerCase().includes('failed to authenticate') ||
        cleaned.toLowerCase().includes('authentication failed') ||
        cleaned.toLowerCase().includes('api key not found')) {
      return 'Confident AI authentication failed. Please verify your API key is correct and try again.';
    }
    
    return cleaned;
  };

  const handleClose = () => {
    // Allow closing/cancelling at any time
    if (isProcessing) {
      // Show a toast when cancelling during processing
      toast({
        title: "Evaluation Cancelled",
        description: "DeepEval evaluation has been cancelled by user",
        variant: "default",
      });
    }
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="bg-cardbg-900 border-slate-800 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2 text-white">
            <BarChart3 className="h-5 w-5 text-yellow-500" />
            <span>
              {evaluationRequest?.confident_api_key 
                ? 'DeepEval Cloud Evaluation' 
                : 'DeepEval Local Evaluation'
              }
            </span>
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            {evaluationRequest?.confident_api_key 
              ? 'Running evaluation on Confident AI cloud with real-time progress updates'
              : 'Running local evaluation with real-time progress updates'
            }
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Steps Progress */}
          <div className="space-y-4">
            {steps.map((step, index) => {
              const stepStatus = getStepStatus(step);
              
              return (
                <div key={step} className="space-y-2">
                  {/* Step Header */}
                  <div className="flex items-center space-x-3">
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                      stepStatus.isComplete 
                        ? 'bg-emerald-600 border-emerald-600' 
                        : stepStatus.isActive 
                          ? 'border-yellow-500 bg-yellow-500/10' 
                          : 'border-slate-600 bg-slate-800'
                    }`}>
                      {stepStatus.isComplete ? (
                        // Special case: Show ConfidentLogo for successful cloud authentication
                        step === 'login' && evaluationRequest?.confident_api_key && showLoginSuccess ? (
                          <ConfidentLogo className="h-4 w-4" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-white" />
                        )
                      ) : stepStatus.isActive ? (
                        currentStep === 'error' ? (
                          <XCircle className="h-4 w-4 text-red-500" />
                        ) : (
                          <Loader2 className="h-4 w-4 text-yellow-500 animate-spin" />
                        )
                      ) : (
                        stepStatus.icon
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <h4 className={`font-medium ${
                        stepStatus.isActive ? 'text-white' : 'text-slate-400'
                      }`}>
                        {stepStatus.title}
                      </h4>
                      <p className="text-sm text-slate-500">
                        {stepStatus.description}
                      </p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {(stepStatus.isActive || stepStatus.isComplete) && (
                    <div className="ml-11 space-y-1">
                      <Progress 
                        value={stepStatus.progress} 
                        className="h-2 bg-slate-700"
                      />
                      <div className="flex justify-between text-xs text-slate-400">
                        <span>{Math.round(stepStatus.progress)}%</span>
                        {stepStatus.isComplete && (
                          <span className="text-emerald-500">Complete</span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Step Separator */}
                  {index < steps.length - 1 && (
                    <div className="ml-4 w-px h-4 bg-slate-700"></div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Error Display */}
          {currentStep === 'error' && error && (
            <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
              <div className="flex items-center space-x-2 text-red-400 mb-2">
                <XCircle className="h-4 w-4" />
                <span className="font-medium">Evaluation Failed</span>
              </div>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {/* Success Display */}
          {currentStep === 'complete' && evaluationResult && (
            <div className="bg-emerald-900/20 border border-emerald-800 rounded-lg p-4">
              <div className="flex items-center space-x-2 text-emerald-400 mb-2">
                <CheckCircle className="h-4 w-4" />
                <span className="font-medium">Evaluation Complete</span>
              </div>
              <div className="text-sm text-emerald-300 space-y-1">
                <p>• Test cases evaluated: {evaluationResult.test_case_count}</p>
                <p>• Dataset saved: {evaluationResult.dataset_saved ? 'Yes' : 'No'}</p>
                <p>• Execution time: {evaluationResult.execution_time?.toFixed(1)}s</p>
                {evaluationResult.dataset_location && (
                  <p>• Location: {evaluationResult.dataset_location}</p>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-700">
            {currentStep === 'error' && (
              <Button
                onClick={startEvaluation}
                disabled={isProcessing}
                className="bg-zinc-900 border border-slate-800 shadow-xl hover:bg-green-600 hover:border-slate-300 text-white"
              >
                Retry
              </Button>
            )}
            
            <Button
              onClick={handleClose}
              variant="outline"
              className="border border-slate-800 shadow-xl bg-zinc-900 text-white  hover:bg-red-700  hover:border-slate-300 hover:text-white"
            >
              {currentStep === 'complete' || currentStep === 'error' ? 'Close' : 'Cancel'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 