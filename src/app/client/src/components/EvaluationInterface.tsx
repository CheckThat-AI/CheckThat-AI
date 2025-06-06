import React, { useEffect, useRef, useState } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { ModelOption, PromptStyleOption } from '@shared/types';
import { Play, PaperclipIcon, FileTextIcon, FileJsonIcon, FileSpreadsheetIcon } from 'lucide-react';
import EvaluationResultsComponent from './EvaluationResults';
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
  
  // API Key states
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [anthropicApiKey, setAnthropicApiKey] = useState('');
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [grokApiKey, setGrokApiKey] = useState('');
  
  const { toast } = useToast();
  
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

    if (missingKeys.length > 0) {
      toast({
        title: "API Keys Required",
        description: `Please provide API keys for: ${missingKeys.join(', ')}`,
        variant: "destructive",
      });
      return false;
    }
    return true;
  };

  const handleStartEvaluation = () => {
    if (!validateApiKeys()) return;
    
    // Add validation for Cross-Refine model
    if (selectedEvalMethod === 'CROSS-REFINE' && !evaluationData.crossRefineModel) {
      toast({
        title: "Cross-Refine Model Required",
        description: "Please select a model for cross-refinement.",
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
                This is the evaluation mode interface for batch-processing large datasets. If you wish to extract claims from a single source, please switch back to the Chat mode.
              </p>
            </motion.div>

            {/* Claim Evaluation Card */}
            <Card className="bg-gradient-to-t from-gray-800 to-gray-700 border border-gray-800 shadow-lg">
            <CardContent className="p-6 bg-gray-700 rounded-lg">
              <h2 className="text-xl text-white font-semibold mb-6">Claim Evaluation</h2>
          
          {/* Model Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Models</h3>
            <p className="text-sm text-slate-300 mb-4">
              Select one model to use for claim normalization:
            </p>
            
            <ToggleGroup 
              type="single" 
              value={evaluationData.selectedModels.length > 0 ? evaluationData.selectedModels[0] : ''}
              onValueChange={(value) => {
                const newModel = value ? (value as ModelOption) : null;
                updateEvaluationData({ selectedModels: newModel ? [newModel] : [] });
                // If primary model is also cross-refine model, clear cross-refine model in evaluationData
                if (newModel && evaluationData.crossRefineModel && newModel === evaluationData.crossRefineModel) {
                  updateEvaluationData({ crossRefineModel: null });
                }
              }}
              className="justify-start"
            >
              {modelOptions.map((option) => (
                <ToggleGroupItem 
                  key={option.value} 
                  value={option.value}
                  variant="outline"
                  className={`border-2 px-1 py-1 font-medium text-slate-200 bg-gray-800 border-gray-600 data-[state=on]:bg-primary/10 data-[state=on]:border-primary data-[state=on]:text-primary min-w-[112px] text-start`}
                >
                  {option.label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          {/* API Keys Section - Only show if paid models are selected */}
          {getSelectedModelProviders().size > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-medium text-white mb-3">API Keys</h3>
              <p className="text-sm text-slate-300 mb-4">
                Enter API keys for the selected paid models:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* OpenAI API Key */}
                {getSelectedModelProviders().has('openai') && (
                  <div>
                    <label htmlFor="openai-api-key" className="block text-sm font-medium text-slate-300 mb-2">
                      OpenAI API Key
                      <span className="text-xs text-slate-400 ml-2">(GPT-4o, GPT-4.1, GPT-4.1 nano)</span>
                    </label>
                    <input
                      id="openai-api-key"
                      type="password"
                      value={openaiApiKey}
                      onChange={(e) => setOpenaiApiKey(e.target.value)}
                      placeholder="sk-..."
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                )}

                {/* Anthropic API Key */}
                {getSelectedModelProviders().has('anthropic') && (
                  <div>
                    <label htmlFor="anthropic-api-key" className="block text-sm font-medium text-slate-300 mb-2">
                      Anthropic API Key
                      <span className="text-xs text-slate-400 ml-2">(Claude 3.7 Sonnet)</span>
                    </label>
                    <input
                      id="anthropic-api-key"
                      type="password"
                      value={anthropicApiKey}
                      onChange={(e) => setAnthropicApiKey(e.target.value)}
                      placeholder="sk-ant-..."
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                )}

                {/* Gemini API Key */}
                {getSelectedModelProviders().has('gemini') && (
                  <div>
                    <label htmlFor="gemini-api-key" className="block text-sm font-medium text-slate-300 mb-2">
                      Gemini API Key
                      <span className="text-xs text-slate-400 ml-2">(Gemini 2.5 Pro, Gemini 2.5 Flash)</span>
                    </label>
                    <input
                      id="gemini-api-key"
                      type="password"
                      value={geminiApiKey}
                      onChange={(e) => setGeminiApiKey(e.target.value)}
                      placeholder="AI..."
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                )}

                {/* Grok API Key */}
                {getSelectedModelProviders().has('grok') && (
                  <div>
                    <label htmlFor="grok-api-key" className="block text-sm font-medium text-slate-300 mb-2">
                      Grok API Key
                      <span className="text-xs text-slate-400 ml-2">(Grok 3 Beta)</span>
                    </label>
                    <input
                      id="grok-api-key"
                      type="password"
                      value={grokApiKey}
                      onChange={(e) => setGrokApiKey(e.target.value)}
                      placeholder="xai-..."
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                )}
              </div>

              <div className="mt-3 p-3 bg-gray-800 rounded-lg border border-gray-600">
                <p className="text-xs text-slate-400">
                  🔒 API keys are transmitted securely and are not stored. They're only used for your current evaluation session.
                </p>
              </div>
            </div>
          )}
          
          {/* Prompt Style Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Prompt Styles</h3>
            <p className="text-sm text-slate-300 mb-4">
              Select one prompt style for evaluation:
            </p>
            
            {/* Default Prompts Section */}
            <div className="mb-6">
              <h4 className="text-md font-medium text-slate-300 mb-2">Default Prompts</h4>
              
              <ToggleGroup 
                type="single" 
                value={evaluationData.selectedPromptStyles.length > 0 ? evaluationData.selectedPromptStyles[0] : ''}
                onValueChange={(value) => {
                  const newPromptStyle = value ? (value as PromptStyleOption) : null;
                  updateEvaluationData({ selectedPromptStyles: newPromptStyle ? [newPromptStyle] : [] });
                }}
                className="justify-start flex-wrap mb-3"
              >
                {promptStyleOptions.map((option) => (
                  <ToggleGroupItem 
                    key={option.value} 
                    value={option.value}
                    variant="outline"
                    className={`border-2 px-4 py-2 font-medium text-slate-200 bg-gray-800 border-gray-600 data-[state=on]:bg-primary/10 data-[state=on]:border-primary data-[state=on]:text-primary min-w-[120px] text-center`}
                  >
                    {option.label}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
              
              <div className="flex flex-wrap gap-2 mb-3">
                {promptStyleOptions.map((option) => (
                  <Button
                    key={`view-${option.value}`}
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:text-white hover:bg-gray-700"
                    onClick={() => handlePromptPreview(option.value as PromptStyleOption)}
                  >
                    View {option.label}
                  </Button>
                ))}
              </div>
              <div className="mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  className="text-slate-200 hover:text-white border-gray-600 bg-gray-800 hover:bg-gray-600"
                  onClick={() => {
                    setSelectedPrompt('Zero-shot');
                    setIsPromptModalOpen(true);
                    setShowSystemPrompt(true);
                  }}
                >
                  View System Prompt
                </Button>
              </div>
            </div>

            {/* Custom Prompt Section */}
            <div>
              <h4 className="text-md font-medium  text-slate-300 mb-2">Custom Prompt</h4>
              <textarea
                className="w-full p-3 border border-gray-800 bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                rows={4}
                placeholder="Enter your custom prompt here..."
                value={evaluationData.customPrompt || ''}
                onChange={(e) => updateEvaluationData({ customPrompt: e.target.value })}
              />
            </div>
          </div>

          {/* Eval Methods Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Evaluation Methods</h3>
            <p className="text-sm text-slate-300 mb-4">
              Select an evaluation method for iterative refinement:
            </p>
            
            <div className="flex flex-wrap gap-4 mb-4">
              {/* Self-Refine Option */}
              <div className="relative" data-eval-method="self-refine">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="outline"
                        className={`border-2 px-6 py-3 text-slate-200 bg-gray-800 border-gray-600 hover:bg-gray-600 hover:text-white transition-all duration-200 ${
                          selectedEvalMethod === 'SELF-REFINE'
                            ? 'bg-primary/10 border-primary text-primary'
                            : ''
                        }`}
                        onClick={() => {
                          setSelectedEvalMethod(selectedEvalMethod === 'SELF-REFINE' ? null : 'SELF-REFINE');
                          setShowSelfRefineInput(!showSelfRefineInput);
                          setShowCrossRefineInput(false);
                        }}
                      >
                        SELF-REFINE
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent className="bg-gray-900 border-gray-600">
                      <div className="text-white text-sm mb-2 font-medium">Self-Refine Process</div>
                      <div className="bg-gray-800 p-2 rounded text-xs text-slate-300">
                        Initial Claim → Feedback → Refined Claim → Repeat
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                
                {/* Numeric Input for Self-Refine */}
                {showSelfRefineInput && (
                  <div className="absolute top-full left-0 mt-2 bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-lg z-40">
                    <label htmlFor="self-refine-iterations" className="block text-sm text-slate-300 mb-2">Iterations (1-10):</label>
                    <input
                      id="self-refine-iterations"
                      type="number"
                      min="1"
                      max="10"
                      value={selfRefineIterations}
                      onChange={(e) => setSelfRefineIterations(Math.max(1, Math.min(10, parseInt(e.target.value) || 1)))}
                      className="w-20 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                )}
              </div>

              {/* Cross-Refine Option */}
              <div className="relative" data-eval-method="cross-refine">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="outline"
                        className={`border-2 px-6 py-3 text-slate-200 bg-gray-800 border-gray-600 hover:bg-gray-600 hover:text-white transition-all duration-200 ${selectedEvalMethod === 'CROSS-REFINE' ? 'bg-primary/10 border-primary text-primary' : ''}`}
                        onClick={() => {
                          setSelectedEvalMethod(selectedEvalMethod === 'CROSS-REFINE' ? null : 'CROSS-REFINE');
                          setShowCrossRefineInput(!showCrossRefineInput);
                          setShowSelfRefineInput(false);
                        }}
                      >
                        CROSS-REFINE
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent className="bg-gray-900 border-gray-600">
                      <div className="text-white text-sm mb-2 font-medium">Cross-Refine Process</div>
                      <div className="bg-gray-800 p-2 rounded text-xs text-slate-300">
                        Initial Claim (Model A) → Feedback (Model B) → Refined Claim (Model A) → Repeat
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                
                {/* Numeric Input for Cross-Refine */}
                {showCrossRefineInput && (
                  <div className="absolute top-full left-0 mt-2 bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-lg z-40">
                    <label htmlFor="cross-refine-iterations" className="block text-sm text-slate-300 mb-2">Iterations (1-10):</label>
                    <input
                      id="cross-refine-iterations"
                      type="number"
                      min="1"
                      max="10"
                      value={crossRefineIterations}
                      onChange={(e) => setCrossRefineIterations(Math.max(1, Math.min(10, parseInt(e.target.value) || 1)))}
                      className="w-20 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                )}
              </div>
            </div>

            {/* New: Cross-Refine Model Selection (Model B) */}
            {selectedEvalMethod === 'CROSS-REFINE' && (
              <div className="mt-6 mb-8">
                <h3 className="text-lg font-medium text-white mb-3">Cross-Refine Feedback Model (Model B)</h3>
                <p className="text-sm text-slate-300 mb-4">
                  Select a model to generate feedback during cross-refinement. This model cannot be the same as your primary selected model.
                </p>
                <ToggleGroup 
                  type="single" 
                  value={evaluationData.crossRefineModel || ''} // Use null if no model is selected
                  onValueChange={(value) => updateEvaluationData({ crossRefineModel: value ? (value as ModelOption) : null })}
                  className="justify-start flex-wrap"
                >
                  {modelOptions
                    .filter(option => 
                      !evaluationData.selectedModels.includes(option.value as ModelOption)
                    )
                    .map((option) => (
                      <ToggleGroupItem 
                        key={option.value} 
                        value={option.value}
                        variant="outline"
                        className={`border-2 px-1 py-1 font-medium text-slate-200 bg-gray-800 border-gray-600 data-[state=on]:bg-primary/10 data-[state=on]:border-primary data-[state=on]:text-primary min-w-[112px] text-start`}
                      >
                        {option.label}
                      </ToggleGroupItem>
                    ))
                  }
                </ToggleGroup>
              </div>
            )}

            {selectedEvalMethod && (
              <div className="mt-4 p-3 bg-gray-800 rounded-lg border border-gray-600">
                <p className="text-sm text-slate-300">
                  {(() => {
                    const iterationCount = selectedEvalMethod === 'SELF-REFINE' ? selfRefineIterations : crossRefineIterations;
                    const pluralSuffix = iterationCount > 1 ? 's' : '';
                    return (
                      <>
                        <span className="font-medium text-white">{selectedEvalMethod}</span> selected with{' '}
                        <span className="font-medium text-orange-500">{iterationCount}</span>{' '}
                        iteration{pluralSuffix}
                        {selectedEvalMethod === 'CROSS-REFINE' && (
                          <>
                            <span className="text-slate-300"> and feedback model </span>
                            <span className="text-amber-500"> {evaluationData.crossRefineModel}</span>
                          </>
                        )}
                      </>
                    );
                  })()}
                </p>
              </div>
            )}
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
                  <div className="text-sm text-slate-500 flex items-center">
                    {getFileIcon(evaluationData.file.name)}
                    <span>{evaluationData.file.name}</span>
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
                  updateEvaluationData({ file });
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
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-lg font-medium text-white">Evaluation Progress</h3>
                  <span className="text-sm font-medium text-slate-300">{progress}%</span>
                </div>
                
                <Progress value={progress} className="h-3 mb-2" />
                
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-slate-300">{getProgressStatusText()}</span>
                  <div className="flex space-x-2">
                    {progressStatus === 'pending' ? (
                      <Button
                        type="button"
                        onClick={handleStartEvaluation}
                        disabled={
                          evaluationData.selectedModels.length === 0 || 
                          evaluationData.selectedPromptStyles.length === 0 || 
                          !evaluationData.file
                        }
                        className="bg-gray-800 hover:bg-gray-900 text-white"
                      >
                        <Play className="h-4 w-4 mr-1" />
                        Start Evaluation
                      </Button>
                    ) : progressStatus === 'processing' ? (
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
                </div>
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
            <DialogTitle className="text-white">
              {showSystemPrompt ? 'System Prompt' : (selectedPrompt && defaultPrompts[selectedPrompt].title)}
            </DialogTitle>
            <DialogDescription className="text-slate-300">
              {showSystemPrompt ? 'The system prompt that guides the model\'s behavior' : (selectedPrompt && defaultPrompts[selectedPrompt].description)}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 flex-1 overflow-auto">
            <pre className="bg-gray-700 text-slate-200 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono text-sm">
              {showSystemPrompt ? sys_prompt : (selectedPrompt && defaultPrompts[selectedPrompt].template)}
            </pre>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}