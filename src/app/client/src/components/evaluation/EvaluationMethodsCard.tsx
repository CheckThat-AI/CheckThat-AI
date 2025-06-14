import React from 'react';
import { Button } from '@/components/ui/button';
import { ModelOption, EvaluationData } from '@shared/types';
import { InfoIcon } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface EvaluationMethodsCardProps {
  selectedEvalMethod: 'SELF-REFINE' | 'CROSS-REFINE' | null;
  setSelectedEvalMethod: (method: 'SELF-REFINE' | 'CROSS-REFINE' | null) => void;
  selfRefineIterations: number;
  setSelfRefineIterations: (iterations: number) => void;
  crossRefineIterations: number;
  setCrossRefineIterations: (iterations: number) => void;
  evaluationData: EvaluationData;
  updateEvaluationData: (data: any) => void;
  setSelectedMethodInfo: (method: 'SELF-REFINE' | 'CROSS-REFINE' | null) => void;
  setShowEvalMethodInfo: (show: boolean) => void;
  getModelProvider: (model: string) => string;
  openaiApiKey: string;
  setOpenaiApiKey: (key: string) => void;
  anthropicApiKey: string;
  setAnthropicApiKey: (key: string) => void;
  geminiApiKey: string;
  setGeminiApiKey: (key: string) => void;
  grokApiKey: string;
  setGrokApiKey: (key: string) => void;
}

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

export default function EvaluationMethodsCard({
  selectedEvalMethod,
  setSelectedEvalMethod,
  selfRefineIterations,
  setSelfRefineIterations,
  crossRefineIterations,
  setCrossRefineIterations,
  evaluationData,
  updateEvaluationData,
  setSelectedMethodInfo,
  setShowEvalMethodInfo,
  getModelProvider,
  openaiApiKey,
  setOpenaiApiKey,
  anthropicApiKey,
  setAnthropicApiKey,
  geminiApiKey,
  setGeminiApiKey,
  grokApiKey,
  setGrokApiKey
}: EvaluationMethodsCardProps) {
  return (
    <div className="mb-8">
      <h3 className="text-lg font-medium text-white mb-3">Iterative Refinement Methods (Optional)</h3>
      <div className="flex items-center space-x-4">
        <Select
          value={selectedEvalMethod || 'STANDARD'}
          onValueChange={(value) => {
            const newValue = value === 'STANDARD' ? null : value as 'SELF-REFINE' | 'CROSS-REFINE';
            setSelectedEvalMethod(newValue);
          }}
        >
          <SelectTrigger className="w-[400px] max-w-fit bg-cardbg-900 text-white border-slate-800 
          focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
            <SelectValue placeholder="Select evaluation method" />
          </SelectTrigger>
          <SelectContent className="bg-cardbg-900 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
            <SelectItem value="STANDARD" className="text-white focus:bg-slate-800 focus:text-white">
              <span className="font-medium">Standard (No Refinement)</span>
            </SelectItem>
            <SelectItem value="SELF-REFINE" className="text-white focus:bg-slate-800 focus:text-white">
              <span className="font-medium">SELF-REFINE</span>
            </SelectItem>
            <SelectItem value="CROSS-REFINE" className="text-white focus:bg-slate-800 focus:text-white">
              <span className="font-medium">CROSS-REFINE</span>
            </SelectItem>
          </SelectContent>
        </Select>

        {/* Info Button - appears when refinement method is selected */}
        {selectedEvalMethod && (
          <Button
            variant="outline"
            size="sm"
            className="bg-cardbg-900 hover:bg-zinc-900 hover:text-white text-white border-slate-800 px-2 py-1"
            onClick={() => {
              setSelectedMethodInfo(selectedEvalMethod);
              setShowEvalMethodInfo(true);
            }}
          >
            <InfoIcon className="h-4 w-4" />
          </Button>
        )}

        {/* Iteration Selector - appears when refinement method is selected */}
        {selectedEvalMethod && (
          <div className="flex items-center space-x-2 ">
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
                className="w-16 px-2 py-1 bg-cardbg-900 border border-slate-800 rounded text-white text-sm 
                focus:outline-none focus:ring-2 focus:ring-emerald-700 text-center"
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
              onValueChange={(value: string) => {
                updateEvaluationData({ crossRefineModel: value === "" ? null : (value as ModelOption) });
              }}
            >
              <SelectTrigger className="w-[180px] bg-cardbg-900 text-white border-slate-800 
              focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none 
              data-[state=open]:ring-0 data-[state=open]:outline-none"
              >
                <SelectValue placeholder="Select Model B" />
              </SelectTrigger>
              <SelectContent className="bg-cardbg-900 border-slate-800
              focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none"
              >
                {modelOptions
                  .filter(option => 
                    !evaluationData.selectedModels.includes(option.value as ModelOption)
                  )
                  .map((option) => (
                    <SelectItem key={option.value} value={option.value} className="text-white focus:bg-slate-800 focus:text-white">
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
              <div className="flex items-center space-x-2 px-3">
                <label className="text-sm text-slate-300 whitespace-nowra">
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
                  className="w-[200px] px-3 py-2 bg-cardbg-900 border border-slate-800 rounded-lg text-white placeholder-slate-400 
                  focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:border-transparent"
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 