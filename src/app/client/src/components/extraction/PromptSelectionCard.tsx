import React from 'react';
import { Button } from '@/components/ui/button';
import { PromptStyleOption } from '@shared/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface PromptSelectionCardProps {
  readonly extractionData: any;
  readonly updateExtractionData: (data: any) => void;
  readonly isCustomPromptSelected: boolean;
  readonly setIsCustomPromptSelected: (selected: boolean) => void;
  readonly setSelectedPrompt: (prompt: PromptStyleOption) => void;
  readonly setIsPromptModalOpen: (open: boolean) => void;
  readonly setShowSystemPrompt: (show: boolean) => void;
}

const promptStyleOptions = [
  { value: 'Zero-shot', label: 'Zero-shot' },
  { value: 'Few-shot', label: 'Few-shot' },
  { value: 'Zero-shot-CoT', label: 'Zero-shot-CoT' },
  { value: 'Few-shot-CoT', label: 'Few-shot-CoT' }
];

export default function PromptSelectionCard({
  extractionData,
  updateExtractionData,
  isCustomPromptSelected,
  setIsCustomPromptSelected,
  setSelectedPrompt,
  setIsPromptModalOpen,
  setShowSystemPrompt
}: PromptSelectionCardProps) {
  return (
    <div className="mb-8">
      <h3 className="text-lg font-medium text-white mb-3">Prompt Styles</h3>
      <p className="text-sm text-slate-300 mb-4">
        Select a prompt style for evaluation:
      </p>
      
      <div className="flex items-center space-x-4 mb-4">
        <Select 
          value={(() => {
            if (isCustomPromptSelected) return 'Custom';
            if (extractionData.selectedPromptStyles.length > 0) return extractionData.selectedPromptStyles[0];
            return '';
          })()}
          onValueChange={(value) => {
            if (value === 'Custom') {
              setIsCustomPromptSelected(true);
              updateExtractionData({ selectedPromptStyles: [] });
            } else {
              setIsCustomPromptSelected(false);
              const newPromptStyle = value as PromptStyleOption;
              updateExtractionData({ selectedPromptStyles: [newPromptStyle] });
            }
          }}
        >
          <SelectTrigger className="w-[300px] bg-cardbg-900 text-white border-slate-800 
          focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none 
          data-[state=open]:ring-0 data-[state=open]:outline-none">
            <SelectValue placeholder="Select prompt" />
          </SelectTrigger>
          <SelectContent className="bg-cardbg-900 border-slate-600 
          focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
            {promptStyleOptions.map((option) => (
              <SelectItem key={option.value} value={option.value} className="text-white focus:bg-slate-800 focus:text-white">
                <span className="font-medium">{option.label}</span>
              </SelectItem>
            ))}
            <SelectItem value="Custom" className="text-white focus:bg-slate-800 focus:text-white">
              <span className="font-medium">Custom</span>
            </SelectItem>
          </SelectContent>
        </Select>

        {/* View Prompt Button - appears when default prompt is selected */}
        {extractionData.selectedPromptStyles.length > 0 && !isCustomPromptSelected && (
          <Button
            variant="outline"
            size="sm"
            className="bg-cardbg-900 hover:bg-zinc-900 hover:text-white text-white border-slate-800"
            onClick={() => {
              setSelectedPrompt(extractionData.selectedPromptStyles[0]);
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
            className="w-full p-3 text-slate-300 bg-cardbg-900 border border-slate-800 rounded-lg 
            focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:border-transparent"
            rows={4}
            placeholder="Enter your custom prompt here..."
            value={extractionData.customPrompt ?? ''}
            onChange={(e) => updateExtractionData({ customPrompt: e.target.value })}
          />
        </div>
      )}
    </div>
  );
} 