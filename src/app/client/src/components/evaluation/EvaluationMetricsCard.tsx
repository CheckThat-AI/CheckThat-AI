import React from 'react';
import { BarChart3Icon } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface EvaluationMetricsCardProps {
  readonly selectedEvalMetric: string;
  readonly setSelectedEvalMetric: (metric: string) => void;
  readonly updateEvaluationData: (data: any) => void;
}

const evalMetricOptions: { value: string; label: string; description: string; category: string }[] = [
  // Reference-less metrics (can work without ground truth)
  { value: 'bleu', label: 'BLEU', description: 'Bilingual Evaluation Understudy for text similarity', category: 'Reference-less' },
  { value: 'rouge', label: 'ROUGE', description: 'Recall-Oriented Understudy for Gisting Evaluation', category: 'Reference-less' },
  { value: 'meteor', label: 'METEOR', description: 'Metric for Evaluation of Translation with Explicit ORdering', category: 'Reference-less' },
  { value: 'bertscore', label: 'BERTScore', description: 'Semantic similarity using BERT embeddings', category: 'Reference-less' },
  { value: 'cosine-similarity', label: 'Cosine Similarity', description: 'Cosine similarity between embeddings', category: 'Reference-less' }
];

export default function EvaluationMetricsCard({
  selectedEvalMetric,
  setSelectedEvalMetric,
  updateEvaluationData
}: EvaluationMetricsCardProps) {
  return (
    <div className="mb-8">
      <h3 className="text-lg font-medium text-white mb-3">Eval Metrics</h3>
      <Select
        value={selectedEvalMetric}
        onValueChange={(value) => {
          setSelectedEvalMetric(value);
          updateEvaluationData({ evalMetric: value });
        }}
      >
        <SelectTrigger className="w-[450px] max-w-fit bg-cardbg-900 text-white border-slate-800 
        focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none 
        data-[state=open]:ring-0 data-[state=open]:outline-none"
        >
          <BarChart3Icon className="h-4 w-4 mr-2 flex-shrink-0 text-yellow-500" />
          <SelectValue placeholder="Select evaluation metric" />
        </SelectTrigger>
        <SelectContent 
          side="right" 
          align="start"
          className="bg-cardbg-900 border-slate-800 
          focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none 
          min-w-[100px] max-w-[450px] max-h-[300px] overflow-y-auto"
        >
          {evalMetricOptions.map((option) => (
            <SelectItem 
              key={option.value} 
              value={option.value} 
              className="text-white focus:bg-slate-800 focus:text-white pl-8 pr-3 py-3 min-h-[60px] bg-cardbg-900"
            >
              <div className="flex flex-col text-white max-w-fit">
                <span className="font-medium">{option.label}</span>
                <span className="text-xs text-slate-400 font-normal leading-tight mt-1 break-words">{option.description}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
} 