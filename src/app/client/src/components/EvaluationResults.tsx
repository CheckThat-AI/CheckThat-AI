import React from 'react';
import { 
  Card, 
  CardContent 
} from '@/components/ui/card';
import { EvaluationResults, ModelOption, PromptStyleOption, MeteorScore } from '@shared/types';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { motion } from 'framer-motion';

interface EvaluationResultsProps {
  results: EvaluationResults;
  selectedModels: ModelOption[];
  selectedPromptStyles: PromptStyleOption[];
}

// Helper function to format model name for display
const formatModelName = (model: string): string => {
  switch (model) {
    case 'model1':
      return 'GPT-4';
    case 'model2':
      return 'LLaMA';
    case 'model3':
      return 'Claude';
    default:
      return model;
  }
};

// Helper function to format prompt style for display
const formatStyleName = (style: string): string => {
  switch (style) {
    case 'style1':
      return 'Standard';
    case 'style2':
      return 'Detailed';
    case 'style3':
      return 'Concise';
    default:
      return style;
  }
};

const EvaluationResultsComponent: React.FC<EvaluationResultsProps> = ({ 
  results, 
  selectedModels, 
  selectedPromptStyles 
}) => {
  // Single selection case
  const isSingleSelection = selectedModels.length === 1 && selectedPromptStyles.length === 1;
  
  if (isSingleSelection) {
    const singleScore = results.scores.find(
      score => score.model === selectedModels[0] && score.promptStyle === selectedPromptStyles[0]
    );
    
    if (!singleScore) return null;
    
    // Format the score as a percentage
    const scorePercentage = Math.round(singleScore.score * 100);
    
    return (
      <div className="mt-8">
        <h3 className="text-lg font-medium text-slate-800 mb-4">Evaluation Results</h3>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-100"
        >
          <div className="text-center">
            <h4 className="text-xl font-medium text-gray-700">
              METEOR Score 
            </h4>
            <p className="text-sm text-gray-500 mb-4">
              {formatModelName(singleScore.model)} using {formatStyleName(singleScore.promptStyle)} prompt style
            </p>
            
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="flex justify-center items-center"
            >
              <div className="relative w-36 h-36 flex items-center justify-center bg-white rounded-full shadow-md border-4 border-blue-100">
                <div className="absolute inset-0 rounded-full">
                  <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full">
                    <motion.circle
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: singleScore.score }}
                      transition={{ delay: 0.5, duration: 1.5, ease: "easeOut" }}
                      stroke="url(#blue-gradient)"
                      strokeWidth="8"
                      fill="transparent"
                      r="44"
                      cx="50"
                      cy="50"
                      strokeLinecap="round"
                      strokeDasharray="276.46"
                      strokeDashoffset="0"
                      transform="rotate(-90 50 50)"
                    />
                    <defs>
                      <linearGradient id="blue-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#8b5cf6" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8, duration: 0.5 }}
                  className="relative text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-violet-500"
                >
                  {scorePercentage}%
                </motion.div>
              </div>
            </motion.div>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1, duration: 0.5 }}
              className="mt-6 text-sm text-gray-600"
            >
              {scorePercentage >= 85 ? 'Excellent result!' :
               scorePercentage >= 70 ? 'Good result!' :
               scorePercentage >= 50 ? 'Average result.' :
               'Below average result.'}
            </motion.p>
          </div>
        </motion.div>
      </div>
    );
  }
  
  // Multiple selection case - show chart
  // Transform data for chart display
  const chartData = selectedPromptStyles.map(style => {
    const data: any = { name: formatStyleName(style) };
    
    selectedModels.forEach(model => {
      const score = results.scores.find(s => s.model === model && s.promptStyle === style);
      data[formatModelName(model)] = score ? Math.round(score.score * 100) : 0;
    });
    
    return data;
  });
  
  const chartColors = ['#3b82f6', '#8b5cf6', '#ef4444', '#10b981', '#f59e0b'];
  
  return (
    <div className="mt-8">
      <h3 className="text-lg font-medium text-slate-800 mb-4">Evaluation Results</h3>
      <Card>
        <CardContent className="pt-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full"
            style={{ height: 400 }}
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: 'METEOR Score (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value) => [`${value}%`, 'Score']} />
                <Legend />
                {selectedModels.map((model, index) => (
                  <Bar 
                    key={model} 
                    dataKey={formatModelName(model)} 
                    fill={chartColors[index % chartColors.length]} 
                    animationDuration={1500}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
          
          <div className="mt-4 text-sm text-gray-500 text-center">
            Chart showing METEOR scores for each model across different prompt styles
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EvaluationResultsComponent;