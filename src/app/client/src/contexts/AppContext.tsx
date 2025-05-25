import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiRequest } from '@/lib/queryClient';
import { 
  Message, 
  EvaluationData, 
  NormalizationResponse, 
  EvaluationResponse, 
  ModelOption, 
  PromptStyleOption,
  ProgressResponse,
  EvaluationResults,
  MeteorScore
} from '@shared/types';
import { generateId } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

type AppMode = 'chat' | 'evaluation';

interface AppContextType {
  mode: AppMode;
  toggleMode: () => void;
  messages: Message[];
  isLoading: boolean;
  selectedFile: File | null;
  currentMessage: string;
  setCurrentMessage: (message: string) => void;
  sendMessage: () => Promise<void>;
  handleFileChange: (file: File | null) => void;
  clearMessages: () => void;
  selectedModel: ModelOption;
  setSelectedModel: (model: ModelOption) => void;
  apiKey: string;
  setApiKey: (key: string) => void;
  
  // Evaluation mode
  evaluationData: EvaluationData;
  updateEvaluationData: (data: Partial<EvaluationData>) => void;
  submitEvaluation: () => Promise<boolean>;
  resetEvaluation: () => void;
  evaluationSubmitted: boolean;
  
  // New evaluation features
  progress: number;
  progressStatus: 'pending' | 'processing' | 'completed' | 'error';
  startEvaluation: () => Promise<void>;
  checkProgress: () => Promise<number>;
  evaluationResults: EvaluationResults | null;
}

const defaultEvaluationData: EvaluationData = {
  file: null,
  selectedModels: [],
  selectedPromptStyles: []
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<AppMode>('chat');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateId(),
      content: "Hello! I'm your claim normalization assistant. You can provide your source text to analyze.",
      sender: 'system',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentMessage, setCurrentMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState<ModelOption>('meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre');
  const [apiKey, setApiKey] = useState('');
  const [evaluationData, setEvaluationData] = useState<EvaluationData>(defaultEvaluationData);
  const [evaluationSubmitted, setEvaluationSubmitted] = useState(false);
  
  // New state for progress tracking
  const [progress, setProgress] = useState<number>(0);
  const [progressStatus, setProgressStatus] = useState<'pending' | 'processing' | 'completed' | 'error'>('pending');
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResults | null>(null);
  
  const { toast } = useToast();

  const toggleMode = () => {
    setMode(prevMode => prevMode === 'chat' ? 'evaluation' : 'chat');
  };

  const sendMessage = async () => {
    console.log('sendMessage called');
    if (!currentMessage.trim() && !selectedFile) {
      console.log('No message or file to send');
      return;
    }
    
    console.log('Creating user message');
    // Add user message to chat
    const userMessage: Message = {
      id: generateId(),
      content: currentMessage,
      sender: 'user',
      timestamp: new Date(),
      files: selectedFile ? [selectedFile] : undefined
    };
    
    console.log('Adding user message to chat');
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);
    
    try {
      console.log('Preparing request data:', {
        user_query: currentMessage,
        model: selectedModel,
        api_key: apiKey ? '***' : undefined
      });

      const requestBody = {
        user_query: currentMessage,
        model: selectedModel,
        api_key: apiKey
      };

      console.log('Sending request to /api/chat');
      // Call API to normalize claim
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      console.log('Response received:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        console.error('Error response:', errorData);
        throw new Error(errorData?.detail || 'Failed to normalize claim');
      }
      
      const data: NormalizationResponse = await response.json();
      console.log('Response data:', data);
      
      // Add system response
      const systemMessage: Message = {
        id: generateId(),
        content: `**Normalized Claim:** ${data.normalizedClaim}`,
        sender: 'system',
        timestamp: new Date()
      };
      
      console.log('Adding system response to chat');
      setMessages(prev => [...prev, systemMessage]);
      
      // Clear file if any
      setSelectedFile(null);
    } catch (error) {
      console.error('Error in sendMessage:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to normalize your claim. Please try again.",
        variant: "destructive",
      });
    } finally {
      console.log('Setting isLoading to false');
      setIsLoading(false);
    }
  };

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    
    if (file) {
      toast({
        title: "File Ready",
        description: `"${file.name}" has been selected and is ready to upload.`,
      });
    }
  };

  const clearMessages = () => {
    setMessages([
      {
        id: generateId(),
        content: "Hello! I'm your claim normalization assistant. You can provide me your source text to analyze.",
        sender: 'system',
        timestamp: new Date()
      }
    ]);
    setSelectedFile(null);
  };

  const updateEvaluationData = (data: Partial<EvaluationData>) => {
    setEvaluationData(prev => ({ ...prev, ...data }));
  };

  const submitEvaluation = async (): Promise<boolean> => {
    if (!evaluationData.file || evaluationData.selectedModels.length === 0 || evaluationData.selectedPromptStyles.length === 0) {
      toast({
        title: "Missing Information",
        description: "Please select a file, at least one model, and one prompt style.",
        variant: "destructive",
      });
      return false;
    }
    
    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', evaluationData.file);
      formData.append('model', evaluationData.selectedModels[0]);
      formData.append('prompt_style', evaluationData.selectedPromptStyles[0]);
      
      const response = await fetch('/api/normalize-claims', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit evaluation');
      }
      
      const data = await response.json();
      
      setEvaluationSubmitted(true);
      toast({
        title: "Success",
        description: "Your evaluation has been submitted successfully.",
        variant: "success",
      });
      return true;
    } catch (error) {
      console.error('Error submitting evaluation:', error);
      toast({
        title: "Error",
        description: "Failed to submit your evaluation. Please try again.",
        variant: "destructive",
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const resetEvaluation = () => {
    setEvaluationData(defaultEvaluationData);
    setEvaluationSubmitted(false);
    setProgress(0);
    setProgressStatus('pending');
  };
  
  // New methods for model evaluation with progress tracking
  const startEvaluation = async (): Promise<void> => {
    if (evaluationData.selectedModels.length === 0 || evaluationData.selectedPromptStyles.length === 0) {
      toast({
        title: "Selection Required",
        description: "Please select at least one model and one prompt style.",
        variant: "destructive",
      });
      return;
    }
    
    setProgressStatus('processing');
    setProgress(0);
    setIsLoading(true);
    
    try {
      // Create form data for the API request
      const formData = new FormData();
      
      // Add the CSV file
      if (evaluationData.file) {
        formData.append('file', evaluationData.file);
      } else {
        throw new Error('No file selected');
      }
      
      // Add the request parameters
      const requestData = {
        model: evaluationData.selectedModels[0], // For now, we'll use the first selected model
        prompt_style: evaluationData.selectedPromptStyles[0], // For now, we'll use the first selected prompt style
        self_refine_iterations: 0 // Default value
      };
      
      // Call the FastAPI endpoint through the proxy
      const response = await fetch('/api/normalize-claims', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to start evaluation');
      }
      
      const data = await response.json();
      
      // Update the evaluation results
      setEvaluationResults({
        scores: [{
          model: data.model,
          promptStyle: data.prompt_style,
          score: data.meteor_score
        }],
        timestamp: new Date()
      });
      
      setProgressStatus('completed');
      setProgress(100);
      
    } catch (error) {
      console.error('Error during evaluation:', error);
      setProgressStatus('error');
      toast({
        title: "Error",
        description: "Failed to complete the evaluation. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Check progress of running evaluation
  const checkProgress = async (): Promise<number> => {
    // Since our FastAPI endpoint is synchronous, we don't need to poll for progress
    return progress;
  };
  
  // Fetch evaluation results after completion
  const fetchEvaluationResults = async () => {
    try {
      const response = await apiRequest('GET', '/api/evaluation-results');
      
      if (!response.ok) {
        throw new Error('Failed to fetch evaluation results');
      }
      
      const data: EvaluationResults = await response.json();
      setEvaluationResults(data);
      
      if (data.scores.length > 0) {
        toast({
          title: "Results Available",
          description: "Evaluation results are now available for viewing.",
          variant: "default",
        });
      }
    } catch (error) {
      console.error('Error fetching evaluation results:', error);
      toast({
        title: "Error",
        description: "Failed to fetch evaluation results. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <AppContext.Provider value={{
      mode,
      toggleMode,
      messages,
      isLoading,
      selectedFile,
      currentMessage,
      setCurrentMessage,
      sendMessage,
      handleFileChange,
      clearMessages,
      selectedModel,
      setSelectedModel,
      apiKey,
      setApiKey,
      evaluationData,
      updateEvaluationData,
      submitEvaluation,
      resetEvaluation,
      evaluationSubmitted,
      // New properties
      progress,
      progressStatus,
      startEvaluation,
      checkProgress,
      evaluationResults
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}
