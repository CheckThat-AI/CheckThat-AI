import React from 'react';
import { ModelOption, EvaluationData } from '@shared/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ModelSelectionCardProps {
  readonly evaluationData: EvaluationData;
  readonly updateEvaluationData: (data: any) => void;
  readonly openaiApiKey: string;
  readonly setOpenaiApiKey: (key: string) => void;
  readonly anthropicApiKey: string;
  readonly setAnthropicApiKey: (key: string) => void;
  readonly geminiApiKey: string;
  readonly setGeminiApiKey: (key: string) => void;
  readonly grokApiKey: string;
  readonly setGrokApiKey: (key: string) => void;
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

export default function ModelSelectionCard({
  evaluationData,
  updateEvaluationData,
  openaiApiKey,
  setOpenaiApiKey,
  anthropicApiKey,
  setAnthropicApiKey,
  geminiApiKey,
  setGeminiApiKey,
  grokApiKey,
  setGrokApiKey
}: ModelSelectionCardProps) {
  return (
    <div className="mb-8">
      <h3 className="text-lg font-medium text-white mb-3">Model</h3>
      <div className="flex items-center space-x-">
        <Select 
          value={evaluationData.selectedModels.length > 0 ? evaluationData.selectedModels[0] : ''}
          onValueChange={(value: string) => {
            const selectedModels = value === "" ? [] : [(value as ModelOption)];
            updateEvaluationData({ selectedModels });
            // If primary model is also cross-refine model, clear cross-refine model in evaluationData
            if (value && evaluationData.crossRefineModel && (value as ModelOption) === evaluationData.crossRefineModel) {
              updateEvaluationData({ crossRefineModel: null });
            }
          }}
        >
          <SelectTrigger className="w-[300px] bg-cardbg-900 text-white border-slate-600 max-w-fit
          focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none 
          data-[state=open]:ring-0 data-[state=open]:outline-none">
            <SelectValue placeholder="Select model" />
          </SelectTrigger>
          <SelectContent className="bg-cardbg-900 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
            {modelOptions.map((option) => (
              <SelectItem key={option.value} value={option.value} className="text-white focus:bg-slate-800 focus:text-white">
                <span className="font-medium">{option.label}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* API Key Input - appears when paid model is selected */}
        {evaluationData.selectedModels.length > 0 && evaluationData.selectedModels[0] !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
          <div className="flex items-center space-x-2 max-w-fit px-4">
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
              className="w-[300px] px-2 py-2 bg-cardbg-900 border border-gray-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:border-transparent"
            />
          </div>
        )}
      </div>

      {/* Security Notice - appears when API key is shown */}
      {evaluationData.selectedModels.length > 0 && evaluationData.selectedModels[0] !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
        <div className="mt-3 p-3 bg-zinc-950 rounded-lg border-b border-gray-600 max-w-fit">
          <p className="text-xs text-slate-400">
            🔒 API keys are transmitted securely and are not stored. They're only used for your current evaluation session.
          </p>
        </div>
      )}
    </div>
  );
} 