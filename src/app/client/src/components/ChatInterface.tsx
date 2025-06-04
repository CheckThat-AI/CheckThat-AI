import React, { useRef, useEffect, useState } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import type { Message } from '@shared/types';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { formatMarkdown } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { 
  SendIcon,
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
import './scrollbar-hide.css';

export default function ChatInterface() {
  const { 
    messages, 
    currentMessage, 
    setCurrentMessage, 
    sendMessage,
    selectedModel,
    setSelectedModel,
    apiKey,
    setApiKey,
    setMessages
  } = useAppContext();

  const [showApiKey, setShowApiKey] = useState(false);
  const { toast } = useToast();
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const modelOptions: { value: ModelOption; label: string }[] = [
    { value: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free', label: 'Llama 3.3 70B' },
    { value: 'claude-3.7-sonnet-latest', label: 'Claude 3.7 Sonnet' },
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
  
  const [showApiKeyError, setShowApiKeyError] = useState(false);

  const handleSubmit = async (e?: React.FormEvent | React.KeyboardEvent) => {
    console.log('handleSubmit called');
    if (e) e.preventDefault();
    
    // Check if API key is required but not provided
    const isDefaultModel = selectedModel === 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free';
    const apiKeyRequired = !isDefaultModel && !apiKey.trim();
    
    if (apiKeyRequired) {
      setShowApiKeyError(true);
      // Auto-hide the error after 3 seconds
      setTimeout(() => setShowApiKeyError(false), 3000);
      return;
    }
    
    setShowApiKeyError(false);
    console.log('Calling sendMessage');

    // Add the user message to the chat immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: currentMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Add a temporary assistant message for streaming
    const tempMessageId = (Date.now() + 1).toString();
    const tempMessage: Message = {
      id: tempMessageId,
      sender: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, tempMessage]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_query: currentMessage,
          model: selectedModel,
          api_key: apiKey
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');
      
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      let accumulatedContent = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = new TextDecoder().decode(value);
        accumulatedContent += chunk;
        setMessages(prev => prev.map(msg =>
          msg.id === tempMessageId
            ? { ...msg, content: accumulatedContent }
            : msg
        ));
      }
      // After streaming is done, parse and clean up
      try {
        const parsed = JSON.parse(accumulatedContent);
        const cleanText = parsed.claim || parsed.normalizedClaim || parsed.result || accumulatedContent;
        setMessages(prev => prev.map(msg =>
          msg.id === tempMessageId
            ? { ...msg, content: cleanText, isStreaming: false }
            : msg
        ));
      } catch {
        setMessages(prev => prev.map(msg =>
          msg.id === tempMessageId
            ? { ...msg, content: accumulatedContent, isStreaming: false }
            : msg
        ));
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => prev.map(msg =>
        msg.id === tempMessageId
          ? { ...msg, content: 'Error: Failed to get response', isStreaming: false }
          : msg
      ));
    }
    setCurrentMessage('');
    textareaRef.current?.focus();
  };

  const handleTextareaKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    console.log('handleTextareaKeyDown called with key:', e.key);
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isChatStarted = messages.length > 1 || (messages.length === 1 && messages[0].sender !== 'system');

  return (
    <div className="flex-1 flex flex-col">
      {!isChatStarted ? (
        <div className="flex flex-col items-center justify-center flex-1">
          <div className="w-full max-w-3xl">
            {/* System message */}
            {messages[0] && messages[0].sender === 'system' && (
              <div className="mb-8 text-center text-slate-200 text-lg">
                <div dangerouslySetInnerHTML={{ __html: formatMarkdown(messages[0].content) }} />
              </div>
            )}
            {/* Input area */}
            <Card className="bg-transparent border-0 shadow-none w-full max-w-3xl mx-auto">
              <CardContent className="p-4 bg-gray-700 rounded-lg">
                <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
                  <div className="flex flex-col border border-gray-800 rounded-lg p-2 gap-2 bg-gradient-to-b from-gray-600 to-gray-700">
                    <Textarea
                      id="message-input"
                      ref={textareaRef}
                      className="flex-grow text-white resize-none border-0 focus:ring-0 focus:outline-none bg-transparent min-h-[40px] focus:border-0 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none placeholder:text-slate-200"
                      placeholder="Type or paste your input text here..."
                      rows={2}
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyDown={handleTextareaKeyDown}
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
                        {selectedModel && selectedModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
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
                        <div className="relative">
                          <Button
                            type="submit"
                            className="bg-gray-700 hover:bg-gray-600 text-white border-slate-600"
                            disabled={!currentMessage.trim()}
                          >
                            <ArrowUpIcon className="h-4 w-4" />
                          </Button>
                          {showApiKeyError && (
                            <motion.div
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-yellow-500 text-white text-sm rounded-md whitespace-nowrap"
                            >
                              Please enter an API key for this model
                            </motion.div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <AnimatePresence>
                    {selectedModel && selectedModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
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
        </div>
      ) : (
        <>
          <div
            className="mt-10 flex-1 flex-col overflow-auto scrollbar-hide 
            bg-gradient-to-b from-gray-700 to-gray-800 
            border border-gray-800 shadow-lg rounded-lg
            p-4 max-w-3xl w-full mx-auto 
            font-mono text-sm"
            ref={messageContainerRef}
            style={{ minHeight: '120px', maxHeight: '400px' }}
          >
            <pre className="whitespace-pre-wrap">
              {messages
                .filter((msg, idx) => !(idx === 0 && msg.sender === 'system'))
                .map((message) => (
                  <div
                    key={message.id}
                    className={`flex w-full ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`message-bubble p-3 rounded-2xl mb-1 relative 
                        max-w-[80%] 
                        ${message.sender === 'user' 
                          ? 'bg-primary text-white rounded-tr-sm self-end' 
                          : 'bg-slate-100 text-slate-800 rounded-tl-sm self-start'}
                        ${message.isStreaming ? 'animate-pulse' : ''}`}
                    >
                      <div
                        dangerouslySetInnerHTML={{
                          __html: formatMarkdown(message.content)
                        }}
                      />
                      {message.isStreaming && (
                        <div className="absolute bottom-1 right-1">
                          <div className="animate-spin h-3 w-3 border-2 border-gray-600 border-t-transparent rounded-full" />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
            </pre>
          </div>
          <Card 
            className="bg-transparent border-0 shadow-none 
            flex-1 flex-col max-w-3xl w-full mx-auto
            mt-4"
          >
            <CardContent 
              className="p-4 bg-gradient-to-b from-gray-600 to-gray-700 
              border border-gray-800 rounded-lg"
            >
              <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
                <div 
                  className="flex flex-col rounded-lg p-2 gap-2 
                  bg-gradient-to-b from-gray-600 to-gray-700
                  border-0 shadow-lg"
                >
                  <Textarea
                    id="message-input"
                    ref={textareaRef}
                    className="flex-grow text-white resize-none border-0 
                    bg-transparent min-h-[40px] 
                    focus:ring-0 focus:outline-none focus:border-0 
                    focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none 
                    placeholder:text-slate-200"
                    placeholder="Type or paste your input text here..."
                    rows={2}
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    onKeyDown={handleTextareaKeyDown}
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
                      {selectedModel && selectedModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
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
                      <Button
                        type="submit"
                        className="bg-gray-700 hover:bg-gray-600 text-white border-slate-600"
                        disabled={!currentMessage.trim()}
                      >
                        <ArrowUpIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                <AnimatePresence>
                  {selectedModel && selectedModel !== 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' && (
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
        </>
      )}
    </div>
  );
}
