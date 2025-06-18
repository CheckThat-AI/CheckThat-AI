import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Play, PauseIcon, RotateCcw } from 'lucide-react';
import { motion } from 'framer-motion';

interface ExtractionProgressCardProps {
  readonly progressStatus: 'pending' | 'processing' | 'completed' | 'error';
  readonly progress: number;
  readonly extractionData: any;
  readonly handleStartExtraction: () => void;
  readonly stopExtraction: () => void;
  readonly setShowLogModal: (show: boolean) => void;
  readonly getProgressStatusText: () => string;
}

export default function ExtractionProgressCard({
  progressStatus,
  progress,
  extractionData,
  handleStartExtraction,
  stopExtraction,
  setShowLogModal,
  getProgressStatusText
}: ExtractionProgressCardProps) {
  return (
    <Card className="bg-gradient-to-l from-zinc-950 to-zinc-950 via-cardbg-900 border border-slate-800 shadow-2xl">
      <CardContent className="p-6 rounded-md">
        {progressStatus === 'pending' ? (
          /* Initial state - Just the start button */
          <div className="flex flex-col items-center space-y-4">
            <h3 className="text-lg font-medium text-white">Ready to Evaluate</h3>
            <p className="text-sm text-slate-300 text-center">
              Click the button below to start your batch extraction
            </p>
            <Button
              type="button"
              onClick={handleStartExtraction}
              disabled={
                extractionData.selectedModels.length === 0 || 
                extractionData.selectedPromptStyles.length === 0 || 
                !extractionData.file
              }
              className="bg-primary hover:bg-primary/90 text-white px-8 py-3 text-lg"
            >
              <Play className="h-5 w-5 mr-2" />
              Start Extraction
            </Button>
          </div>
        ) : (
          /* Progress state - Animated progress bar and controls */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          >
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-medium text-white">Extraction Progress</h3>
              <span className="text-sm font-medium text-slate-300">{progress}%</span>
            </div>
            
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.3, delay: 0.2 }}
              className="origin-left"
            >
              <Progress value={progress} className="h-3 mb-2" />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.4 }}
              className="flex justify-between items-center mt-2"
            >
              <span className="text-sm text-slate-300">{getProgressStatusText()}</span>
              <div className="flex space-x-2">
                {progressStatus === 'processing' ? (
                  <>
                    <Button
                      type="button"
                      onClick={stopExtraction}
                      variant="destructive"
                      className="bg-red-600 hover:bg-red-700 text-white"
                    >
                      <PauseIcon className="h-5 w-5 mr-2" />
                      Stop Extraction
                    </Button>
                    <Button
                      type="button"
                      onClick={() => setShowLogModal(true)}
                      variant="outline"
                      className="bg-gradient-to-r from-black via-zinc-950 to-black 
                      hover:bg-cardbg-600 hover:text-red-600 text-white border border-slate-800"
                    >
                      View Terminal
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      type="button"
                      onClick={handleStartExtraction}
                      disabled={
                        extractionData.selectedModels.length === 0 || 
                        extractionData.selectedPromptStyles.length === 0 || 
                        !extractionData.file
                      }
                      className="bg-gradient-to-r from-black via-zinc-950 to-black 
                      hover:bg-cardbg-600 hover:text-blue-600 text-white border border-slate-800"
                    >
                      <RotateCcw className="h-5 w-5 mr-2" />
                      Restart Extraction
                    </Button>
                    <Button
                      type="button"
                      onClick={() => setShowLogModal(true)}
                      variant="outline"
                      className="bg-gradient-to-r from-black via-zinc-950 to-black 
                      hover:bg-cardbg-600 hover:text-red-600 text-white border border-slate-800"
                    >
                      View Terminal
                    </Button>
                  </>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
} 