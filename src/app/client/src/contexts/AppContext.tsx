import React, { createContext, useContext, useState, useEffect, ReactNode, useMemo } from 'react';
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
import { getWsUrl, getApiUrl } from '@/config';

type AppMode = 'chat' | 'evaluation';

export interface AppContextType {
  mode: AppMode;
  toggleMode: () => void;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
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
  
  // Batch mode
  evaluationData: EvaluationData;
  updateEvaluationData: (data: Partial<EvaluationData>) => void;
  resetEvaluation: () => void;
  
  // Evaluation methods
  selectedEvalMethod: 'SELF-REFINE' | 'CROSS-REFINE' | null;
  setSelectedEvalMethod: (method: 'SELF-REFINE' | 'CROSS-REFINE' | null) => void;
  selfRefineIterations: number;
  setSelfRefineIterations: (iterations: number) => void;
  crossRefineIterations: number;
  setCrossRefineIterations: (iterations: number) => void;
  
  // New evaluation features
  progress: number;
  progressStatus: 'pending' | 'processing' | 'completed' | 'error';
  startEvaluation: (apiKeys?: { openai?: string; anthropic?: string; gemini?: string; grok?: string }) => Promise<void>;
  stopEvaluation: () => void;
  evaluationResults: EvaluationResults | null;
  logMessages: string[];
  setLogMessages: React.Dispatch<React.SetStateAction<string[]>>;
}

const defaultEvaluationData: EvaluationData = {
  file: null,
  selectedModels: [],
  selectedPromptStyles: [],
  fieldMapping: null,
  evalMetric: null
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<AppMode>('chat');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateId(),
      content: "🤖 Hello! I'm your claim normalization assistant. You can provide your source text to analyze.",
      sender: 'system',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentMessage, setCurrentMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState<ModelOption>('meta-llama/Llama-3.3-70B-Instruct-Turbo-Free');
  const [apiKey, setApiKey] = useState('');
  const [evaluationData, setEvaluationData] = useState<EvaluationData>(defaultEvaluationData);
  
  // Evaluation methods state
  const [selectedEvalMethod, setSelectedEvalMethod] = useState<'SELF-REFINE' | 'CROSS-REFINE' | null>(null);
  const [selfRefineIterations, setSelfRefineIterations] = useState<number>(1);
  const [crossRefineIterations, setCrossRefineIterations] = useState<number>(1);
  
  // New state for progress tracking
  const [progress, setProgress] = useState<number>(0);
  const [progressStatus, setProgressStatus] = useState<'pending' | 'processing' | 'completed' | 'error'>('pending');
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResults | null>(null);
  const [logMessages, setLogMessages] = useState<string[]>([]);
  
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

      console.log('Sending request to /chat');
      // Call API to normalize claim
      const response = await fetch(`${getApiUrl()}/chat`, {
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

  const resetEvaluation = () => {
    setEvaluationData(defaultEvaluationData);
    setSelectedEvalMethod(null);
    setSelfRefineIterations(1);
    setCrossRefineIterations(1);
    setProgress(0);
    setProgressStatus('pending');
    setEvaluationResults(null);
    setIsLoading(false); // Ensure loading state is cleared
  };
  
  // WebSocket for real-time evaluation updates
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [sessionId, setSessionId] = useState<string>('');

  // Generate session ID on mount
  useEffect(() => {
    const array = new Uint32Array(1);
    window.crypto.getRandomValues(array);
    const id = array[0].toString(36);
    setSessionId(id);
  }, []);

  // New methods for model evaluation with progress tracking using WebSocket
  const startEvaluation = async (apiKeys?: { openai?: string; anthropic?: string; gemini?: string; grok?: string }): Promise<void> => {
    // Validation
    if (evaluationData.selectedModels.length === 0 || evaluationData.selectedPromptStyles.length === 0) {
      toast({
        title: "Selection Required",
        description: "Please select one model and one prompt style.",
        variant: "destructive",
      });
      return;
    }
    
    if (!evaluationData.file) {
      toast({
        title: "File Required",
        description: "Please upload a dataset file.",
        variant: "destructive",
      });
      return;
    }
    
    if (!evaluationData.fieldMapping || !evaluationData.fieldMapping.inputText) {
      toast({
        title: "Field Mapping Required",
        description: "Please map the input text field for your dataset.",
        variant: "destructive",
      });
      return;
    }
    
    if (!sessionId) {
      toast({
        title: "Error",
        description: "Session not initialized. Please refresh the page.",
        variant: "destructive",
      });
      return;
    }
    
    setProgressStatus('processing');
    setProgress(0);
    // Don't set isLoading for WebSocket evaluation since we have real-time updates
    
    try {
      // Create WebSocket connection
      const wsUrl = `${getWsUrl()}/ws/evaluation/${sessionId}`;
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        setLogMessages(prev => [...prev, `> Connected to evaluation service (Session: ${sessionId})`]);
        
        // Calculate iterations based on selected eval method
        let iterations = 0;
        if (selectedEvalMethod === 'SELF-REFINE') {
          iterations = selfRefineIterations;
        } else if (selectedEvalMethod === 'CROSS-REFINE') {
          iterations = crossRefineIterations;
        }
        
        // Convert file to base64
        const reader = new FileReader();
        reader.onload = () => {
          const fileContent = reader.result as string;
          const base64Content = fileContent.split(',')[1]; // Remove data:... prefix
          
          // Check file size and warn user if it's large
          const fileSizeInMB = evaluationData.file!.size / (1024 * 1024);
          const base64SizeInMB = (base64Content.length * 0.75) / (1024 * 1024); // Base64 is ~33% larger
          
          if (fileSizeInMB > 2) {
            setLogMessages(prev => [...prev, `> Warning: Large file detected (${fileSizeInMB.toFixed(1)}MB). This may cause connection issues.`]);
            
            if (fileSizeInMB > 5) {
              setLogMessages(prev => [...prev, `> Consider reducing file size or splitting into smaller chunks.`]);
            }
          }
          
          // Prepare evaluation data
          const evaluationPayload = {
            type: 'start_evaluation',
            data: {
              models: evaluationData.selectedModels,
              prompt_styles: evaluationData.selectedPromptStyles,
              file_data: {
                name: evaluationData.file!.name,
                content: base64Content
              },
              self_refine_iterations: iterations,
              eval_method: selectedEvalMethod,
              custom_prompt: evaluationData.customPrompt || null,
              api_keys: apiKeys || {},
              cross_refine_model: evaluationData.crossRefineModel || null,
              field_mapping: evaluationData.fieldMapping || null,
              eval_metric: evaluationData.evalMetric || null
            }
          };
          
          setLogMessages(prev => [...prev, `> Sending evaluation request...`]);
          // Send evaluation request
          websocket.send(JSON.stringify(evaluationPayload));
        };
        
        reader.onerror = () => {
          setLogMessages(prev => [...prev, `✗ Failed to read file`]);
          setProgressStatus('error');
        };
        
        reader.readAsDataURL(evaluationData.file!);
      };
      
      websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        switch (message.type) {
          case 'progress':
            setProgress(message.data.percentage || 0);
            break;
            
          case 'log':
            // Add server logs with terminal-style prefix
            setLogMessages(prev => [...prev, `$ ${message.data.message}`]);
            break;
            
          case 'log_batch':
            // Handle batched log messages
            if (message.data.messages && Array.isArray(message.data.messages)) {
              const newLogMessages = message.data.messages.map((logData: any) => `$ ${logData.message}`);
              setLogMessages(prev => [...prev, ...newLogMessages]);
            }
            break;
            
          case 'status':
            // Add status updates with different prefix
            setLogMessages(prev => [...prev, `> ${message.data.message}`]);
            if (message.data.message.includes('stopped') || message.data.message.includes('cancelled')) {
              setProgressStatus('error');
              setLogMessages(prev => [...prev, `✗ Evaluation stopped`]);
              websocket.close(1000, 'Evaluation stopped');
              
              toast({
                title: "Evaluation Stopped",
                description: "The evaluation has been stopped.",
                variant: "default",
              });
            }
            break;
            
          case 'complete':
            setLogMessages(prev => [...prev, `✓ Evaluation completed successfully`]);
            if (message.data.scores) {
              // Convert scores to the expected format
              const results: MeteorScore[] = Object.entries(message.data.scores).map(([key, score]) => {
                const [model_name, prompt_style] = key.split('_');
                return {
                  model: model_name.replace(/_/g, '/'), // Convert back to original model name
                  promptStyle: prompt_style.replace(/_/g, '-'),
                  score: score as number
                };
              });
              
              setEvaluationResults({
                scores: results,
                timestamp: new Date()
              });
              
              // Add final scores to log
              results.forEach(result => {
                setLogMessages(prev => [...prev, `  ${result.model} (${result.promptStyle}): ${result.score.toFixed(4)}`]);
              });
            }
             setProgressStatus('completed');
             setProgress(100);
             websocket.close();
            
            toast({
              title: "Evaluation Complete",
              description: "Successfully completed the evaluation.",
              variant: "default",
            });
            break;
            
          case 'error':
            setLogMessages(prev => [...prev, `✗ Error: ${message.data.message}`]);
            setProgressStatus('error');
            websocket.close();
            
            toast({
              title: "Error",
              description: message.data.message,
              variant: "destructive",
            });
            break;
        }
      };
      
      websocket.onerror = (error) => {
        setLogMessages(prev => [...prev, `✗ Connection error: Failed to connect to evaluation service`]);
        setProgressStatus('error');
        
        toast({
          title: "Connection Error",
          description: "Failed to connect to the evaluation service.",
          variant: "destructive",
        });
      };
      
      websocket.onclose = (event) => {
        // Handle specific close codes
        if (event.code === 1009) {
          setLogMessages(prev => [...prev, `✗ File too large for WebSocket transmission`]);
          setLogMessages(prev => [...prev, `> Try using a smaller file (< 2MB) or reduce the number of rows`]);
          setProgressStatus('error');
          toast({
            title: "File Too Large",
            description: "Please use a smaller file (< 2MB) or reduce the dataset size.",
            variant: "destructive",
          });
        } else if (event.code !== 1000 && progressStatus !== 'completed') {
          setLogMessages(prev => [...prev, `> Connection closed unexpectedly (code: ${event.code})`]);
          if (progressStatus === 'processing') {
            setProgressStatus('error');
            toast({
              title: "Connection Lost",
              description: "Connection to evaluation service was lost.",
              variant: "destructive",
            });
          }
        } else {
          setLogMessages(prev => [...prev, `> Disconnected from evaluation service`]);
        }
        setWs(null);
      };
      
      setWs(websocket);
      
    } catch (error) {
      setLogMessages(prev => [...prev, `✗ Failed to start evaluation: ${error instanceof Error ? error.message : 'Unknown error'}`]);
      setProgressStatus('error');
      
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to start the evaluation.",
        variant: "destructive",
      });
    }
  };

  // Function to stop evaluation
  const stopEvaluation = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      // Send stop message
      ws.send(JSON.stringify({ type: 'stop_evaluation' }));
      
      // Update state immediately
      setProgressStatus('error');
      setLogMessages(prev => [...prev, `✗ Evaluation stopped by user`]);
      
      // Close WebSocket connection after a short delay to allow server to process stop message
      setTimeout(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.close(1000, 'Evaluation stopped by user');
        }
      }, 500);
      
      toast({
        title: "Evaluation Stopped",
        description: "The evaluation has been stopped successfully.",
        variant: "default",
      });
    } else {
      // If WebSocket is not connected, just update the state
      setProgressStatus('error');
      setLogMessages(prev => [...prev, `✗ Evaluation stopped (no active connection)`]);
      
      toast({
        title: "Evaluation Stopped",
        description: "The evaluation has been stopped successfully.",
        variant: "default",
      });
    }
  };
  
  const contextValue = useMemo(() => ({
    mode,
    toggleMode,
    messages,
    setMessages,
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
    resetEvaluation,
    // Evaluation methods
    selectedEvalMethod,
    setSelectedEvalMethod,
    selfRefineIterations,
    setSelfRefineIterations,
    crossRefineIterations,
    setCrossRefineIterations,
    // New properties
    progress,
    progressStatus,
    startEvaluation,
    stopEvaluation,
    evaluationResults,
    logMessages,
    setLogMessages
  }), [
    mode, messages, isLoading, selectedFile, currentMessage, selectedModel, apiKey,
    evaluationData, selectedEvalMethod, selfRefineIterations, crossRefineIterations,
    progress, progressStatus, evaluationResults, logMessages
  ]);

  return (
    <AppContext.Provider value={contextValue}>
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
