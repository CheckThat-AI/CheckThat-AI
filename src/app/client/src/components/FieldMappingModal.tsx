import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { CheckIcon, AlertCircleIcon } from "lucide-react";
import { FieldMapping } from "@shared/types";

interface FieldMappingModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly file: File | null;
  readonly onSave: (mapping: FieldMapping) => void;
  readonly initialMapping: FieldMapping | null;
}

interface DetectedFields {
  columns: string[];
  sampleData: Record<string, any>[];
  fileType: 'csv' | 'json' | 'jsonl';
}

export default function FieldMappingModal({ isOpen, onClose, file, onSave, initialMapping }: FieldMappingModalProps) {
  const [detectedFields, setDetectedFields] = useState<DetectedFields | null>(null);
  const [mapping, setMapping] = useState<FieldMapping>({
    inputText: null,
    expectedOutput: null,
    actualOutput: null,
    context: null,
    retrievalContext: null,
    metadata: null,
    comments: null,
  });
  const [contextDelimiter, setContextDelimiter] = useState<string>('none');
  const [retrievalContextDelimiter, setRetrievalContextDelimiter] = useState<string>('none');
  const [isLoading, setIsLoading] = useState(false);

  // Detect file structure when modal opens and file is provided
  useEffect(() => {
    if (isOpen && file) {
      detectFileStructure(file);
    }
  }, [isOpen, file]);

  const detectFileStructure = async (file: File) => {
    setIsLoading(true);
    try {
      const fileContent = await readFileContent(file);
      const fileType = getFileType(file.name);
      
      let columns: string[] = [];
      let sampleData: Record<string, any>[] = [];

      if (fileType === 'csv') {
        const { headers, rows } = parseCSV(fileContent);
        columns = headers;
        sampleData = rows.slice(0, 3); // Get first 3 rows as sample
      } else if (fileType === 'json') {
        const jsonData = JSON.parse(fileContent);
        if (Array.isArray(jsonData) && jsonData.length > 0) {
          columns = Object.keys(jsonData[0]);
          sampleData = jsonData.slice(0, 3);
        }
      } else if (fileType === 'jsonl') {
        const lines = fileContent.trim().split('\n');
        const firstLine = JSON.parse(lines[0]);
        columns = Object.keys(firstLine);
        sampleData = lines.slice(0, 3).map(line => JSON.parse(line));
      }

      setDetectedFields({ columns, sampleData, fileType });
      
      // Auto-suggest mappings based on common column names
      autoSuggestMappings(columns);
      
    } catch (error) {
      console.error('Error detecting file structure:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  };

  const getFileType = (fileName: string): 'csv' | 'json' | 'jsonl' => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    if (extension === 'csv') return 'csv';
    if (extension === 'jsonl') return 'jsonl';
    return 'json';
  };

  const parseCSV = (content: string) => {
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/['"]/g, ''));
    const rows = lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.trim().replace(/['"]/g, ''));
      const row: Record<string, any> = {};
      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });
      return row;
    });
    return { headers, rows };
  };

  const autoSuggestMappings = (columns: string[]) => {
    const suggestions: FieldMapping = {
      inputText: null,
      expectedOutput: null,
      actualOutput: null,
      context: null,
      retrievalContext: null,
      metadata: null,
      comments: null,
    };

    // Common patterns for input text
    const textPatterns = ['text', 'claim', 'input', 'content', 'message', 'statement'];
    const textColumn = columns.find(col => 
      textPatterns.some(pattern => col.toLowerCase().includes(pattern))
    );
    if (textColumn) suggestions.inputText = textColumn;

    // Common patterns for ground truth
    const truthPatterns = ['truth', 'label', 'target', 'expected', 'reference', 'ground', 'answer'];
    const truthColumn = columns.find(col => 
      truthPatterns.some(pattern => col.toLowerCase().includes(pattern))
    );
    if (truthColumn) suggestions.expectedOutput = truthColumn;

    // Common patterns for context
    const contextPatterns = ['context', 'prompt', 'instruction', 'query'];
    const contextColumn = columns.find(col => 
      contextPatterns.some(pattern => col.toLowerCase().includes(pattern))
    );
    if (contextColumn) suggestions.context = contextColumn;

    // Common patterns for actual output
    const actualOutputPatterns = ['output', 'generated', 'prediction', 'result', 'response'];
    const actualOutputColumn = columns.find(col => 
      actualOutputPatterns.some(pattern => col.toLowerCase().includes(pattern))
    );
    if (actualOutputColumn) suggestions.actualOutput = actualOutputColumn;

    // Common patterns for retrieval context
    const retrievalPatterns = ['retrieval', 'retrieved', 'document', 'passage', 'knowledge'];
    const retrievalColumn = columns.find(col => 
      retrievalPatterns.some(pattern => col.toLowerCase().includes(pattern))
    );
    if (retrievalColumn) suggestions.retrievalContext = retrievalColumn;

    // Common patterns for metadata
    const metadataPatterns = ['metadata', 'meta', 'info', 'details', 'id', 'index'];
    const metadataColumn = columns.find(col => 
      metadataPatterns.some(pattern => col.toLowerCase().includes(pattern))
    );
    if (metadataColumn) suggestions.metadata = metadataColumn;

    // Common patterns for comments
    const commentPatterns = ['comment', 'note', 'remark', 'observation'];
    const commentColumn = columns.find(col => 
      commentPatterns.some(pattern => col.toLowerCase().includes(pattern))
    );
    if (commentColumn) suggestions.comments = commentColumn;

    setMapping(suggestions);
  };

  const handleConfirm = () => {
    const mappingWithDelimiters = {
      ...mapping,
      contextDelimiter: mapping.context ? (contextDelimiter === 'none' ? null : contextDelimiter) : undefined,
      retrievalContextDelimiter: mapping.retrievalContext ? (retrievalContextDelimiter === 'none' ? null : retrievalContextDelimiter) : undefined,
    };
    onSave(mappingWithDelimiters);
    onClose();
  };

  const isValidMapping = mapping.inputText !== null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] flex-1 flex-col
      bg-gradient-to-r from-black to-zinc-950 via-cardbg-900
      border border-slate-800 shadow-xl rounded-lg
      text-slate-200 overflow-y-auto custom-scrollbar overflow-x-auto">
        <DialogHeader>
          <DialogTitle className="text-white">Map Dataset Fields</DialogTitle>
          <DialogDescription className="text-slate-300">
            Map your dataset columns to the required fields for evaluation.
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full mr-3" />
            <span>Analyzing file structure...</span>
          </div>
        ) : detectedFields ? (
          <div className="space-y-6">
            {/* File Info */}
            <div className="bg-gradient-to-r from-black via-zinc-950 to-black 
            p-4 rounded-lg border border-slate-800 shadow-xl">
              <h3 className="text-sm font-medium text-white mb-2">File Information</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">File Type:</span>
                  <span className="ml-2 uppercase font-mono">{detectedFields.fileType}</span>
                </div>
                <div>
                  <span className="text-slate-400">Detected Columns:</span>
                  <span className="ml-2">{detectedFields.columns.length}</span>
                </div>
              </div>
            </div>

            {/* Field Mapping */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-white">Field Mapping</h3>
              
              {/* Input Text Mapping */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white flex items-center">
                  Input<span className="text-red-400 ml-1">*</span>
                  <span className="text-xs text-slate-400 ml-2">(Required - The input text/query/prompt given to the model)</span>
                </label>
                <Select value={mapping.inputText || 'none'} onValueChange={(value) => {
                  const inputText = value === 'none' ? null : value;
                  setMapping(prev => ({ ...prev, inputText }));
                }}>
                  <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  text-white border-slate-800">
                    <SelectValue placeholder="Select column for input text" />
                  </SelectTrigger>
                  <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  border-slate-800 text-white focus:bg-cardbg-900">
                    <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None</SelectItem>
                    {detectedFields.columns.map((column) => (
                      <SelectItem key={column} value={column} className="text-white focus:bg-cardbg-900 focus:text-white">
                        {column}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Actual Output Mapping */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white flex items-center">
                  Actual Output<span className="text-red-400 ml-1">*</span>
                  <span className="text-xs text-slate-400 ml-2">(Required - Output text generated by your model)</span>
                </label>
                <Select value={mapping.actualOutput || 'none'} onValueChange={(value) => {
                  const actualOutput = value === 'none' ? null : value;
                  setMapping(prev => ({ ...prev, actualOutput }));
                }}>
                  <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  text-white border-slate-800">
                    <SelectValue placeholder="Select column for actual output (optional)" />
                  </SelectTrigger>
                  <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  border-slate-800 text-white focus:bg-cardbg-900">
                    <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None</SelectItem>
                    {detectedFields.columns.map((column) => (
                      <SelectItem key={column} value={column} className="text-white focus:bg-cardbg-900 focus:text-white">
                        {column}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* Ground Truth Mapping */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white flex items-center">
                  Expected Output
                  <span className="text-xs text-slate-400 ml-2">(Optional - Required only for reference-based metrics like accuracy)</span>
                </label>
                <Select value={mapping.expectedOutput || 'none'} onValueChange={(value) => {
                  const expectedOutput = value === 'none' ? null : value;
                  setMapping(prev => ({ ...prev, expectedOutput }));
                }}>
                  <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  text-white border-slate-800">
                    <SelectValue placeholder="Select column for ground truth (optional)" />
                  </SelectTrigger>
                  <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  border-slate-800 text-white focus:bg-cardbg-900">
                    <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None</SelectItem>
                    {detectedFields.columns.map((column) => (
                      <SelectItem key={column} value={column} className="text-white focus:bg-cardbg-900 focus:text-white">
                        {column}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Retrieval Context Mapping */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white flex items-center">
                  Retrieval Context
                  <span className="text-xs text-slate-400 ml-2">(Optional List of text - Retrieved context for RAG systems)</span>
                </label>
                <div className="flex space-x-2">
                  <Select value={mapping.retrievalContext || 'none'} onValueChange={(value) => {
                    const retrievalContext = value === 'none' ? null : value;
                    setMapping(prev => ({ ...prev, retrievalContext }));
                  }}>
                    <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                    text-white border-slate-800 flex-1">
                      <SelectValue placeholder="Select column for retrieval context (optional)" />
                    </SelectTrigger>
                    <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                    border-slate-800 text-white focus:bg-cardbg-900">
                      <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None</SelectItem>
                      {detectedFields.columns.map((column) => (
                        <SelectItem key={column} value={column} className="text-white focus:bg-cardbg-900 focus:text-white">
                          {column}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {mapping.retrievalContext && (
                    <Select value={retrievalContextDelimiter} onValueChange={setRetrievalContextDelimiter}>
                      <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                      text-white border-slate-800 w-32">
                        <SelectValue placeholder="Delimiter" />
                      </SelectTrigger>
                      <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                      border-slate-800 text-white focus:bg-cardbg-900">
                        <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None (Single entry)</SelectItem>
                        <SelectItem value="\n" className="text-white focus:bg-cardbg-900 focus:text-white">Newline</SelectItem>
                        <SelectItem value="," className="text-white focus:bg-cardbg-900 focus:text-white">Comma</SelectItem>
                        <SelectItem value=";" className="text-white focus:bg-cardbg-900 focus:text-white">Semicolon</SelectItem>
                        <SelectItem value="|" className="text-white focus:bg-cardbg-900 focus:text-white">Pipe</SelectItem>
                        <SelectItem value=" " className="text-white focus:bg-cardbg-900 focus:text-white">Space</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                </div>
                {mapping.retrievalContext && (
                  <p className="text-xs text-slate-500">
                    Delimiter: "{retrievalContextDelimiter === 'none' ? 'None (use entire entry)' : retrievalContextDelimiter === '\n' ? '\\n' : retrievalContextDelimiter}" - {retrievalContextDelimiter === 'none' ? 'Use entire column entry as single context' : 'Used to split multiple context items'}
                  </p>
                )}
              </div>

              {/* Context Mapping */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white flex items-center">
                  Context
                  <span className="text-xs text-slate-400 ml-2">(Optional List of text - Additional context for the input)</span>
                </label>
                <div className="flex space-x-2">
                  <Select value={mapping.context || 'none'} onValueChange={(value) => {
                    const context = value === 'none' ? null : value;
                    setMapping(prev => ({ ...prev, context }));
                  }}>
                    <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                    text-white border-slate-800 flex-1">
                      <SelectValue placeholder="Select column for context (optional)" />
                    </SelectTrigger>
                    <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                    border-slate-800 text-white focus:bg-cardbg-900">
                      <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None</SelectItem>
                      {detectedFields.columns.map((column) => (
                        <SelectItem key={column} value={column} className="text-white focus:bg-cardbg-900 focus:text-white">
                          {column}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {mapping.context && (
                    <Select value={contextDelimiter} onValueChange={setContextDelimiter}>
                      <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                      text-white border-slate-800 w-32">
                        <SelectValue placeholder="Delimiter" />
                      </SelectTrigger>
                      <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                      border-slate-800 text-white focus:bg-cardbg-900">
                        <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None (Single entry)</SelectItem>
                        <SelectItem value="\n" className="text-white focus:bg-cardbg-900 focus:text-white">Newline</SelectItem>
                        <SelectItem value="," className="text-white focus:bg-cardbg-900 focus:text-white">Comma</SelectItem>
                        <SelectItem value=";" className="text-white focus:bg-cardbg-900 focus:text-white">Semicolon</SelectItem>
                        <SelectItem value="|" className="text-white focus:bg-cardbg-900 focus:text-white">Pipe</SelectItem>
                        <SelectItem value=" " className="text-white focus:bg-cardbg-900 focus:text-white">Space</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                </div>
                {mapping.context && (
                  <p className="text-xs text-slate-500">
                    Delimiter: "{contextDelimiter === 'none' ? 'None (use entire entry)' : contextDelimiter === '\n' ? '\\n' : contextDelimiter}" - {contextDelimiter === 'none' ? 'Use entire column entry as single context' : 'Used to split multiple context items'}
                  </p>
                )}
              </div>

              {/* Metadata Mapping */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white flex items-center">
                  Metadata
                  <span className="text-xs text-slate-400 ml-2">(Optional - Additional metadata about the record)</span>
                </label>
                <Select value={mapping.metadata || 'none'} onValueChange={(value) => {
                  const metadata = value === 'none' ? null : value;
                  setMapping(prev => ({ ...prev, metadata }));
                }}>
                  <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  text-white border-slate-800">
                    <SelectValue placeholder="Select column for metadata (optional)" />
                  </SelectTrigger>
                  <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  border-slate-800 text-white focus:bg-cardbg-900">
                    <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None</SelectItem>
                    {detectedFields.columns.map((column) => (
                      <SelectItem key={column} value={column} className="text-white focus:bg-cardbg-900 focus:text-white">
                        {column}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Comments Mapping */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white flex items-center">
                  Comments
                  <span className="text-xs text-slate-400 ml-2">(Optional - Comments or notes about the record)</span>
                </label>
                <Select value={mapping.comments || 'none'} onValueChange={(value) => {
                  const comments = value === 'none' ? null : value;
                  setMapping(prev => ({ ...prev, comments }));
                }}>
                  <SelectTrigger className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  text-white border-slate-800">
                    <SelectValue placeholder="Select column for comments (optional)" />
                  </SelectTrigger>
                  <SelectContent className="bg-gradient-to-r from-black via-zinc-950 to-black 
                  border-slate-800 text-white focus:bg-cardbg-900">
                    <SelectItem value="none" className="text-white focus:bg-cardbg-900 focus:text-white">None</SelectItem>
                    {detectedFields.columns.map((column) => (
                      <SelectItem key={column} value={column} className="text-white focus:bg-cardbg-900 focus:text-white">
                        {column}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Sample Data Preview */}
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-white">Sample Data Preview</h3>
              <div className="bg-gradient-to-r from-black via-zinc-950 to-black 
              p-3 rounded-lg overflow-x-auto border border-slate-800 shadow-xl">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-gray-600">
                      {detectedFields.columns.map((column) => (
                        <th key={column} className="text-center p-2 text-white text-base font-bold">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {detectedFields.sampleData.map((row, index) => (
                      <tr key={`row-${index}-${Object.values(row).join('-').slice(0, 50)}`} className="border-b border-slate-800">
                        {detectedFields.columns.map((column) => (
                          <td key={column} className="p-2 text-slate-200 max-w-[200px] truncate border border-slate-800">
                            {String(row[column] || '')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Validation Message */}
            {!isValidMapping && (
              <div className="flex items-center space-x-2 text-yellow-400 bg-yellow-400/10 p-3 rounded-lg">
                <AlertCircleIcon className="h-4 w-4" />
                <span className="text-sm">Please select a column for the input text field (required).</span>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-700">
              <Button
                variant="outline"
                onClick={onClose}
                className="bg-gradient-to-r from-black via-zinc-950 to-black 
                hover:bg-cardbg-600 hover:text-red-600 text-white border-slate-800"
              >
                Cancel
              </Button>
              <Button
                onClick={handleConfirm}
                disabled={!isValidMapping}
                className="bg-gradient-to-r from-black via-zinc-950 to-black 
                hover:bg-cardbg-600 hover:text-green-600 text-white border border-slate-800"
              >
                <CheckIcon className="h-4 w-4 mr-2" />
                Confirm Mapping
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-8 text-slate-400">
            No file provided for analysis.
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
} 