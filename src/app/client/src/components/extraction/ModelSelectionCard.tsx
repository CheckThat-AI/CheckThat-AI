import React from 'react';
import { ModelOption, EvaluationData } from '@shared/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";

interface ModelSelectionCardProps {
  readonly extractionData: EvaluationData;
  readonly updateExtractionData: (data: any) => void;
  readonly openaiApiKey: string;
  readonly setOpenaiApiKey: (key: string) => void;
  readonly anthropicApiKey: string;
  readonly setAnthropicApiKey: (key: string) => void;
  readonly geminiApiKey: string;
  readonly setGeminiApiKey: (key: string) => void;
  readonly grokApiKey: string;
  readonly setGrokApiKey: (key: string) => void;
}

const modelGroups = [
  {
    label: "Together AI (Free)",
    models: [
      { value: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free', label: 'Llama 3.3 70B' },
    ]
  },
  {
    label: "OpenAI",
    models: [
      { value: 'gpt-4o-2024-11-20', label: 'GPT-4o' },
      { value: 'gpt-4.1-2025-04-14', label: 'GPT-4.1' },
      { value: 'gpt-4.1-nano-2025-04-14', label: 'GPT-4.1 Nano' },
    ]
  },
  {
    label: "Anthropic",
    models: [
      { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet 4' },
      { value: 'claude-opus-4-20250514', label: 'Claude Opus 4' },
    ]
  },
  {
    label: "Google AI",
    models: [
      { value: 'gemini-2.5-pro-preview-05-06', label: 'Gemini 2.5 Pro' },
      { value: 'gemini-2.5-flash-preview-04-17', label: 'Gemini 2.5 Flash' },
    ]
  },
  {
    label: "xAI",
    models: [
      { value: 'grok-3-latest', label: 'Grok 3 Beta' }
    ]
  }
];

export default function ModelSelectionCard({
  extractionData,
  updateExtractionData,
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
          value={extractionData.selectedModels.length > 0 ? extractionData.selectedModels[0] : ''}
          onValueChange={(value: string) => {
            const selectedModels = value === "" ? [] : [(value as ModelOption)];
            updateExtractionData({ selectedModels });
            // If primary model is also cross-refine model, clear cross-refine model in extractionData
            if (value && extractionData.crossRefineModel && (value as ModelOption) === extractionData.crossRefineModel) {
              updateExtractionData({ crossRefineModel: null });
            }
          }}
        >
          <SelectTrigger className="w-[300px] bg-cardbg-900 text-white border-slate-600 max-w-xl
          focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none 
          data-[state=open]:ring-0 data-[state=open]:outline-none">
            <SelectValue placeholder="Select model" />
          </SelectTrigger>
          <SelectContent className="bg-cardbg-900 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none max-h-[30vh] overflow-y-auto scrollbar-hide">
            {modelGroups.map((group) => (
              <SelectGroup key={group.label}>
                <SelectLabel className="text-slate-400 font-medium px-2 py-1.5">
                  {group.label}
                </SelectLabel>
                {group.models.map((model) => (
                  <SelectItem key={model.value} value={model.value} className="text-white focus:bg-slate-800 focus:text-white">
                    <span className="font-medium">{model.label}</span>
                  </SelectItem>
                ))}
              </SelectGroup>
            ))}
          </SelectContent>
        </Select>

        {/* API Key Input - appears when paid model is selected */}
        {extractionData.selectedModels.length > 0 && extractionData.selectedModels[0] !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
          <div className="flex items-center space-x-2 max-w-fit px-4">
            <label className="text-sm text-slate-300 whitespace-nowrap">
              {(() => {
                const selectedModel = extractionData.selectedModels[0];
                if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                  return 'OpenAI API Key:';
                } else if (['claude-sonnet-4-20250514', 'claude-opus-4-20250514'].includes(selectedModel)) {
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
                const selectedModel = extractionData.selectedModels[0];
                if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                  return openaiApiKey;
                } else if (['claude-sonnet-4-20250514', 'claude-opus-4-20250514'].includes(selectedModel)) {
                  return anthropicApiKey;
                } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(selectedModel)) {
                  return geminiApiKey;
                } else if (['grok-3-latest'].includes(selectedModel)) {
                  return grokApiKey;
                }
                return '';
              })()}
              onChange={(e) => {
                const selectedModel = extractionData.selectedModels[0];
                if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                  setOpenaiApiKey(e.target.value);
                } else if (['claude-sonnet-4-20250514', 'claude-opus-4-20250514'].includes(selectedModel)) {
                  setAnthropicApiKey(e.target.value);
                } else if (['gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-04-17'].includes(selectedModel)) {
                  setGeminiApiKey(e.target.value);
                } else if (['grok-3-latest'].includes(selectedModel)) {
                  setGrokApiKey(e.target.value);
                }
              }}
              placeholder={(() => {
                const selectedModel = extractionData.selectedModels[0];
                if (['gpt-4o-2024-11-20', 'gpt-4.1-2025-04-14', 'gpt-4.1-nano-2025-04-14'].includes(selectedModel)) {
                  return 'sk-...';
                } else if (['claude-sonnet-4-20250514', 'claude-opus-4-20250514'].includes(selectedModel)) {
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
      {extractionData.selectedModels.length > 0 && extractionData.selectedModels[0] !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
        <div className="mt-3 p-3 bg-zinc-950 rounded-lg border-b border-gray-600 max-w-fit">
          <p className="text-xs text-slate-400">
            🔒 API keys are transmitted securely and are not stored. They're only used for your current evaluation session.
          </p>
        </div>
      )}
    </div>
  );
} 