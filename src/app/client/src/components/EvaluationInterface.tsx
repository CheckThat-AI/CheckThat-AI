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
import { defaultPrompts } from '@shared/prompts';
import { sys_prompt } from '@shared/prompts';
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
    evaluationResults
  } = useAppContext();
  
  const resultsRef = useRef<HTMLDivElement>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<PromptStyleOption | null>(null);
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const { toast } = useToast();
  
  const modelOptions = [
    { value: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre', label: 'Llama 3.3 70B' },
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
        return progress < 30 ? 'Loading data...' : 
              progress < 60 ? 'Processing claims...' : 
              progress < 90 ? 'Generating results...' : 
              'Finalizing evaluation...';
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

  return (
    <div>
      {/* Animated Evaluation Mode Text */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-6 p-4 bg-gray-800 border-0 shadow-sm border-blue-200 rounded-lg mt-8"
      >
        <p className="text-slate-300 text-center">
          This is the evaluation mode interface for batch-processing large datasets. If you wish to extract claims from a single source, please switch back to the Chat mode.
        </p>
      </motion.div>

      <Card className="mb-4 bg-gray-700 border-solid border-gray-700 shadow-lg flex flex-col max-w-6xl w-full mx-auto">
        <CardContent className="p-6 bg-gray-700 rounded-lg">
          <h2 className="text-xl text-white font-semibold mb-6">Claim Evaluation</h2>
          
          {/* Model Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Models</h3>
            <p className="text-sm text-slate-300 mb-4">
              Select one or more models to use for claim normalization:
            </p>
            
            <ToggleGroup 
              type="multiple" 
              value={evaluationData.selectedModels}
              onValueChange={(value) => updateEvaluationData({ selectedModels: value as ModelOption[] })}
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
          
          {/* Prompt Style Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-white mb-3">Prompt Styles</h3>
            
            {/* Default Prompts Section */}
            <div className="mb-6">
              <h4 className="text-md font-medium text-slate-300 mb-2">Default Prompts</h4>
              <div className="flex flex-wrap gap-2 mb-3">
                {promptStyleOptions.map((option) => (
                  <div key={option.value} className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      className={`border-2 px-4 py-2 text-slate-200 bg-gray-800 border-gray-600 hover:bg-gray-600 hover:text-white ${
                        evaluationData.selectedPromptStyles.includes(option.value as PromptStyleOption)
                          ? 'bg-primary/10 border-primary text-primary'
                          : ''
                      }`}
                      onClick={() => {
                        const newStyles = evaluationData.selectedPromptStyles.includes(option.value as PromptStyleOption)
                          ? evaluationData.selectedPromptStyles.filter(style => style !== option.value)
                          : [...evaluationData.selectedPromptStyles, option.value as PromptStyleOption];
                        updateEvaluationData({ selectedPromptStyles: newStyles });
                      }}
                    >
                      {option.label}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-slate-400 hover:text-white hover:bg-gray-700"
                      onClick={() => handlePromptPreview(option.value as PromptStyleOption)}
                    >
                      View
                    </Button>
                  </div>
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
                className="w-full p-3 border bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                rows={4}
                placeholder="Enter your custom prompt here..."
                value={evaluationData.customPrompt || ''}
                onChange={(e) => updateEvaluationData({ customPrompt: e.target.value })}
              />
            </div>

            {/* File Upload Section */}
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
                accept=".csv,.json,.jsonl,.txt,text/csv,application/json,application/x-jsonlines,text/plain"
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
          
          {/* Progress Tracking */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-medium text-white">Evaluation Progress</h3>
              <span className="text-sm font-medium text-slate-300">{progress}%</span>
            </div>
            
            <Progress value={progress} className="h-3 mb-2" />
            
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-slate-300">{getProgressStatusText()}</span>
              <Button
                type="button"
                onClick={() => startEvaluation()}
                disabled={evaluationData.selectedModels.length === 0 || evaluationData.selectedPromptStyles.length === 0 || progressStatus === 'processing'}
                className="bg-gray-800 hover:bg-gray-900 text-white"
              >
                <Play className="h-4 w-4 mr-1" />
                Start Evaluation
              </Button>
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

      {/* Prompt Preview Modal */}
      <Dialog open={isPromptModalOpen} onOpenChange={(open) => {
        setIsPromptModalOpen(open);
        if (!open) {
          setShowSystemPrompt(false);
        }
      }}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col bg-gray-800 text-slate-200">
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