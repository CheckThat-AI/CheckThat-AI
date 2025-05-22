import React, { useRef, useEffect, useState } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { formatMarkdown, isValidFileType } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { 
  PaperclipIcon, 
  SendIcon,
  FileTextIcon,
  FileJsonIcon,
  FileSpreadsheetIcon,
  KeyIcon,
  EyeIcon,
  EyeOffIcon,
  InfoIcon,
  ArrowUpIcon
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ModelOption } from '@shared/types';
import { motion, AnimatePresence } from 'framer-motion';

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

export default function ChatInterface() {
  const { 
    messages, 
    currentMessage, 
    setCurrentMessage, 
    sendMessage, 
    selectedFile, 
    handleFileChange 
  } = useAppContext();

  const [selectedModel, setSelectedModel] = useState<ModelOption>('meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre');
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const { toast } = useToast();
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const modelOptions: { value: ModelOption; label: string }[] = [
    { value: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre', label: 'Llama 3.3 70B' },
    { value: 'claude-3-7-sonnet-latest', label: 'Claude 3.7 Sonnet' },
    { value: 'gpt-4o-2024-11-20', label: 'GPT-4o' },
    { value: 'gpt-4.1-2025-04-14', label: 'GPT-4.1' },
    { value: 'gpt-4.1-nano-2025-04-14', label: 'GPT-4.1 nano' },
    { value: 'gemini-2.5-pro-preview-05-06', label: 'Gemini 2.5 Pro' },
    { value: 'gemini-2.5-flash-preview-04-17', label: 'Gemini 2.5 Flash' },
    { value: 'grok-3-latest', label: 'Grok 3 Beta' },
  ];

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage();
  };
  
  const handleFileUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    
    // Validate file
    if (file && !isValidFileType(file)) {
      toast({
        title: "Invalid File Type",
        description: "Please upload only CSV, JSON, JSONL, or TXT files.",
        variant: "destructive",
      });
      e.target.value = ''; // Reset input
      return;
    }
    
    handleFileChange(file);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat History */}
      <div className="flex-grow mb-4 overflow-auto justify-items-center bg-gray-700 border-0 rounded-lg shadow-gray-700 p-4 max-w-3xl w-full mx-auto max-h-[calc(100vh-240px)]" ref={messageContainerRef}>
        <div className="flex flex-col space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`message-bubble p-3 rounded-2xl mb-1 relative ${
                message.sender === 'user' 
                  ? 'max-w-[80%] bg-primary text-white rounded-tr-sm self-end' 
                  : message.sender === 'system'
                    ? 'w-full bg-gray-700 text-slate-200 rounded-tl-sm text-lg text-justify'
                    : 'max-w-[80%] bg-slate-100 text-slate-800 rounded-tl-sm self-start'
              }`}
            >
              <div 
                dangerouslySetInnerHTML={{ 
                  __html: formatMarkdown(message.content)
                }} 
              />
              
              {message.files && message.files.length > 0 && (
                <div className="mt-2 text-xs opacity-80">
                  <div className="flex items-center">
                    {getFileIcon(message.files[0].name)}
                    <span>{message.files[0].name}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* Chat Input */}
      <Card className="bg-transparent border-0 shadow-none max-w-3xl w-full mx-auto">
        <CardContent className="p-4 bg-gray-700 rounded-lg">
          <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
            <div className="flex flex-col border border-gray-800 rounded-lg p-2 gap-2 bg-gradient-to-b from-gray-600 to-gray-700">
              <Textarea
                id="message-input"
                className="flex-grow text-white resize-none border-0 focus:ring-0 focus:outline-none bg-transparent min-h-[40px] focus:border-0 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none placeholder:text-slate-200"
                placeholder="Type or paste your input text here..."
                rows={2}
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
              />
              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center space-x-2">
                  <Select
                    value={selectedModel}
                    onValueChange={(value) => setSelectedModel(value as ModelOption)}
                  >
                    <SelectTrigger className="w-[200px] bg-gray-700 text-white border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none data-[state=open]:ring-0 data-[state=open]:outline-none">
                      <SelectValue placeholder="Select model" />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-700 border-slate-600 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none">
                      {modelOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value} className="text-white focus:bg-gray-600 focus:text-white">
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {selectedModel && selectedModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre' && (
                    <div className="flex items-center space-x-2">
                      <div className="relative">
                        <KeyIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <Input
                          type={showApiKey ? "text" : "password"}
                          placeholder="Enter your API Key here"
                          value={apiKey}
                          onChange={(e) => setApiKey(e.target.value)}
                          className="pl-9 pr-9 w-[250px] bg-gray-700 text-white border-slate-600 placeholder:text-slate-400 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none"
                        />
                        <button
                          type="button"
                          onClick={() => setShowApiKey(!showApiKey)}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                        >
                          {showApiKey ? (
                            <EyeOffIcon className="h-4 w-4" />
                          ) : (
                            <EyeIcon className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  {selectedFile && (
                    <div className="text-sm text-slate-500 flex items-center">
                      {getFileIcon(selectedFile.name)}
                      <span>{selectedFile.name}</span>
                    </div>
                  )}
                  <Button
                    type="submit"
                    className="bg-gray-700 hover:bg-gray-600 text-white border-slate-600"
                    disabled={!currentMessage.trim() && !selectedFile}
                  >
                    <ArrowUpIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
            <input
              type="file"
              id="file-upload"
              ref={fileInputRef}
              className="hidden"
              accept=".csv,.json,.jsonl,.txt,text/csv,application/json,application/x-jsonlines,text/plain"
              onChange={handleFileInputChange}
            />

            {/* API Key Policy Note */}
            <AnimatePresence>
              {selectedModel && selectedModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre' && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="mt-3 flex items-start space-x-2 text-sm text-slate-200 bg-gray-800 p-3 rounded-lg border border-slate-700"
                >
                  <InfoIcon className="h-4 w-4 mt-0.5 flex-shrink-0 text-slate-400" />
                  <p>
                    Llama 3.3 70B is our free default model. If you wish to use other models, you need to enter your API Key. 
                    We do not store your API Keys or share them with anyone. Your API keys are automatically purged after every request.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
