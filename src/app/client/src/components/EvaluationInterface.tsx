import React, { useEffect, useRef, useState } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { ModelOption, PromptStyleOption, FieldMapping } from '@shared/types';
import { Play, PaperclipIcon, FileTextIcon, FileJsonIcon, FileSpreadsheetIcon, BarChart3Icon, InfoIcon } from 'lucide-react';
import EvaluationResultsComponent from './EvaluationResults';
import FieldMappingModal from './FieldMappingModal';
import { motion } from 'framer-motion';
import { defaultPrompts, sys_prompt } from '@shared/prompts';
import { useToast } from '@/hooks/use-toast';
import { isValidFileType } from '@/lib/utils';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import './scrollbar-hide.css';

// Add CSS for hiding scrollbars
const scrollbarStyles = `
  .custom-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .custom-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
`;



// Function to get the appropriate icon based on file extension
const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'csv':
      return <FileSpreadsheetIcon className="h-3 w-3 mr-1" />;
    case 'json':
    case 'jsonl':
      return <FileJsonIcon className="h-3 w-3 mr-1" />;
    case 'txt':
    default:
      return <FileTextIcon className="h-3 w-3 mr-1" />;
  }
};

export default function EvaluationInterface() {
  const {
    evaluationData,
    updateEvaluationData,
    resetEvaluation,
    progress,
    progressStatus,
    startEvaluation,
    evaluationResults,
    selectedEvalMethod,
    setSelectedEvalMethod,
    selfRefineIterations,
    setSelfRefineIterations,
    crossRefineIterations,
    setCrossRefineIterations,
    stopEvaluation,
    logMessages,
    setLogMessages
  } = useAppContext();
  
  const resultsRef = useRef<HTMLDivElement>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<PromptStyleOption | null>(null);
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const [showSelfRefineInput, setShowSelfRefineInput] = useState(false);
  const [showCrossRefineInput, setShowCrossRefineInput] = useState(false);
  const [selectedEvalMetric, setSelectedEvalMetric] = useState<string>('');
  const [showEvalMethodInfo, setShowEvalMethodInfo] = useState(false);
  const [selectedMethodInfo, setSelectedMethodInfo] = useState<'SELF-REFINE' | 'CROSS-REFINE' | null>(null);
  const [isCustomPromptSelected, setIsCustomPromptSelected] = useState(false);
  const [showFieldMappingModal, setShowFieldMappingModal] = useState(false);
  // Use evaluationData.fieldMapping instead of local state
  const fieldMapping = evaluationData.fieldMapping || {
    inputText: null,
    expectedOutput: null,
    actualOutput: null,
    context: null,
    retrievalContext: null,
    metadata: null,
    comments: null
  };
  
  // API Key states
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [anthropicApiKey, setAnthropicApiKey] = useState('');
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [grokApiKey, setGrokApiKey] = useState('');
  
  const { toast } = useToast();
  
  // Helper function to get provider family for a model
  const getModelProvider = (model: string): string => {
    if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(model)) {
      return 'openai';
    } else if (['claude-3-7-sonnet-latest'].includes(model)) {
      return 'anthropic';
    } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(model)) {
      return 'gemini';
    } else if (['grok-3-latest'].includes(model)) {
      return 'grok';
    } else if (model === 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free') {
      return 'free';
    }
    return 'unknown';
  };
  
  // Helper functions to determine which API keys are needed
  const getSelectedModelProviders = () => {
    const providers = new Set();
    evaluationData.selectedModels.forEach(model => {
      if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(model)) {
        providers.add('openai');
      } else if (['claude-3-7-sonnet-latest'].includes(model)) {
        providers.add('anthropic');
      } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(model)) {
        providers.add('gemini');
      } else if (['grok-3-latest'].includes(model)) {
        providers.add('grok');
      }
    });
    return providers;
  };
  
  const modelOptions = [
    { value: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free', label: 'Llama 3.3 70B' },
    { value: 'claude-3-7-sonnet-latest', label: 'Claude 3.7 Sonnet' },
    { value: 'gpt-4o-2024-11-20', label: 'GPT-4o' },
    { value: 'gpt-4.1-2025-04-14', label: 'GPT-4.1' },
    { value: 'gpt-4.1-nano-2025-04-14', label: 'GPT-4.1 nano' },
    { value: 'gemini-2.5-pro-preview-05-06', label: 'Gemini 2.5 Pro' },
    { value: 'gemini-2.5-flash-preview-04-17', label: 'Gemini 2.5 Flash' },
    { value: 'grok-3-latest', label: 'Grok 3 Beta' }
  ];
  
  const promptStyleOptions = [
    { value: 'Zero-shot', label: 'Zero-shot' },
    { value: 'Few-shot', label: 'Few-shot' },
    { value: 'Zero-shot-CoT', label: 'Zero-shot-CoT' },
    { value: 'Few-shot-CoT', label: 'Few-shot-CoT' }
  ];
  
  const evalMetricOptions: { value: string; label: string; description: string; category: string }[] = [
    // Reference-based metrics (require ground truth/gold standard)
    { value: 'accuracy', label: 'Accuracy', description: 'TP + TN / (TP + TN + FP + FN)', category: 'Reference-based' },
    { value: 'precision', label: 'Precision', description: 'TP / (TP + FP)', category: 'Reference-based' },
    { value: 'recall', label: 'Recall', description: 'TP / (TP + FN)', category: 'Reference-based' },
    { value: 'f1-score', label: 'F1-Score', description: 'Harmonic mean of precision and recall', category: 'Reference-based' },
    { value: 'exact-match', label: 'Exact Match', description: 'Binary exact string matching', category: 'Reference-based' },
    
    // Reference-less metrics (can work without ground truth)
    { value: 'bleu', label: 'BLEU', description: 'Bilingual Evaluation Understudy for text similarity', category: 'Reference-less' },
    { value: 'rouge', label: 'ROUGE', description: 'Recall-Oriented Understudy for Gisting Evaluation', category: 'Reference-less' },
    { value: 'meteor', label: 'METEOR', description: 'Metric for Evaluation of Translation with Explicit ORdering', category: 'Reference-less' },
    { value: 'bertscore', label: 'BERTScore', description: 'Semantic similarity using BERT embeddings', category: 'Reference-less' },
    { value: 'cosine-similarity', label: 'Cosine Similarity', description: 'Cosine similarity between embeddings', category: 'Reference-less' }
  ];

  const referenceBased = evalMetricOptions.filter(m => m.category === 'Reference-based');
  const referenceLess = evalMetricOptions.filter(m => m.category === 'Reference-less');
  
  // Scroll to results when evaluation is completed
  useEffect(() => {
    if (progressStatus === 'completed' && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [progressStatus]);
  
  // Get progress status text
  const getProgressStatusText = () => {
    switch (progressStatus) {
      case 'pending':
        return 'Not started';
      case 'processing':
        if (progress < 90) return 'Generating results...';
        return 'Finalizing evaluation...';
      case 'completed':
        return 'Evaluation completed successfully';
      case 'error':
        return 'Error during evaluation';
      default:
        return 'Unknown status';
    }
  };

  const handlePromptPreview = (promptStyle: PromptStyleOption) => {
    setSelectedPrompt(promptStyle);
    setIsPromptModalOpen(true);
  };

  // --- Output Log Modal State and Logic ---
  const [showLogModal, setShowLogModal] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  // Auto-scroll log modal to bottom
  useEffect(() => {
    if (showLogModal && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logMessages, showLogModal]);

  // Close numeric inputs when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('[data-eval-method]')) {
        setShowSelfRefineInput(false);
        setShowCrossRefineInput(false);
      }
    };

    if (showSelfRefineInput || showCrossRefineInput) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showSelfRefineInput, showCrossRefineInput]);

  // Handle Escape key for modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showLogModal) {
        setShowLogModal(false);
      }
    };

    if (showLogModal) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [showLogModal]);

  // Validate API keys before starting evaluation
  const validateApiKeys = () => {
    const selectedProviders = getSelectedModelProviders();
    const missingKeys = [];
    const missingFeedbackKeys = [];
    
    // Check main model API keys
    if (selectedProviders.has('openai') && !openaiApiKey.trim()) {
      missingKeys.push('OpenAI');
    }
    if (selectedProviders.has('anthropic') && !anthropicApiKey.trim()) {
      missingKeys.push('Anthropic');
    }
    if (selectedProviders.has('gemini') && !geminiApiKey.trim()) {
      missingKeys.push('Gemini');
    }
    if (selectedProviders.has('grok') && !grokApiKey.trim()) {
      missingKeys.push('Grok');
    }

    // Check Cross-Refine feedback model API keys (only if different from main model provider)
    if (selectedEvalMethod === 'CROSS-REFINE' && 
        evaluationData.crossRefineModel && 
        evaluationData.crossRefineModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' &&
        evaluationData.selectedModels.length > 0 &&
        getModelProvider(evaluationData.crossRefineModel) !== getModelProvider(evaluationData.selectedModels[0])) {
      
      const feedbackProvider = getModelProvider(evaluationData.crossRefineModel);
      
      if (feedbackProvider === 'openai' && !openaiApiKey.trim()) {
        missingFeedbackKeys.push('OpenAI (for feedback model)');
      } else if (feedbackProvider === 'anthropic' && !anthropicApiKey.trim()) {
        missingFeedbackKeys.push('Anthropic (for feedback model)');
      } else if (feedbackProvider === 'gemini' && !geminiApiKey.trim()) {
        missingFeedbackKeys.push('Gemini (for feedback model)');
      } else if (feedbackProvider === 'grok' && !grokApiKey.trim()) {
        missingFeedbackKeys.push('Grok (for feedback model)');
      }
    }

    const allMissingKeys = [...missingKeys, ...missingFeedbackKeys];
    
    if (allMissingKeys.length > 0) {
      toast({
        title: "API Keys Required",
        description: `Please provide API keys for: ${allMissingKeys.join(', ')}`,
        variant: "destructive",
      });
      return false;
    }
    return true;
  };

  const handleStartEvaluation = () => {
    if (!validateApiKeys()) return;
    
    // Add validation for Cross-Refine model only if CROSS-REFINE is selected
    if (selectedEvalMethod === 'CROSS-REFINE' && !evaluationData.crossRefineModel) {
      toast({
        title: "Cross-Refine Model Required",
        description: "Please select a feedback model for cross-refinement.",
        variant: "destructive",
      });
      return;
    }
    
    // Pass API keys to startEvaluation
    const apiKeys = {
      openai: openaiApiKey,
      anthropic: anthropicApiKey,
      gemini: geminiApiKey,
      grok: grokApiKey
    };
    
    startEvaluation(apiKeys);
  };

  const handleFieldMapping = (mapping: FieldMapping) => {
    updateEvaluationData({ fieldMapping: mapping });
    toast({
      title: "Field Mapping Saved",
      description: `Mapped input text to "${mapping.inputText}" column.`,
      variant: "default",
    });
  };

  const handleFieldMappingClose = () => {
    setShowFieldMappingModal(false);
  };

  const evalMethodDescriptions = {
    'SELF-REFINE': {
      title: 'Self-Refine Process',
      description: 'A single model iteratively improves its own output through self-criticism and refinement.',
      process: 'Initial Claim → Self-Generated Feedback → Refined Claim → Repeat',
      benefits: ['Single model approach', 'Consistent reasoning style', 'Lower computational cost']
    },
    'CROSS-REFINE': {
      title: 'Cross-Refine Process', 
      description: 'Two different models work together - one generates claims while the other provides feedback.',
      process: 'Initial Claim (LLM A) → External Feedback (LLM B) → Refined Claim (LLM A) → Repeat',
      benefits: ['Diverse perspectives', 'Reduced bias', 'Enhanced quality through collaboration']
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      <style>{scrollbarStyles}</style>

      {showLogModal && (
        <dialog 
          open
          className="fixed inset-0 z-50 bg-black bg-opacity-60 overflow-auto m-0 p-0 w-full h-full max-w-none max-h-none"
        >
          <div 
            className="bg-gray-900 rounded-lg shadow-lg w-full max-w-4xl mx-auto my-8 p-6 relative flex flex-col"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg text-white font-bold">Evaluation Terminal</h3>
              <button
                onClick={() => setShowLogModal(false)}
                className="text-slate-400 hover:text-white"
                aria-label="Close terminal"
              >
                ✕
              </button>
            </div>
            <div
              ref={logRef}
              className="bg-black text-green-300 font-mono text-xs rounded p-4 overflow-y-auto border border-slate-700 flex-1 custom-scrollbar"
              style={{ 
                minHeight: '200px',
                maxHeight: '70vh',
                maxWidth: '90vw',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}
            >
              {logMessages.length === 0 ? (
                <span className="text-slate-400">evaluation@server:~$ # Waiting for evaluation to start...</span>
              ) : (
                logMessages.map((msg, idx) => (
                  <div key={`log-${idx}-${msg.slice(0, 10)}`} className="py-0.5 font-mono">
                    {msg}
                  </div>
                ))
              )}
            </div>
            <div className="mt-4 flex justify-between items-center text-xs text-slate-400">
              <div>
                {logMessages.length > 0 && (
                  <span>{logMessages.length} log entries</span>
                )}
              </div>
              <div className="space-x-2">
                {logMessages.length > 0 && (
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(logMessages.join('\n'));
                      toast({
                        title: 'Terminal output copied',
                        variant: 'default',
                      });
                    }}
                    className="text-slate-300 hover:text-white"
                  >
                    Copy All
                  </button>
                )}
                <button
                  onClick={() => setShowLogModal(false)}
                  className="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </dialog>
      )}

            <div className="flex flex-col h-full max-h-[calc(100vh-120px)]">
                {/* Scrollable Middle Section */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 min-h-0">
          <div className="max-w-6xl w-full mx-auto space-y-4">
            {/* Eval Mode System Message */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="px-2 py-4 bg-gray-700 border-0 shadow-xl border-blue-200 rounded-md mx-auto max-w-6xl w-full"
            >
              <p className="text-slate-300 text-center">
                This is the batch mode interface for processing large datasets. If you wish to extract claims from a single source, please switch back to Chat mode.
              </p>
            </motion.div>

            {/* Claim Evaluation Card */}
            <Card className="bg-gradient-to-t from-gray-800 to-gray-700 border border-gray-800 shadow-lg">
            <CardContent className="p-6 bg-gray-700 rounded-lg">
              <h2 className="text-xl text-white font-semibold mb-6">Claim Evaluation</h2>
          
          {/* Model Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Model</h3>
            <div className="flex items-center space-x-4">
              <Select 
                value={evaluationData.selectedModels.length > 0 ? evaluationData.selectedModels[0] : ''}
                onValueChange={(value) => {
                  const newModel = value ? (value as ModelOption) : null;
                  const selectedModels = newModel ? [newModel] : [];
                  updateEvaluationData({ selectedModels });
                  // If primary model is also cross-refine model, clear cross-refine model in evaluationData
                  if (newModel && evaluationData.crossRefineModel && newModel === evaluationData.crossRefineModel) {
                    updateEvaluationData({ crossRefineModel: null });
                  }
                }}
              >
                <SelectTrigger className="w-[300px] bg-gray-700 text-white border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none data-[state=open]:ring-0 data-[state=open]:outline-none">
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent className="bg-gray-700 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
                  {modelOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value} className="text-white focus:bg-gray-600 focus:text-white">
                      <span className="font-medium">{option.label}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* API Key Input - appears when paid model is selected */}
              {evaluationData.selectedModels.length > 0 && evaluationData.selectedModels[0] !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-slate-300 whitespace-nowrap">
                    {(() => {
                      const selectedModel = evaluationData.selectedModels[0];
                      if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                        return 'OpenAI API Key:';
                      } else if (['claude-3-7-sonnet-latest'].includes(selectedModel)) {
                        return 'Anthropic API Key:';
                      } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(selectedModel)) {
                        return 'Gemini API Key:';
                      } else if (['grok-3-latest'].includes(selectedModel)) {
                        return 'Grok API Key:';
                      }
                      return 'API Key:';
                    })()}
                  </label>
                  <input
                    type="password"
                    value={(() => {
                      const selectedModel = evaluationData.selectedModels[0];
                      if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                        return openaiApiKey;
                      } else if (['claude-3-7-sonnet-latest'].includes(selectedModel)) {
                        return anthropicApiKey;
                      } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(selectedModel)) {
                        return geminiApiKey;
                      } else if (['grok-3-latest'].includes(selectedModel)) {
                        return grokApiKey;
                      }
                      return '';
                    })()}
                    onChange={(e) => {
                      const selectedModel = evaluationData.selectedModels[0];
                      if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                        setOpenaiApiKey(e.target.value);
                      } else if (['claude-3-7-sonnet-latest'].includes(selectedModel)) {
                        setAnthropicApiKey(e.target.value);
                      } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(selectedModel)) {
                        setGeminiApiKey(e.target.value);
                      } else if (['grok-3-latest'].includes(selectedModel)) {
                        setGrokApiKey(e.target.value);
                      }
                    }}
                    placeholder={(() => {
                      const selectedModel = evaluationData.selectedModels[0];
                      if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                        return 'sk-...';
                      } else if (['claude-3-7-sonnet-latest'].includes(selectedModel)) {
                        return 'sk-ant-...';
                      } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(selectedModel)) {
                        return 'AI...';
                      } else if (['grok-3-latest'].includes(selectedModel)) {
                        return 'xai-...';
                      }
                      return 'Enter API key...';
                    })()}
                    className="w-[300px] px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
              )}
            </div>

            {/* Security Notice - appears when API key is shown */}
            {evaluationData.selectedModels.length > 0 && evaluationData.selectedModels[0] !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
              <div className="mt-3 p-3 bg-gray-800 rounded-lg border border-gray-600 max-w-fit">
                <p className="text-xs text-slate-400">
                  🔒 API keys are transmitted securely and are not stored. They're only used for your current evaluation session.
                </p>
              </div>
            )}
          </div>
          
          {/* Prompt Style Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Prompt Styles</h3>
            <p className="text-sm text-slate-300 mb-4">
              Select a prompt style for evaluation:
            </p>
            
            <div className="flex items-center space-x-4 mb-4">
              <Select 
                value={(() => {
                  if (isCustomPromptSelected) return 'Custom';
                  if (evaluationData.selectedPromptStyles.length > 0) return evaluationData.selectedPromptStyles[0];
                  return '';
                })()}
                onValueChange={(value) => {
                  if (value === 'Custom') {
                    setIsCustomPromptSelected(true);
                    updateEvaluationData({ selectedPromptStyles: [] });
                  } else {
                    setIsCustomPromptSelected(false);
                    const newPromptStyle = value as PromptStyleOption;
                    updateEvaluationData({ selectedPromptStyles: [newPromptStyle] });
                  }
                }}
              >
                <SelectTrigger className="w-[300px] bg-gray-700 text-white border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none data-[state=open]:ring-0 data-[state=open]:outline-none">
                  <SelectValue placeholder="Select prompt" />
                </SelectTrigger>
                <SelectContent className="bg-gray-700 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
                  {promptStyleOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value} className="text-white focus:bg-gray-600 focus:text-white">
                      <span className="font-medium">{option.label}</span>
                    </SelectItem>
                  ))}
                  <SelectItem value="Custom" className="text-white focus:bg-gray-600 focus:text-white">
                    <span className="font-medium">Custom</span>
                  </SelectItem>
                </SelectContent>
              </Select>

              {/* View Prompt Button - appears when default prompt is selected */}
              {evaluationData.selectedPromptStyles.length > 0 && !isCustomPromptSelected && (
                <Button
                  variant="outline"
                  size="sm"
                  className="bg-gray-700 hover:bg-gray-600 text-white border-slate-600"
                  onClick={() => {
                    setSelectedPrompt(evaluationData.selectedPromptStyles[0]);
                    setIsPromptModalOpen(true);
                    setShowSystemPrompt(false);
                  }}
                >
                  View Prompt
                </Button>
              )}
            </div>

            {/* Custom Prompt Section - only appears when Custom is selected */}
            {isCustomPromptSelected && (
              <div>
                <h4 className="text-md font-medium text-slate-300 mb-2">Custom Prompt</h4>
                <textarea
                  className="w-full p-3 border border-gray-800 bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  rows={4}
                  placeholder="Enter your custom prompt here..."
                  value={evaluationData.customPrompt || ''}
                  onChange={(e) => updateEvaluationData({ customPrompt: e.target.value })}
                />
              </div>
            )}
          </div>

          {/* Eval Methods Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Iterative Refinement Methods (Optional)</h3>
            <div className="flex items-center space-x-4">
              <Select
                value={selectedEvalMethod || 'STANDARD'}
                onValueChange={(value) => {
                  const newValue = value === 'STANDARD' ? null : value as 'SELF-REFINE' | 'CROSS-REFINE';
                  setSelectedEvalMethod(newValue);
                  setShowSelfRefineInput(false);
                  setShowCrossRefineInput(false);
                }}
              >
                <SelectTrigger className="w-[400px] bg-gray-700 text-white border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
                  <SelectValue placeholder="Select evaluation method" />
                </SelectTrigger>
                <SelectContent className="bg-gray-700 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
                  <SelectItem value="STANDARD" className="text-white focus:bg-gray-600 focus:text-white">
                    <span className="font-medium">Standard (No Refinement)</span>
                  </SelectItem>
                  <SelectItem value="SELF-REFINE" className="text-white focus:bg-gray-600 focus:text-white">
                    <span className="font-medium">SELF-REFINE</span>
                  </SelectItem>
                  <SelectItem value="CROSS-REFINE" className="text-white focus:bg-gray-600 focus:text-white">
                    <span className="font-medium">CROSS-REFINE</span>
                  </SelectItem>
                </SelectContent>
              </Select>

              {/* Info Button - appears when refinement method is selected */}
              {selectedEvalMethod && (
                <Button
                  variant="outline"
                  size="sm"
                  className="bg-gray-700 hover:bg-gray-600 text-white border-slate-600 px-2 py-1"
                  onClick={() => {
                    if (selectedEvalMethod === 'SELF-REFINE' || selectedEvalMethod === 'CROSS-REFINE') {
                      setSelectedMethodInfo(selectedEvalMethod);
                    }
                    setShowEvalMethodInfo(true);
                  }}
                >
                  <InfoIcon className="h-4 w-4" />
                </Button>
              )}

              {/* Iteration Selector - appears when refinement method is selected */}
              {selectedEvalMethod && (
                <div className="flex items-center space-x-2">
                  <label htmlFor="iterations-input" className="text-sm text-slate-300 whitespace-nowrap">
                    Iterations:
                  </label>
                  <div className="relative">
                    <input
                      id="iterations-input"
                      type="number"
                      min="1"
                      max="10"
                      value={selectedEvalMethod === 'SELF-REFINE' ? selfRefineIterations : crossRefineIterations}
                      onChange={(e) => {
                        const value = Math.max(1, Math.min(10, parseInt(e.target.value) || 1));
                        if (selectedEvalMethod === 'SELF-REFINE') {
                          setSelfRefineIterations(value);
                        } else {
                          setCrossRefineIterations(value);
                        }
                      }}
                      className="w-16 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary text-center"
                    />
                  </div>
                </div>
              )}

              {/* Cross-Refine Model Selector - appears when CROSS-REFINE is selected */}
              {selectedEvalMethod === 'CROSS-REFINE' && (
                <div className="flex items-center space-x-2">
                  <label htmlFor="feedback-model-select" className="text-sm text-slate-300 whitespace-nowrap">
                    Feedback Model:
                  </label>
                  <Select
                    value={evaluationData.crossRefineModel || ''}
                    onValueChange={(value) => {
                      const crossRefineModel = value ? (value as ModelOption) : null;
                      updateEvaluationData({ crossRefineModel });
                    }}
                  >
                    <SelectTrigger className="w-[180px] bg-gray-700 text-white border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none data-[state=open]:ring-0 data-[state=open]:outline-none">
                      <SelectValue placeholder="Select Model B" />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-700 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
                      {modelOptions
                        .filter(option => 
                          !evaluationData.selectedModels.includes(option.value as ModelOption)
                        )
                        .map((option) => (
                          <SelectItem key={option.value} value={option.value} className="text-white focus:bg-gray-600 focus:text-white">
                            {option.label}
                          </SelectItem>
                        ))
                      }
                    </SelectContent>
                  </Select>

                  {/* Cross-Refine API Key Input - appears when paid feedback model from different family is selected */}
                  {evaluationData.crossRefineModel && 
                   evaluationData.crossRefineModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' &&
                   evaluationData.selectedModels.length > 0 &&
                   getModelProvider(evaluationData.crossRefineModel) !== getModelProvider(evaluationData.selectedModels[0]) && (
                    <div className="flex items-center space-x-2">
                      <label className="text-sm text-slate-300 whitespace-nowrap">
                        {(() => {
                          const feedbackModel = evaluationData.crossRefineModel;
                          if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(feedbackModel!)) {
                            return 'OpenAI API Key:';
                          } else if (['claude-3-7-sonnet-latest'].includes(feedbackModel!)) {
                            return 'Anthropic API Key:';
                          } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(feedbackModel!)) {
                            return 'Gemini API Key:';
                          } else if (['grok-3-latest'].includes(feedbackModel!)) {
                            return 'Grok API Key:';
                          }
                          return 'API Key:';
                        })()}
                      </label>
                      <input
                        type="password"
                        value={(() => {
                          const feedbackModel = evaluationData.crossRefineModel;
                          if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(feedbackModel!)) {
                            return openaiApiKey;
                          } else if (['claude-3-7-sonnet-latest'].includes(feedbackModel!)) {
                            return anthropicApiKey;
                          } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(feedbackModel!)) {
                            return geminiApiKey;
                          } else if (['grok-3-latest'].includes(feedbackModel!)) {
                            return grokApiKey;
                          }
                          return '';
                        })()}
                        onChange={(e) => {
                          const feedbackModel = evaluationData.crossRefineModel;
                          if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(feedbackModel!)) {
                            setOpenaiApiKey(e.target.value);
                          } else if (['claude-3-7-sonnet-latest'].includes(feedbackModel!)) {
                            setAnthropicApiKey(e.target.value);
                          } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(feedbackModel!)) {
                            setGeminiApiKey(e.target.value);
                          } else if (['grok-3-latest'].includes(feedbackModel!)) {
                            setGrokApiKey(e.target.value);
                          }
                        }}
                        placeholder={(() => {
                          const feedbackModel = evaluationData.crossRefineModel;
                          if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(feedbackModel!)) {
                            return 'sk-...';
                          } else if (['claude-3-7-sonnet-latest'].includes(feedbackModel!)) {
                            return 'sk-ant-...';
                          } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(feedbackModel!)) {
                            return 'AI...';
                          } else if (['grok-3-latest'].includes(feedbackModel!)) {
                            return 'xai-...';
                          }
                          return 'Enter API key...';
                        })()}
                        className="w-[200px] px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Eval Metrics Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Eval Metrics</h3>
            <Select
              value={selectedEvalMetric}
              onValueChange={(value) => {
                setSelectedEvalMetric(value);
                updateEvaluationData({ evalMetric: value });
              }}
            >
              <SelectTrigger className="w-[450px] bg-gray-700 text-white border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none data-[state=open]:ring-0 data-[state=open]:outline-none">
                <BarChart3Icon className="h-4 w-4 mr-2 flex-shrink-0" />
                <SelectValue placeholder="Select evaluation metric" />
              </SelectTrigger>
              <SelectContent 
                side="right" 
                align="start"
                className="bg-gray-700 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none min-w-[500px] max-h-[300px] overflow-y-auto"
              >
                {/* Reference-based metrics */}
                <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wide bg-gray-600">
                  Reference-based
                </div>
                {referenceBased.map((option) => (
                  <SelectItem 
                    key={option.value} 
                    value={option.value} 
                    className="text-white focus:bg-gray-800 focus:text-white pl-8 pr-3 py-3 min-h-[60px] bg-gray-700"
                  >
                    <div className="flex flex-col text-white w-full">
                      <span className="font-medium">{option.label}</span>
                      <span className="text-xs text-slate-400 font-normal leading-tight mt-1 break-words">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
                
                {/* Separator */}
                <div className="mx-2 my-1 border-t border-slate-600"></div>
                
                {/* Reference-less metrics */}
                <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wide bg-gray-600">
                  Reference-less
                </div>
                {referenceLess.map((option) => (
                  <SelectItem 
                    key={option.value} 
                    value={option.value} 
                    className="text-white focus:bg-gray-800 focus:text-white pl-8 pr-3 py-3 min-h-[60px] bg-gray-700"
                  >
                    <div className="flex flex-col text-white w-full">
                      <span className="font-medium">{option.label}</span>
                      <span className="text-xs text-slate-400 font-normal leading-tight mt-1 break-words">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* File Upload Section */}
          <div className="mb-8">
            <div className="mt-6">
              <h4 className="text-md font-medium text-white mb-2">Upload Dataset</h4>
              <div className="flex items-center space-x-2">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        type="button"
                        variant="outline"
                        className="flex items-center text-slate-300 hover:text-primary-600 bg-gray-800 hover:bg-gray-600"
                        onClick={() => document.getElementById('file-upload')?.click()}
                      >
                        <PaperclipIcon className="h-4 w-4 mr-1" />
                        <span className="text-sm">Upload</span>
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Accepted formats: CSV, JSON, JSONL</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                {evaluationData.file && (
                  <div className="flex flex-col space-y-2">
                    <div className="text-sm text-slate-500 flex items-center">
                      {getFileIcon(evaluationData.file.name)}
                      <span>{evaluationData.file.name}</span>
                      <Button
                        variant="outline"
                        size="sm"
                        className="ml-3 bg-gray-700 hover:bg-gray-600 text-white border-slate-600 text-xs px-2 py-1"
                        onClick={() => setShowFieldMappingModal(true)}
                      >
                        Edit Mapping
                      </Button>
                    </div>
                    {fieldMapping.inputText && (
                      <div className="text-xs text-slate-400 ml-4">
                        Input: "{fieldMapping.inputText}"
                        {fieldMapping.expectedOutput && `, Expected Output: "${fieldMapping.expectedOutput}"`}
                        {fieldMapping.actualOutput && `, Actual Output: "${fieldMapping.actualOutput}"`}
                        {fieldMapping.context && `, Context: "${fieldMapping.context}"`}
                        {fieldMapping.retrievalContext && `, Retrieval Context: "${fieldMapping.retrievalContext}"`}
                        {fieldMapping.metadata && `, Metadata: "${fieldMapping.metadata}"`}
                        {fieldMapping.comments && `, Comments: "${fieldMapping.comments}"`}
                      </div>
                    )}
                  </div>
                )}
              </div>
              <input  
                type="file"
                id="file-upload"
                className="hidden"
                accept=".csv,.json,.jsonl,text/csv,application/json,application/x-jsonlines"
                onChange={(e) => {
                  const file = e.target.files?.[0] || null;
                  if (file && !isValidFileType(file)) {
                    toast({
                      title: "Invalid File Type",
                      description: "Please upload only CSV, JSON, or JSONL files.",
                      variant: "destructive",
                    });
                    e.target.value = ''; // Reset input
                    return;
                  }
                  if (file) {
                    updateEvaluationData({ file });
                    setShowFieldMappingModal(true);
                  } else {
                    updateEvaluationData({ file: null, fieldMapping: null });
                  }
                }}
              />
            </div>
          </div>
          
              {/* Visualization Section */}
              <div ref={resultsRef}>
                {progressStatus === 'completed' && evaluationResults && evaluationResults.scores.length > 0 && (
                  <EvaluationResultsComponent 
                    results={evaluationResults}
                    selectedModels={evaluationData.selectedModels}
                    selectedPromptStyles={evaluationData.selectedPromptStyles}
                  />
                )}
              </div>
              
              {/* Reset Button */}
              {progressStatus === 'completed' && (
                <div className="flex justify-end mt-8">
                  <Button
                    type="button"
                    onClick={resetEvaluation}
                    className="bg-slate-200 hover:bg-slate-300 text-slate-800"
                  >
                    Start New Evaluation
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

            {/* Evaluation Progress Section */}
            <Card className="bg-gradient-to-t from-gray-800 to-gray-700 border border-gray-800 shadow-lg">
              <CardContent className="p-6 bg-gray-700 rounded-lg">
                {progressStatus === 'pending' ? (
                  /* Initial state - Just the start button */
                  <div className="flex flex-col items-center space-y-4">
                    <h3 className="text-lg font-medium text-white">Ready to Evaluate</h3>
                    <p className="text-sm text-slate-300 text-center">
                      Click the button below to start your batch evaluation
                    </p>
                    <Button
                      type="button"
                      onClick={handleStartEvaluation}
                      disabled={
                        evaluationData.selectedModels.length === 0 || 
                        evaluationData.selectedPromptStyles.length === 0 || 
                        !evaluationData.file
                      }
                      className="bg-primary hover:bg-primary/90 text-white px-8 py-3 text-lg"
                    >
                      <Play className="h-5 w-5 mr-2" />
                      Start Evaluation
                    </Button>
                  </div>
                ) : (
                  /* Progress state - Animated progress bar and controls */
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-lg font-medium text-white">Evaluation Progress</h3>
                      <span className="text-sm font-medium text-slate-300">{progress}%</span>
                    </div>
                    
                    <motion.div
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ duration: 0.3, delay: 0.2 }}
                      className="origin-left"
                    >
                      <Progress value={progress} className="h-3 mb-2" />
                    </motion.div>
                    
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3, delay: 0.4 }}
                      className="flex justify-between items-center mt-2"
                    >
                      <span className="text-sm text-slate-300">{getProgressStatusText()}</span>
                      <div className="flex space-x-2">
                        {progressStatus === 'processing' ? (
                          <>
                            <Button
                              type="button"
                              onClick={stopEvaluation}
                              variant="destructive"
                              className="bg-red-600 hover:bg-red-700 text-white"
                            >
                              Stop Evaluation
                            </Button>
                            <Button
                              type="button"
                              onClick={() => setShowLogModal(true)}
                              variant="outline"
                              className="bg-gray-800 hover:bg-gray-700 text-white border-slate-600"
                            >
                              View Terminal
                            </Button>
                          </>
                        ) : (
                          <>
                            <Button
                              type="button"
                              onClick={handleStartEvaluation}
                              className="bg-gray-800 hover:bg-gray-900 text-white"
                            >
                              Restart Evaluation
                            </Button>
                            <Button
                              type="button"
                              onClick={() => setShowLogModal(true)}
                              variant="outline"
                              className="bg-gray-800 hover:bg-gray-700 text-white border-slate-600"
                            >
                              View Terminal
                            </Button>
                          </>
                        )}
                      </div>
                    </motion.div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Fixed Footer - Additional buttons if needed */}
        <div className="flex-shrink-0 p-4">
          {/* This can remain empty or contain fixed footer content */}
        </div>
      </div>

            {/* Prompt Preview Modal */}
      <Dialog open={isPromptModalOpen} onOpenChange={(open) => {
        setIsPromptModalOpen(open);
        if (!open) {
          setShowSystemPrompt(false);
        }
      }}>
        <DialogContent 
          className="max-w-3xl max-h-[80vh]  
          flex-1 flex-col overflow-auto scrollbar-hide
          bg-gray-800 
          text-slate-200">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <div>
            <DialogTitle className="text-white">
              {(() => {
                if (showSystemPrompt) {
                  return 'System Prompt';
                }
                return selectedPrompt && defaultPrompts[selectedPrompt].title;
              })()}
            </DialogTitle>
            <DialogDescription className="text-slate-300 mt-4">
              {(() => {
                if (showSystemPrompt) {
                  return 'The system prompt that guides the model\'s behavior';
                }
                return selectedPrompt && defaultPrompts[selectedPrompt].description;
              })()}
            </DialogDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="bg-gray-700 hover:bg-gray-600 text-white border-slate-600"
                onClick={() => setShowSystemPrompt(!showSystemPrompt)}
              >
                {showSystemPrompt ? 'View Prompt' : 'View System Prompt'}
              </Button>
            </div>
          </DialogHeader>
          <div className="mt-4 flex-1 overflow-auto">
            <pre className="bg-gray-700 text-slate-200 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono text-sm">
              {(() => {
                if (showSystemPrompt) {
                  return sys_prompt;
                }
                return selectedPrompt && defaultPrompts[selectedPrompt].template;
              })()}
            </pre>
          </div>
        </DialogContent>
      </Dialog>

      {/* Evaluation Method Info Modal */}
      <Dialog open={showEvalMethodInfo} onOpenChange={setShowEvalMethodInfo}>
        <DialogContent 
          className="max-w-2xl bg-gray-800 text-slate-200"
        >
          <DialogHeader>
            <DialogTitle className="text-white">
              {selectedMethodInfo && evalMethodDescriptions[selectedMethodInfo].title}
            </DialogTitle>
            <DialogDescription className="text-slate-300">
              {selectedMethodInfo && evalMethodDescriptions[selectedMethodInfo].description}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            {selectedMethodInfo && (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-white mb-2">Process Flow:</h4>
                  <div className="bg-gray-700 p-3 rounded-lg">
                    <code className="text-sm text-slate-200">
                      {evalMethodDescriptions[selectedMethodInfo].process}
                    </code>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-white mb-2">Benefits:</h4>
                  <ul className="space-y-1">
                    {evalMethodDescriptions[selectedMethodInfo].benefits.map((benefit, index) => (
                      <li key={index} className="text-sm text-slate-300 flex items-center">
                        <span className="text-green-400 mr-2">•</span>
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Field Mapping Modal */}
      <FieldMappingModal
        isOpen={showFieldMappingModal}
        onClose={handleFieldMappingClose}
        file={evaluationData.file}
        onMapping={handleFieldMapping}
      />
    </div>
  );
}