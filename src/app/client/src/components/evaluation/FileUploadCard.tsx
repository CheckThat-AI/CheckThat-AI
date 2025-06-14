import React from 'react';
import { Button } from '@/components/ui/button';
import { PaperclipIcon, FileTextIcon, FileJsonIcon, FileSpreadsheetIcon } from 'lucide-react';
import { FieldMapping } from '@shared/types';
import { useToast } from '@/hooks/use-toast';
import { isValidFileType } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface FileUploadCardProps {
  readonly evaluationData: any;
  readonly updateEvaluationData: (data: any) => void;
  readonly fieldMapping: FieldMapping;
  readonly setShowFieldMappingModal: (show: boolean) => void;
}

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

export default function FileUploadCard({
  evaluationData,
  updateEvaluationData,
  fieldMapping,
  setShowFieldMappingModal
}: FileUploadCardProps) {
  const { toast } = useToast();

  return (
    <div className="mb-2">
      <div className="mt-6">
        <h4 className="text-md font-medium text-white mb-2">Upload Dataset</h4>
        <div className="flex items-center space-x-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="outline"
                  className="flex items-center text-slate-300 hover:text-primary-600 bg-cardbg-900 hover:bg-cardbg-800"
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
            <div className="flex flex-col space-y-2 px-4 py-4 mt-6">
              <div className="text-sm text-slate-500 flex items-center">
                {getFileIcon(evaluationData.file.name)}
                <span>{evaluationData.file.name}</span>
                <Button
                  variant="outline"
                  size="sm"
                  className="ml-6 bg-cardbg-900 hover:bg-cardbg-800 text-white border-slate-800 text-sm px-4 py-4 hover:text-white"
                  onClick={() => setShowFieldMappingModal(true)}
                >
                  Edit Mapping
                </Button>
              </div>
              {fieldMapping.inputText && (
                <div className="text-xs text-slate-400 text-start mt-6">
                  Input: "{fieldMapping.inputText}"
                  {fieldMapping.expectedOutput && `, Expected Output: "${fieldMapping.expectedOutput}"`}
                  {fieldMapping.actualOutput && `, Actual Output: "${fieldMapping.actualOutput}"`}
                  {fieldMapping.context && `, Context: "${fieldMapping.context}"`}
                  {fieldMapping.retrievalContext && `, Retrieval Context: "${fieldMapping.retrievalContext}"`}
                  {fieldMapping.metadata && `, Metadata: "${fieldMapping.metadata}"`}
                  {fieldMapping.comments && `, Comments: "${fieldMapping.comments}"`}
                </div>
              )}
            </div>
          )}
        </div>
        <input  
          type="file"
          id="file-upload"
          className="hidden"
          accept=".csv,.json,.jsonl,text/csv,application/json,application/x-jsonlines"
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
            if (file) {
              updateEvaluationData({ file });
              setShowFieldMappingModal(true);
            } else {
              updateEvaluationData({ file: null, fieldMapping: null });
            }
          }}
        />
      </div>
    </div>
  );
} 