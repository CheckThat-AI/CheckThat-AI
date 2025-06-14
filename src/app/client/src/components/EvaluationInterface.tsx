import React, { useEffect, useRef, useState } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { PromptStyleOption, FieldMapping } from '@shared/types';
import EvaluationResultsComponent from './EvaluationResults';
import FieldMappingModal from './FieldMappingModal';
import { defaultPrompts, sys_prompt } from '@shared/prompts';
import { useToast } from '@/hooks/use-toast';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import './scrollbar-hide.css';

// Import modular components
import {
  SystemMessageCard,
  ModelSelectionCard,
  PromptSelectionCard,
  EvaluationMethodsCard,
  EvaluationMetricsCard,
  FileUploadCard,
  EvaluationProgressCard
} from './evaluation/index';

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
  } = useAppContext();
  
  const resultsRef = useRef<HTMLDivElement>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<PromptStyleOption | null>(null);
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
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

  // --- Output Log Modal State and Logic ---
  const [showLogModal, setShowLogModal] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  // Auto-scroll log modal to bottom
  useEffect(() => {
    if (showLogModal && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logMessages, showLogModal]);

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

  // Helper to check if API key is missing for a provider
  const checkMissingApiKey = (provider: string): string | null => {
    const keyMap = {
      openai: openaiApiKey,
      anthropic: anthropicApiKey,
      gemini: geminiApiKey,
      grok: grokApiKey
    };
    return keyMap[provider as keyof typeof keyMap]?.trim() ? null : provider;
  };

  // Check main model API keys
  const validateMainModelKeys = (): string[] => {
    const selectedProviders = getSelectedModelProviders();
    return Array.from(selectedProviders)
      .map(provider => checkMissingApiKey(provider as string))
      .filter((provider): provider is string => Boolean(provider))
      .map(provider => provider.charAt(0).toUpperCase() + provider.slice(1));
  };

  // Check Cross-Refine feedback model API keys
  const validateFeedbackModelKeys = (): string[] => {
    if (selectedEvalMethod !== 'CROSS-REFINE' || 
        !evaluationData.crossRefineModel || 
        evaluationData.crossRefineModel === 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' ||
        !evaluationData.selectedModels.length ||
        getModelProvider(evaluationData.crossRefineModel) === getModelProvider(evaluationData.selectedModels[0])) {
      return [];
    }

    const feedbackProvider = getModelProvider(evaluationData.crossRefineModel);
    const missingKey = checkMissingApiKey(feedbackProvider);
    return missingKey ? [`${missingKey.charAt(0).toUpperCase() + missingKey.slice(1)} (for feedback model)`] : [];
  };

  // Validate API keys before starting evaluation
  const validateApiKeys = () => {
    const missingKeys = [...validateMainModelKeys(), ...validateFeedbackModelKeys()];
    
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

                {/* Scrollable Middle Section */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 min-h-0">
          <div className="max-w-6xl w-full mx-auto space-y-4">
          {/* System Message */}
          <SystemMessageCard />

            {/* Claim Evaluation Card */}
          <Card className="border-slate-800 rounded-md shadow-2xl 
          bg-gradient-to-r from-zinc-950 to-zinc-950 via-cardbg-900">
            <CardContent className="p-6">
              <h2 className="text-xl text-white font-semibold mb-6">Claim Evaluation</h2>
          
          {/* Model Selection Section */}
              <ModelSelectionCard
                evaluationData={evaluationData}
                updateEvaluationData={updateEvaluationData}
                openaiApiKey={openaiApiKey}
                setOpenaiApiKey={setOpenaiApiKey}
                anthropicApiKey={anthropicApiKey}
                setAnthropicApiKey={setAnthropicApiKey}
                geminiApiKey={geminiApiKey}
                setGeminiApiKey={setGeminiApiKey}
                grokApiKey={grokApiKey}
                setGrokApiKey={setGrokApiKey}
              />
          
          {/* Prompt Style Selection Section */}
              <PromptSelectionCard
                evaluationData={evaluationData}
                updateEvaluationData={updateEvaluationData}
                isCustomPromptSelected={isCustomPromptSelected}
                setIsCustomPromptSelected={setIsCustomPromptSelected}
                setSelectedPrompt={setSelectedPrompt}
                setIsPromptModalOpen={setIsPromptModalOpen}
                setShowSystemPrompt={setShowSystemPrompt}
              />

              {/* Evaluation Methods Section */}
              <EvaluationMethodsCard
                selectedEvalMethod={selectedEvalMethod}
                setSelectedEvalMethod={setSelectedEvalMethod}
                selfRefineIterations={selfRefineIterations}
                setSelfRefineIterations={setSelfRefineIterations}
                crossRefineIterations={crossRefineIterations}
                setCrossRefineIterations={setCrossRefineIterations}
                evaluationData={evaluationData}
                updateEvaluationData={updateEvaluationData}
                setSelectedMethodInfo={setSelectedMethodInfo}
                setShowEvalMethodInfo={setShowEvalMethodInfo}
                getModelProvider={getModelProvider}
                openaiApiKey={openaiApiKey}
                setOpenaiApiKey={setOpenaiApiKey}
                anthropicApiKey={anthropicApiKey}
                setAnthropicApiKey={setAnthropicApiKey}
                geminiApiKey={geminiApiKey}
                setGeminiApiKey={setGeminiApiKey}
                grokApiKey={grokApiKey}
                setGrokApiKey={setGrokApiKey}
              />

              {/* Evaluation Metrics Section */}
              <EvaluationMetricsCard
                selectedEvalMetric={selectedEvalMetric}
                setSelectedEvalMetric={setSelectedEvalMetric}
                updateEvaluationData={updateEvaluationData}
              />

          {/* File Upload Section */}
              <FileUploadCard
                evaluationData={evaluationData}
                updateEvaluationData={updateEvaluationData}
                fieldMapping={fieldMapping}
                setShowFieldMappingModal={setShowFieldMappingModal}
              />
          
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
          <EvaluationProgressCard
            progressStatus={progressStatus}
            progress={progress}
            evaluationData={evaluationData}
            handleStartEvaluation={handleStartEvaluation}
            stopEvaluation={stopEvaluation}
            setShowLogModal={setShowLogModal}
            getProgressStatusText={getProgressStatusText}
          />
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
          bg-gradient-to-r from-black via-zinc-950 to-cardbg-900 
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
                className="bg-gradient-to-r from-zinc-950 to-zinc-950 via-cardbg-900 
                hover:bg-zinc-950 hover:text-white text-white border-slate-800"
                onClick={() => setShowSystemPrompt(!showSystemPrompt)}
              >
                {showSystemPrompt ? 'View Prompt' : 'View System Prompt'}
              </Button>
            </div>
          </DialogHeader>
          <div className="mt-4 flex-1 overflow-auto">
            <pre className="bg-gradient-to-r from-zinc-950 to-zinc-950 via-cardbg-900 text-slate-200 p-4 
            border border-slate-800 shadow-xl rounded-lg overflow-x-auto whitespace-pre-wrap font-mono text-sm">
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
                    {evalMethodDescriptions[selectedMethodInfo].benefits.map((benefit) => (
                      <li key={benefit} className="text-sm text-slate-300 flex items-center">
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