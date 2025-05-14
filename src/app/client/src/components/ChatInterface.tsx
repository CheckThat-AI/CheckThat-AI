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
  EyeOffIcon
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

  const [selectedModel, setSelectedModel] = useState<ModelOption>('claude-3-7-sonnet-latest');
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const { toast } = useToast();
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const modelOptions: { value: ModelOption; label: string }[] = [
    { value: 'claude-3-7-sonnet-latest', label: 'Claude 3.7 Sonnet' },
    { value: 'gpt-4o-2024-11-20', label: 'GPT-4o' },
    { value: 'gpt-4.1-2025-04-14', label: 'GPT-4.1' },
    { value: 'gpt-4.1-nano-2025-04-14', label: 'GPT-4.1 nano' },
    { value: 'gemini-2.5-pro-preview-05-06', label: 'Gemini 2.5 Pro' },
    { value: 'gemini-2.5-flash-preview-04-17', label: 'Gemini 2.5 Flash' },
    { value: 'grok-3-latest', label: 'Grok 3 Beta' },
    { value: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre', label: 'Llama 3.3 70B' },
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
      <div className="flex-grow mb-4 overflow-auto bg-white rounded-lg shadow-sm p-4 max-h-[calc(100vh-240px)]" ref={messageContainerRef}>
        <div className="flex flex-col space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`message-bubble max-w-[80%] p-3 rounded-2xl mb-1 relative ${
                message.sender === 'user' 
                  ? 'bg-primary text-white rounded-tr-sm self-end' 
                  : 'bg-slate-100 text-slate-800 rounded-tl-sm self-start'
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
      <Card>
        <CardContent className="p-4">
          <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
            <div className="flex items-center">
              <Textarea
                id="message-input"
                className="flex-grow resize-none border border-slate-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Type your claim here..."
                rows={2}
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-2">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          type="button"
                          variant="outline"
                          className="flex items-center text-slate-600 hover:text-primary-600 bg-slate-100 hover:bg-slate-200"
                          onClick={handleFileUploadClick}
                        >
                          <PaperclipIcon className="h-4 w-4 mr-1" />
                          <span className="text-sm">Upload</span>
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Accepted formats: csv, json, jsonl, txt</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  {selectedFile && (
                    <div className="text-sm text-slate-500 flex items-center">
                      {getFileIcon(selectedFile.name)}
                      <span>{selectedFile.name}</span>
                    </div>
                  )}
                </div>
                <input
                  type="file"
                  id="file-upload"
                  ref={fileInputRef}
                  className="hidden"
                  accept=".csv,.json,.jsonl,.txt,text/csv,application/json,application/x-jsonlines,text/plain"
                  onChange={handleFileInputChange}
                />
              </div>
              <div className="flex items-center space-x-2">
                <Select
                  value={selectedModel}
                  onValueChange={(value) => setSelectedModel(value as ModelOption)}
                >
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {modelOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedModel && (
                  <div className="flex items-center space-x-2">
                    <div className="relative">
                      <KeyIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500" />
                      <Input
                        type={showApiKey ? "text" : "password"}
                        placeholder="Enter your API Key here"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        className="pl-9 pr-9 w-[250px]"
                      />
                      <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-slate-700"
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
                <Button
                  type="submit"
                  className="bg-primary hover:bg-primary/90 text-white"
                  disabled={!currentMessage.trim() && !selectedFile}
                >
                  <span>Send</span>
                  <SendIcon className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
