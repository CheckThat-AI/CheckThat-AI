import React, { useEffect, useRef } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { ModelOption, PromptStyleOption } from '@shared/types';
import { Play } from 'lucide-react';
import EvaluationResultsComponent from './EvaluationResults';
import { motion } from 'framer-motion';

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
  
  const modelOptions = [
    { value: 'Llama', label: 'Llama' },
    { value: 'OpenAI', label: 'OpenAI' },
    { value: 'Gemini', label: 'Gemini' },
    { value: 'Grok', label: 'Grok' }
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

  return (
    <div>
      {/* Animated Evaluation Mode Text */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg"
      >
        <p className="text-blue-800 text-center">
          This is the evaluation mode interface for batch-processing large datasets. If you wish to extract claims from a single source, please switch back to the Chat mode.
        </p>
      </motion.div>

      <Card className="bg-white">
        <CardContent className="p-6">
          <h2 className="text-xl font-semibold mb-6">Claim Evaluation</h2>
          
          {/* Model Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-slate-800 mb-3">Models</h3>
            <p className="text-sm text-slate-600 mb-4">
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
                  className="border-2 px-6 py-3 data-[state=on]:bg-primary/10 data-[state=on]:border-primary data-[state=on]:text-primary font-medium"
                >
                  {option.label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>
          
          {/* Prompt Style Selection Section */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-slate-800 mb-3">Prompt Styles</h3>
            
            {/* Default Prompts Section */}
            <div className="mb-6">
              <h4 className="text-md font-medium text-slate-700 mb-2">Default Prompts</h4>
              <div className="flex flex-wrap gap-2 mb-3">
                {promptStyleOptions.map((option) => (
                  <div key={option.value} className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      className={`border-2 px-4 py-2 ${
                        evaluationData.selectedPromptStyles.includes(option.value as PromptStyleOption)
                          ? 'bg-primary/10 border-primary text-primary'
                          : 'border-slate-200'
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
                      className="text-slate-500 hover:text-primary"
                      onClick={() => {
                        // TODO: Implement preview functionality
                        alert(`Preview of ${option.label} prompt`);
                      }}
                    >
                      View
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Custom Prompt Section */}
            <div>
              <h4 className="text-md font-medium text-slate-700 mb-2">Custom Prompt</h4>
              <textarea
                className="w-full p-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                rows={4}
                placeholder="Enter your custom prompt here..."
                value={evaluationData.customPrompt || ''}
                onChange={(e) => updateEvaluationData({ customPrompt: e.target.value })}
              />
            </div>
          </div>
          
          {/* Progress Tracking */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-medium text-slate-800">Evaluation Progress</h3>
              <span className="text-sm font-medium text-slate-600">{progress}%</span>
            </div>
            
            <Progress value={progress} className="h-3 mb-2" />
            
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-slate-600">{getProgressStatusText()}</span>
              <Button
                type="button"
                onClick={() => startEvaluation()}
                disabled={evaluationData.selectedModels.length === 0 || evaluationData.selectedPromptStyles.length === 0 || progressStatus === 'processing'}
                className="bg-blue-600 hover:bg-blue-700 text-white"
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
    </div>
  );
}