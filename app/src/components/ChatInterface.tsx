import React, { useState, useRef, useEffect, useCallback } from 'react';
import { flushSync } from 'react-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectSeparator, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { UserAvatar } from '@/components/ui/UserAvatar';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { 
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar';
import { 
  Plus, 
  Paperclip, 
  History,
  Trash2,
  Upload,
  X,
  Loader2,
  Settings,
  BookOpen,
  ArrowUpIcon,
  ArrowDown,
  MessageSquare,
  LogOut,
  LogIn,
  Copy,
  Check,
  Square,
  Edit3,
  Save,
  X as XIcon
} from 'lucide-react';
import { ModeToggle } from './mode-toggle';
import { SignInDialog } from './SignInDialog';
import { Login } from './Login';
import { conversationService, type Conversation, type Message, type ConversationBranch } from '@/lib/conversationService';
import { supabase } from '@/lib/supabase';
import { apiService } from '@/lib/apiService';
import { StreamingMessageWrapper, BlinkingCursor } from './ui/streaming-indicators';
import checkThatLogo from '../assets/checkthat-logo.svg';
import ChatFeedbackPopup from './ChatFeedbackPopup';

interface UserInfo {
  id: string;
  email?: string;
  firstName: string;
  lastName: string;
  picture?: string;
  sessionId: string;
  isGuest?: boolean;
}

interface ChatInterfaceProps {
  user: UserInfo;
  onLogout: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ user }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [message, setMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState('meta-llama/Llama-3.3-70B-Instruct-Turbo-Free');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [showSignInDialog, setShowSignInDialog] = useState(false);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [pendingModel, setPendingModel] = useState<string>('');
  const [streamAbortController, setStreamAbortController] = useState<AbortController | null>(null);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState<string>('');
  const [conversationBranches, setConversationBranches] = useState<Record<string, { branches: ConversationBranch[], activeIndex: number }>>({});
  const [hasShownGuestContextWarning, setHasShownGuestContextWarning] = useState(false);
  const [showFeedbackPopup, setShowFeedbackPopup] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const [isUserNearBottom, setIsUserNearBottom] = useState(true);
  const isUserNearBottomRef = useRef<boolean>(true);
  const suppressAutoScrollUntilRef = useRef<number>(0);
  const feedbackIntervalRef = useRef<NodeJS.Timeout | null>(null);
  useEffect(() => {
    isUserNearBottomRef.current = isUserNearBottom;
  }, [isUserNearBottom]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check if conversation has started (has user messages beyond welcome message)
  const hasUserMessages = currentConversation?.messages.some(msg => msg.role === 'user') || false;
  const isInitialState = !hasUserMessages;

  useEffect(() => {
    document.title = currentConversation?.title ? `${currentConversation.title} - CheckThat AI` : 'CheckThat AI';
  }, [currentConversation]);

  // Feedback popup timer - shows every 60 seconds
  useEffect(() => {
    const startFeedbackTimer = () => {
      // Clear any existing interval
      if (feedbackIntervalRef.current) {
        clearInterval(feedbackIntervalRef.current);
      }
      
      // Start new interval
      feedbackIntervalRef.current = setInterval(() => {
        setShowFeedbackPopup(true);
      }, 60000);
    };

    // Start the timer immediately
    startFeedbackTimer();

    return () => {
      if (feedbackIntervalRef.current) {
        clearInterval(feedbackIntervalRef.current);
      }
    };
  }, []);

  // Restart timer when popup is closed
  useEffect(() => {
    if (!showFeedbackPopup) {
      // Restart the timer after a short delay when popup is closed
      const timer = setTimeout(() => {
        if (feedbackIntervalRef.current) {
          clearInterval(feedbackIntervalRef.current);
        }
        feedbackIntervalRef.current = setInterval(() => {
          setShowFeedbackPopup(true);
        }, 60000);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [showFeedbackPopup]);

  const models = [
    { value: 'gpt-5-2025-08-07', label: 'GPT-5', provider: 'OpenAI', isPaid: true },
    { value: 'gpt-5-nano-2025-08-07', label: 'GPT-5 nano', provider: 'OpenAI', isPaid: true },
    { value: 'o3-2025-04-16', label: 'o3', provider: 'OpenAI', isPaid: true },
    { value: 'o4-mini-2025-04-16', label: 'o4-mini', provider: 'OpenAI', isPaid: true },
    { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet 4', provider: 'Anthropic', isPaid: true },
    { value: 'claude-opus-4-1-20250805', label: 'Claude Opus 4.1', provider: 'Anthropic', isPaid: true },
    { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro', provider: 'Google', isPaid: true },
    { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash', provider: 'Google', isPaid: true },
    { value: 'grok-4-0709', label: 'Grok 4', provider: 'xAI', isPaid: true },
    { value: 'grok-3', label: 'Grok 3', provider: 'xAI', isPaid: true },
    { value: 'grok-3-mini', label: 'Grok 3 Mini', provider: 'xAI', isPaid: true },
    { value: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free', label: 'Llama 3.3 70B', provider: 'Together AI', isPaid: false },
    { value: 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free', label: 'DeepSeek R1 Distill Llama 70B', provider: 'Together AI', isPaid: false },
  ];

  const createWelcomeConversation = useCallback(() => {
    const welcomeConversation: Conversation = {
      id: 'welcome',
      title: 'New Chat',
      userId: user.id,
      messages: [
        {
          id: 'welcome-msg',
          content: user.isGuest 
            ? `Hello Guest! 👋\n\nWelcome to CheckThat AI - your comprehensive platform for claim normalization and fact-checking.\n\n**🎉 You're in Guest Mode!**\n\n**What you can do:**\n• Chat with our free Llama 3.3 70B model\n• Ask questions about claim normalization\n• Test our platform capabilities\n\n**Premium features (Sign in required):**\n• Access GPT-4o, Claude, Gemini Pro models\n• Higher rate limits and advanced features\n• File upload and document analysis\n\n**Getting Started:**\nJust start typing your questions below! The free Llama model is already selected and ready to help you with claim normalization tasks.`
            : `Hello ${user.firstName}! 👋\n\nWelcome to CheckThat AI - your comprehensive platform for claim normalization and \nFact-checking.\n\nTo get started:\n1. Click the key icon to set up your API keys\n2. Select a model from the dropdown\n3. Ask me anything about claim normalization, or upload a document to analyze!`,
          role: 'assistant',
          timestamp: new Date(),
        },
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setConversations([welcomeConversation]);
    setCurrentConversation(welcomeConversation);
  }, [user.id, user.firstName, user.isGuest]);

  // Load conversations from Supabase on mount
  useEffect(() => {
    const loadUserConversations = async () => {
      setIsLoadingConversations(true);
      try {
        // Skip Supabase for guest users
        if (user.isGuest) {
          createWelcomeConversation();
        } else {
          await conversationService.initializeUserConversations(user.id);
          const savedConversations = await conversationService.loadConversations(user.id);
          
          if (savedConversations.length > 0) {
            setConversations(savedConversations);
            setCurrentConversation(savedConversations[0]);
          } else {
            createWelcomeConversation();
          }
        }
      } catch (error) {
        console.error('Error loading conversations:', error);
        createWelcomeConversation();
      } finally {
        setIsLoadingConversations(false);
      }
    };

    loadUserConversations();
  }, [user.id, user.isGuest, createWelcomeConversation]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  // Track if user is near the bottom of the viewport
  const handleViewportScroll = useCallback(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const threshold = 24; // px, tighter threshold
    const distanceFromBottom = viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight;
    const nearBottom = distanceFromBottom <= threshold;
    setIsUserNearBottom(nearBottom);
    if (!nearBottom) {
      suppressAutoScrollUntilRef.current = Date.now() + 1500;
    }
  }, []);

  // Remove periodic auto-scroll; rely on on-chunk flush + near-bottom check

  // Immediate scroll when new content arrives during streaming (only if near bottom)
  useEffect(() => {
    if (isStreaming && currentConversation?.messages) {
      // Find the streaming message and scroll if it has content
      const streamingMessage = currentConversation.messages.find(msg => msg.isStreaming);
      if (streamingMessage?.content) {
        if (isUserNearBottom && Date.now() >= suppressAutoScrollUntilRef.current) {
        messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
        }
      }
    } else if (!isStreaming) {
      // Smooth scroll after streaming completes
      if (isUserNearBottom && Date.now() >= suppressAutoScrollUntilRef.current) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
    }
  }, [currentConversation?.messages, isStreaming, isUserNearBottom]);

  // Auto-save conversations when they change
  useEffect(() => {
    if (currentConversation && currentConversation.id !== 'welcome' && !user.isGuest) {
      conversationService.autoSaveConversation(currentConversation);
    }
  }, [currentConversation, user.isGuest]);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      userId: user.id,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversation(newConversation);
  };

  const handleModelChange = (modelValue: string) => {
    const model = models.find(m => m.value === modelValue);
    
    // Check if user is guest and trying to select a paid model
    if (user.isGuest && model?.isPaid) {
      setPendingModel(modelValue);
      setShowSignInDialog(true);
      return;
    }
    
    // If not guest or free model, proceed with selection
    setSelectedModel(modelValue);
  };

  const handleSignInSuccess = () => {
    setShowSignInDialog(false);
    // After successful sign-in, the App component will update the user state
    // and the user will no longer be a guest, allowing access to paid models
    window.location.reload(); // Refresh to get the updated user state
  };

  const handleLoginSuccess = () => {
    setShowLoginDialog(false);
    // After successful sign-in, the App component will update the user state
    // and the user will no longer be a guest
    window.location.reload(); // Refresh to get the updated user state
  };

  const sendMessage = async () => {
    if (!message.trim() || !currentConversation || isStreaming) return;

    // Show guest context warning toast if guest user and not shown before
    if (user.isGuest && !hasShownGuestContextWarning) {
      toast.error(
        "We do not yet support memory context for conversations in guest mode. Please try to include as much context as you can in your queries (≤200k tokens).",
        {
          duration: 5000, // Show for 8 seconds
          position: 'bottom-right',
          style: {
            background: '#FEF3C7',
            color: '#92400E',
            border: '1px solid #F59E0B',
            borderRadius: '8px',
            fontSize: '14px',
            maxWidth: '500px',
          },
        }
      );
      setHasShownGuestContextWarning(true);
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: message.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    // If this is the first user message and we're in the welcome conversation, create a proper conversation
    const isFirstUserMessage = !currentConversation.messages.some(msg => msg.role === 'user');
    const isWelcomeConversation = currentConversation.id === 'welcome';
    
    let workingConversation = currentConversation;
    
    if (isFirstUserMessage && isWelcomeConversation) {
      // Create a new conversation with proper ID and replace welcome in the list
      workingConversation = {
        ...currentConversation,
        id: Date.now().toString(),
        title: message.slice(0, 50) + (message.length > 50 ? '...' : ''),
        messages: [], // Start fresh without welcome message
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      // Replace the welcome conversation instead of adding a duplicate
      const previousId = currentConversation.id; // likely 'welcome'
      setConversations(prev => prev.map(conv => (conv.id === previousId ? workingConversation : conv)));
      setCurrentConversation(workingConversation);
    }
    
    // If this is the first user message, remove the welcome message
    const existingMessages = isFirstUserMessage 
      ? workingConversation.messages.filter(msg => msg.id !== 'welcome-msg')
      : workingConversation.messages;

    const updatedConversation = {
      ...workingConversation,
      messages: [...existingMessages, userMessage],
      title: isFirstUserMessage ? message.slice(0, 50) + (message.length > 50 ? '...' : '') : workingConversation.title,
      updatedAt: new Date(),
    };

    // Force immediate render of the user's message before starting network work
    flushSync(() => {
    setCurrentConversation(updatedConversation);
    setConversations(prev => 
        prev.map(conv => (conv.id === workingConversation.id ? updatedConversation : conv))
    );
    });
    
    const currentMessage = message.trim();
    setMessage('');
    setIsStreaming(true);

    // Create abort controller for this request
    const abortController = new AbortController();
    setStreamAbortController(abortController);

    // Create streaming message immediately (no loading state)
    const streamingMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      model: selectedModel,
      isStreaming: true,
    };

    const conversationWithStreaming = {
      ...updatedConversation,
      messages: [...updatedConversation.messages, streamingMessage],
    };

    flushSync(() => {
    setCurrentConversation(conversationWithStreaming);
    setConversations(prev => 
        prev.map(conv => (conv.id === workingConversation.id ? conversationWithStreaming : conv))
    );
    });

    try {
      // Get conversation history for multi-turn context (exclude the current message)
      const conversationHistory = updatedConversation.messages
        .filter(msg => msg.id !== userMessage.id && msg.id !== 'welcome-msg')
        .slice(0, -1); // Remove the just-added user message since it's sent separately

      const response = await apiService.chat(
        currentMessage,
        selectedModel,
        currentConversation.id,
        conversationHistory.length > 0 ? conversationHistory.map(msg => ({
          ...msg,
          timestamp: msg.timestamp.toISOString()
        })) : undefined,
        user.isGuest,
        { signal: abortController.signal }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let accumulatedContent = '';
      const FLUSH_INTERVAL_MS = 120; // Slow down updates slightly for smoother UX
      let lastFlushTime = 0;
      const rafIdRef = { current: null as number | null };
      const pendingContentRef = { current: '' };

      const currentConvId = workingConversation.id;

      const scheduleRafFlush = () => {
        if (rafIdRef.current !== null) return;
        rafIdRef.current = requestAnimationFrame(() => {
          rafIdRef.current = null;
          const contentToApply = pendingContentRef.current;
          const updatedStreamingMessage = {
            ...streamingMessage,
            content: contentToApply,
          };

          const finalConversation = {
            ...conversationWithStreaming,
            messages: conversationWithStreaming.messages.map(msg => 
              msg.id === streamingMessage.id ? updatedStreamingMessage : msg
            ),
            updatedAt: new Date(),
          };

          setCurrentConversation(finalConversation);
          setConversations(prev => prev.map(conv => (conv.id === currentConvId ? finalConversation : conv)));

          if (isUserNearBottomRef.current && Date.now() >= suppressAutoScrollUntilRef.current) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
          }
        });
      };
      
      // Process stream chunks as they arrive (token-based streaming)
      let streamCompleted = false;
      while (true) {
        // Check if stream was aborted
        if (abortController.signal.aborted) {
          console.log('Stream aborted by user');
          break;
        }

        const { done, value } = await reader.read();
        if (done) {
          console.log('Stream completed naturally');
          streamCompleted = true;
          break;
        }

        // Decode the chunk
        const chunk = decoder.decode(value, { stream: true });

        // For plain text responses, add the chunk directly
        if (chunk) {
          accumulatedContent += chunk;
          pendingContentRef.current = accumulatedContent;
          const now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
          if (now - lastFlushTime >= FLUSH_INTERVAL_MS) {
            lastFlushTime = now;
            scheduleRafFlush();
          }
        }
      }

      // Final flush to ensure all content is displayed
      if (accumulatedContent && pendingContentRef.current !== accumulatedContent) {
        pendingContentRef.current = accumulatedContent;
        scheduleRafFlush();
      }

      // Mark streaming as complete - always stop the streaming state first
      setIsStreaming(false);
      
      if (streamCompleted && !abortController.signal.aborted) {
        // Stream completed naturally
        console.log('Finalizing completed stream with content length:', accumulatedContent.length);
        
        const completedMessage = {
          ...streamingMessage,
          content: accumulatedContent,
          isStreaming: false,
        };

        const completedConversation = {
          ...conversationWithStreaming,
          messages: conversationWithStreaming.messages.map(msg => 
            msg.id === streamingMessage.id ? completedMessage : msg
          ),
          updatedAt: new Date(),
        };

        // Force synchronous update to ensure immediate re-render
        flushSync(() => {
          setCurrentConversation(completedConversation);
          setConversations(prev => prev.map(conv => (conv.id === currentConvId ? completedConversation : conv)));
        });

        console.log('Completed message isStreaming:', completedMessage.isStreaming);
      } else {
        // Stream was aborted or interrupted
        console.log('Finalizing aborted/interrupted stream');
        
        const abortedMessage = {
          ...streamingMessage,
          content: accumulatedContent + (abortController.signal.aborted ? '\n\n[Generation stopped by user]' : '\n\n[Generation interrupted]'),
          isStreaming: false,
        };

        const abortedConversation = {
          ...conversationWithStreaming,
          messages: conversationWithStreaming.messages.map(msg => 
            msg.id === streamingMessage.id ? abortedMessage : msg
          ),
          updatedAt: new Date(),
        };

        // Force synchronous update to ensure immediate re-render
        flushSync(() => {
          setCurrentConversation(abortedConversation);
          setConversations(prev => prev.map(conv => (conv.id === currentConvId ? abortedConversation : conv)));
        });

        console.log('Aborted message isStreaming:', abortedMessage.isStreaming);
      }

      // Ensure streaming state is fully cleared and restore focus
      setTimeout(() => {
        // Double-check that streaming state is cleared (safeguard against race conditions)
        setIsStreaming(false);
        
        // Force a final state check and re-render
        setCurrentConversation(prev => {
          if (!prev) return prev;
          const updatedMessages = prev.messages.map(msg => 
            msg.isStreaming ? { ...msg, isStreaming: false } : msg
          );
          return { ...prev, messages: updatedMessages };
        });
        
        textareaRef.current?.focus();
      }, 100);

    } catch (error) {
      // Handle abort error differently
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was aborted by user');
        return;
      }

      console.error('Error sending message:', error);
      
      // Remove the streaming message and add error message instead
      const conversationWithoutStreaming = {
        ...conversationWithStreaming,
        messages: conversationWithStreaming.messages.filter(msg => msg.id !== streamingMessage.id),
      };
      
      // Determine error type and provide specific guidance
      let errorContent = '⚠️ ';
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorContent += 'Connection Error: Unable to connect to the server.\n\nPlease check:\n1. The backend server is running on localhost:8000\n2. Your internet connection is stable';
      } else if (error instanceof Error && error.message.includes('401')) {
        errorContent += 'Authentication Error: Invalid API key.\n\nPlease check:\n1. Your API key is correctly set\n2. The API key has sufficient credits\n3. The API key has the correct permissions';
      } else if (error instanceof Error && error.message.includes('429')) {
        errorContent += 'Rate Limit Error: Too many requests.\n\nPlease:\n1. Wait a moment before trying again\n2. Check your API usage limits';
      } else {
        errorContent += `Unexpected Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}.\n\nPlease try again or contact support if the issue persists.`;
      }
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: errorContent,
        role: 'assistant',
        timestamp: new Date(),
        model: selectedModel,
      };

      const errorConversation = {
        ...conversationWithoutStreaming,
        messages: [...conversationWithoutStreaming.messages, errorMessage],
        updatedAt: new Date(),
      };

      setCurrentConversation(errorConversation);
      setConversations(prev => 
        prev.map(conv => conv.id === currentConversation.id ? errorConversation : conv)
      );
      
      // Restore focus to textarea after error
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    } finally {
      setIsStreaming(false);
      setStreamAbortController(null);
    }
  };

  const stopStreaming = () => {
    if (streamAbortController) {
      streamAbortController.abort();
      setIsStreaming(false);
      
      // Optionally mark the current streaming message as stopped
      if (currentConversation) {
        const stoppedConversation = {
          ...currentConversation,
          messages: currentConversation.messages.map(msg => 
            msg.isStreaming 
              ? { ...msg, isStreaming: false, content: msg.content + '\n\n[Generation stopped]' }
              : msg
          ),
          updatedAt: new Date(),
        };
        
        setCurrentConversation(stoppedConversation);
        setConversations(prev => 
          prev.map(conv => conv.id === currentConversation.id ? stoppedConversation : conv)
        );
      }
      
      // Restore focus to textarea after stopping
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const deleteConversation = async (id: string) => {
    if (id !== 'welcome') {
      await conversationService.deleteConversation(id);
    }
    
    const newConversations = conversations.filter(conv => conv.id !== id);
    setConversations(newConversations);
    
    if (currentConversation?.id === id) {
      setCurrentConversation(newConversations[0] || null);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const copyToClipboard = async (messageId: string, content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      // Reset the copied state after 2 seconds
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const startEditingMessage = (messageId: string, content: string) => {
    setEditingMessageId(messageId);
    setEditingContent(content);
  };

  const cancelEditingMessage = () => {
    setEditingMessageId(null);
    setEditingContent('');
  };

  const saveEditedMessage = async (messageId: string) => {
    if (!currentConversation || !editingContent.trim()) return;

    const messageIndex = currentConversation.messages.findIndex(msg => msg.id === messageId);
    if (messageIndex === -1) return;

    const originalUserMessage = currentConversation.messages[messageIndex];
    
    // Find the corresponding assistant message (next message with role 'assistant')
    const originalAssistantMessage = currentConversation.messages
      .slice(messageIndex + 1)
      .find(msg => msg.role === 'assistant');

    // Create new user message with edited content
    const editedUserMessage: Message = {
      ...originalUserMessage,
      content: editingContent.trim(),
      timestamp: new Date(),
    };

    // Create original branch if it doesn't exist
    if (!conversationBranches[messageId]) {
      const originalBranch: ConversationBranch = {
        id: `${messageId}-original`,
        userMessage: originalUserMessage,
        assistantMessage: originalAssistantMessage,
        timestamp: originalUserMessage.timestamp,
      };

      setConversationBranches(prev => ({
        ...prev,
        [messageId]: {
          branches: [originalBranch],
          activeIndex: 0
        }
      }));
    }

    // Update the conversation with the edited message (replace user message, remove assistant response)
    const updatedMessages = [...currentConversation.messages];
    updatedMessages[messageIndex] = editedUserMessage;

    // Remove all assistant messages after this user message since we need new responses
    const assistantMessagesToRemove = [];
    for (let i = messageIndex + 1; i < updatedMessages.length; i++) {
      if (updatedMessages[i].role === 'assistant') {
        assistantMessagesToRemove.push(i);
      } else {
        break; // Stop at the next user message
      }
    }

    // Remove assistant messages in reverse order to maintain indices
    assistantMessagesToRemove.reverse().forEach(index => {
      updatedMessages.splice(index, 1);
    });

    const updatedConversation = {
      ...currentConversation,
      messages: updatedMessages,
      updatedAt: new Date(),
    };

    setCurrentConversation(updatedConversation);
    setConversations(prev => 
      prev.map(conv => conv.id === currentConversation.id ? updatedConversation : conv)
    );

    setEditingMessageId(null);
    setEditingContent('');

    // Send new request with the edited message
    await generateResponseForEditedMessage(editedUserMessage, messageId);
  };

  const generateResponseForEditedMessage = async (userMessage: Message, originalMessageId: string) => {
    if (!currentConversation || isStreaming) return;

    setIsStreaming(true);

    // Create abort controller for this request
    const abortController = new AbortController();
    setStreamAbortController(abortController);

    // Create streaming message immediately
    const streamingMessage: Message = {
      id: Date.now().toString(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      model: selectedModel,
      isStreaming: true,
    };

    const conversationWithStreaming = {
      ...currentConversation,
      messages: [...currentConversation.messages, streamingMessage],
    };

    flushSync(() => {
      setCurrentConversation(conversationWithStreaming);
      setConversations(prev => 
        prev.map(conv => conv.id === currentConversation.id ? conversationWithStreaming : conv)
      );
    });

    try {
      // Get conversation history for multi-turn context (exclude the new streaming message)
      const conversationHistory = currentConversation.messages
        .filter(msg => msg.id !== streamingMessage.id && msg.id !== 'welcome-msg')
        .slice(); // Get all previous messages for context

      const response = await apiService.chat(
        userMessage.content,
        selectedModel,
        currentConversation.id,
        conversationHistory.length > 0 ? conversationHistory.map(msg => ({
          ...msg,
          timestamp: msg.timestamp.toISOString()
        })) : undefined,
        user.isGuest,
        { signal: abortController.signal }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let accumulatedContent = '';
      const FLUSH_INTERVAL_MS = 120;
      let lastFlushTime = 0;
      const rafIdRef = { current: null as number | null };
      const pendingContentRef = { current: '' };

      const currentConvId = currentConversation.id;

      const scheduleRafFlush = () => {
        if (rafIdRef.current !== null) return;
        rafIdRef.current = requestAnimationFrame(() => {
          rafIdRef.current = null;
          const contentToApply = pendingContentRef.current;
          const updatedStreamingMessage = {
            ...streamingMessage,
            content: contentToApply,
          };

          const finalConversation = {
            ...conversationWithStreaming,
            messages: conversationWithStreaming.messages.map(msg => 
              msg.id === streamingMessage.id ? updatedStreamingMessage : msg
            ),
            updatedAt: new Date(),
          };

          setCurrentConversation(finalConversation);
          setConversations(prev => prev.map(conv => (
            conv.id === currentConvId ? finalConversation : conv
          )));

          if (isUserNearBottomRef.current && Date.now() >= suppressAutoScrollUntilRef.current) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
          }
        });
      };
      
      // Process stream chunks
      let streamCompleted = false;
      while (true) {
        if (abortController.signal.aborted) {
          console.log('Branch stream aborted by user');
          break;
        }

        const { done, value } = await reader.read();
        if (done) {
          console.log('Branch stream completed naturally');
          streamCompleted = true;
          break;
        }

        const chunk = decoder.decode(value, { stream: true });

        if (chunk) {
          accumulatedContent += chunk;
          pendingContentRef.current = accumulatedContent;
          const now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
          if (now - lastFlushTime >= FLUSH_INTERVAL_MS) {
            lastFlushTime = now;
            scheduleRafFlush();
          }
        }
      }

      // Final flush to ensure all content is displayed
      if (accumulatedContent && pendingContentRef.current !== accumulatedContent) {
        pendingContentRef.current = accumulatedContent;
        scheduleRafFlush();
      }

      // Mark streaming as complete and create new branch - always stop streaming state first
      setIsStreaming(false);
      
      if (streamCompleted && !abortController.signal.aborted) {
        console.log('Finalizing completed branch stream with content length:', accumulatedContent.length);
        
        const completedMessage = {
          ...streamingMessage,
          content: accumulatedContent,
          isStreaming: false,
        };

        const completedConversation = {
          ...conversationWithStreaming,
          messages: conversationWithStreaming.messages.map(msg => 
            msg.id === streamingMessage.id ? completedMessage : msg
          ),
          updatedAt: new Date(),
        };

        // Create new branch with the edited query and new response
        const newBranch: ConversationBranch = {
          id: `${originalMessageId}-${Date.now()}`,
          userMessage,
          assistantMessage: completedMessage,
          timestamp: new Date(),
        };

        // Force synchronous updates to ensure immediate re-render
        flushSync(() => {
          // Add the new branch and set it as active
          setConversationBranches(prev => ({
            ...prev,
            [originalMessageId]: {
              branches: [...(prev[originalMessageId]?.branches || []), newBranch],
              activeIndex: (prev[originalMessageId]?.branches.length || 0)
            }
          }));

          setCurrentConversation(completedConversation);
          setConversations(prev => 
            prev.map(conv => conv.id === currentConvId ? completedConversation : conv)
          );
        });

        // Also update any existing branch data to ensure consistency
        setTimeout(() => {
          setConversationBranches(prev => {
            const updated = { ...prev };
            Object.keys(updated).forEach(key => {
              updated[key] = {
                ...updated[key],
                branches: updated[key].branches.map(branch => ({
                  ...branch,
                  assistantMessage: branch.assistantMessage ? {
                    ...branch.assistantMessage,
                    isStreaming: false
                  } : branch.assistantMessage
                }))
              };
            });
            return updated;
          });
        }, 50);

        console.log('Completed branch message isStreaming:', completedMessage.isStreaming);
      } else {
        console.log('Finalizing aborted/interrupted branch stream');
        
        const abortedMessage = {
          ...streamingMessage,
          content: accumulatedContent + (abortController.signal.aborted ? '\n\n[Generation stopped by user]' : '\n\n[Generation interrupted]'),
          isStreaming: false,
        };

        const abortedConversation = {
          ...conversationWithStreaming,
          messages: conversationWithStreaming.messages.map(msg => 
            msg.id === streamingMessage.id ? abortedMessage : msg
          ),
          updatedAt: new Date(),
        };

        // Force synchronous update to ensure immediate re-render
        flushSync(() => {
          setCurrentConversation(abortedConversation);
          setConversations(prev => 
            prev.map(conv => conv.id === currentConvId ? abortedConversation : conv)
          );
        });

        console.log('Aborted branch message isStreaming:', abortedMessage.isStreaming);
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was aborted by user');
        return;
      }
      console.error('Error sending message:', error);
      // Handle error similar to the main sendMessage function
    } finally {
      setIsStreaming(false);
      setStreamAbortController(null);
      
      // Ensure all streaming state is cleared with a timeout safeguard
      setTimeout(() => {
        setIsStreaming(false);
        
        // Force a final state check and re-render for branch regeneration
        setCurrentConversation(prev => {
          if (!prev) return prev;
          const updatedMessages = prev.messages.map(msg => 
            msg.isStreaming ? { ...msg, isStreaming: false } : msg
          );
          return { ...prev, messages: updatedMessages };
        });
      }, 100);
    }
  };

  const switchToBranch = (messageId: string, branchIndex: number) => {
    if (!conversationBranches[messageId]) return;
    
    setConversationBranches(prev => ({
      ...prev,
      [messageId]: {
        ...prev[messageId],
        activeIndex: branchIndex
      }
    }));
  };

  const hasBranches = (messageId: string): boolean => {
    const branchData = conversationBranches[messageId];
    return branchData && branchData.branches.length > 1;
  };

  if (isLoadingConversations) {
    return (
      <div className="flex h-screen bg-background text-foreground items-center justify-center">
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Loading your conversations...</h2>
          <p className="text-muted-foreground">Please wait while we set up your workspace.</p>
        </motion.div>
      </div>
    );
  }

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex h-screen w-full bg-background text-foreground">
        {/* App Sidebar */}
        <Sidebar variant="sidebar" collapsible="icon" className="border-r border-border">
          <SidebarHeader className="border-b border-border bg-background">
            <div className="flex items-center space-x-2 cursor-pointer" onClick={() => window.open('/', '_blank')}>
              <img 
                src={checkThatLogo}
                alt="CheckThat AI Logo"
                className="h-6 w-auto"
              />
              <div className="truncate text-lg font-bold">
                CheckThat<span className="text-primary"> AI</span>
              </div>
            </div>
          </SidebarHeader>

          <SidebarContent className="bg-background">
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton 
                      onClick={createNewConversation}
                      tooltip="New Chat"
                      className="bg-sidebar-primary text-primary hover:bg-accent hover:text-accent-foreground"
                    >
                      <Plus className="w-4 h-4 text-yellow-300" />
                      <span className='text-yellow-300'>New Chat</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarGroupLabel className="text-muted-foreground">
                    <History className="w-4 h-4 mr-2" />
                    Recent Chats
                  </SidebarGroupLabel>
                  <AnimatePresence>
                    {conversations.map((conv) => (
                      <motion.div
                        key={conv.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.2 }}
                      >
                        <SidebarMenuItem>
                          <SidebarMenuButton
                            onClick={() => setCurrentConversation(conv)}
                            isActive={currentConversation?.id === conv.id}
                            tooltip={conv.title}
                            className="text-slate-300 hover:bg-accent hover:text-accent-foreground data-[active=true]:bg-accent data-[active=true]:text-white"
                          >
                            <MessageSquare className="w-4 h-4" />
                            <span>{conv.title}</span>
                          </SidebarMenuButton>
                          <SidebarMenuAction
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteConversation(conv.id);
                            }}
                            showOnHover
                            className="text-muted-foreground hover:text-destructive hover:bg-destructive/20"
                          >
                            <Trash2 className="w-4 h-4" />
                          </SidebarMenuAction>
                        </SidebarMenuItem>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarFooter className='border-t border-sidebar-border bg-background sticky bottom-0 z-30 py-1.5 group-data-scrolled-from-end/scrollport:shadow-(--sharp-edge-bottom-shadow) empty:hidden'>
            <SidebarMenu>
              <SidebarMenuItem>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <SidebarMenuButton
                      size="lg"
                      tooltip={`${user.firstName} ${user.lastName}`}
                      className="group hoverable gap-2 bg-black hover:bg-card border-0 hover:border-0 data-[state=open]:hover:border-0 data-[state=open]:bg-card data-[state=open]:text-sidebar-accent-foreground no-focus-ring"
                      style={{
                        backgroundColor: 'black',
                        outline: 'none',
                        boxShadow: 'none',
                      } as React.CSSProperties}
                    >
                      <div className="flex items-center justify-center group-disabled:opacity-50 group-data-disabled:opacity-50 icon-lg">
                        <div className="flex overflow-hidden rounded-full select-none bg-gray-500/30 h-6 w-6 shrink-0">
                          <UserAvatar 
                            user={user} 
                            className="h-6 w-6 shrink-0 object-cover rounded-full"
                            fallbackClassName="h-6 w-6 shrink-0 object-cover rounded-full"
                          />
                        </div>
                      </div>
                      <div className="min-w-0">
                        <div className="flex min-w-0 px-2 grow items-center gap-2.5 group-data-no-contents-gap:gap-0">
                          <div className="truncate text-slate-300 font-normal text-sm">
                            {user.isGuest ? 'Guest User' : `${user.firstName} ${user.lastName}`}
                          </div>
                        </div>
                      </div>
                    </SidebarMenuButton>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-sm border border-background shadow-xl bg-card no-focus-ring"
                    side="bottom"
                    align="end"
                    sideOffset={4}
                  >
                    {/* Account Section - Hidden for guests */}
                    {!user.isGuest && (
                      <DropdownMenuLabel className="p-0 font-normal">
                        <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm w-full 
                        bg-transparent hover:bg-muted-foreground/10 hover:text-accent-foreground rounded-sm transition-colors cursor-pointer"
                          onClick={() => window.open(`/account`, '_blank')}
                        >
                          <div className="flex overflow-hidden rounded-full select-none bg-gray-500/30 h-8 w-8 shrink-0">
                            <UserAvatar 
                              user={user} 
                              className="h-8 w-8 shrink-0 object-cover rounded-full"
                              fallbackClassName="h-8 w-8 shrink-0 object-cover rounded-full"
                            />
                          </div>
                          <div className="grid flex-1 text-left text-sm leading-tight">
                            <span className="truncate font-semibold">
                              Account
                            </span>
                          </div>
                        </div>
                      </DropdownMenuLabel>
                    )}
                    
                    {!user.isGuest && <DropdownMenuSeparator />}
                    
                    {/* Settings - Hidden for guests */}
                    {!user.isGuest && (
                      <DropdownMenuItem onClick={() => window.open(`/settings`, '_blank')} className="cursor-pointer hover:bg-muted-foreground/10">
                        <Settings className="h-4 w-4"/>
                        Settings
                      </DropdownMenuItem>
                    )}
                    
                    {/* Documentation - Always visible */}
                    <DropdownMenuItem onClick={() => window.open(`/docs`, '_blank')} className="cursor-pointer bg-card rounded-md hover:bg-muted-foreground/10">
                      <BookOpen className="h-4 w-4" />
                      Documentation
                    </DropdownMenuItem>
                    
                    <DropdownMenuSeparator />
                    
                    {/* Log in for guests, Log out for authenticated users */}
                    {user.isGuest ? (
                      <DropdownMenuItem onClick={() => setShowLoginDialog(true)} className="cursor-pointer hover:bg-muted-foreground/10">
                        <LogIn className="h-4 w-4" />
                        Log in
                      </DropdownMenuItem>
                    ) : (
                      <DropdownMenuItem onClick={async () => {
                        try {
                          const { error } = await supabase.auth.signOut();
                          if (error) {
                            console.error('Logout error:', error);
                            return;
                          }
                          
                          // Clear user data from localStorage
                          localStorage.removeItem('supabase_user');
                          localStorage.removeItem('user_info');
                          
                          console.log('User logged out successfully');
                          // The app should handle redirect via auth state change
                        } catch (error) {
                          console.error('Logout error:', error);
                        }
                      }} className="cursor-pointer hover:bg-muted-foreground/10">
                        <LogOut className="h-4 w-4" />
                        Log out
                      </DropdownMenuItem>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarFooter>
        </Sidebar>

        {/* Main Content */}
        <SidebarInset className="flex flex-col bg-background h-screen">
          {/* Header - Fixed at top */}
          <div className="flex items-center gap-2 px-4 py-2 bg-background flex-shrink-0">
            <Tooltip>
              <TooltipTrigger asChild>
                <SidebarTrigger className="-ml-1 text-slate-300" />
              </TooltipTrigger>
              <TooltipContent side="bottom" align="start">
                <p>Toggle sidebar (⌘B)</p>
              </TooltipContent>
            </Tooltip>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">{currentConversation?.title || 'Chat'}</span>
            </div>
            <div className="ml-auto flex items-center gap-2">
              <Badge variant="secondary" className="bg-chart-1 border-border">
                <span className='text-foreground font-medium'>{models.find(m => m.value === selectedModel)?.label}</span>
              </Badge>
              {/* Theme Toggle */}
              <ModeToggle />
            </div>
          </div>

          {/* Chat Container - Flexible layout with conditional centering */}
          <motion.div 
            layout
            className={`flex-1 flex flex-col h-full overflow-hidden ${isInitialState ? 'justify-center' : ''}`}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            {/* Chat Messages - Scrollable area - Hide in initial state */}
            {!isInitialState && (
              <div className="flex-1 overflow-y-auto">
                <div className="relative h-full">
                  <ScrollArea className="h-full p-4" viewportRef={viewportRef} onViewportScroll={handleViewportScroll}>
                <div className="max-w-4xl mx-auto space-y-6">
                  <AnimatePresence>
                    {currentConversation?.messages
                      .filter(msg => msg.id !== 'welcome-msg') // Filter out welcome message
                        .reduce((acc: React.ReactElement[], msg, index, array) => {
                          // Group user messages with their following assistant messages
                          if (msg.role === 'user') {
                            const nextMessage = array[index + 1];
                            const isAssistantNext = nextMessage?.role === 'assistant';
                            const isEditing = editingMessageId === msg.id;
                            const branchData = conversationBranches[msg.id];
                            const showCarousel = hasBranches(msg.id);

                            acc.push(
                              <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ duration: 0.15 }}
                                className="w-full"
                              >
                                {showCarousel && branchData ? (
                                  <div className="space-y-6">
                                    {/* Display current branch */}
                                    {(() => {
                                      const currentBranch = branchData.branches[branchData.activeIndex];
                                      return (
                                        <div>
                                          {/* User Message */}
                                          <div className="flex gap-4 justify-end justify-items-end group">
                                            <div className="flex flex-col gap-2 max-w-[80%] w-fit ml-auto">
                                              <div className="rounded-lg p-4 dark:bg-neutral-900 bg-muted text-black dark:text-primary-foreground w-fit">
                                                <div className="text-sm prose prose-slate dark:prose-invert max-w-none">
                                                  <div className="whitespace-pre-wrap">{currentBranch.userMessage.content}</div>
                                                </div>
                                              </div>
                                              
                                              {/* Combined navigation and action buttons */}
                                              <div className="flex items-center justify-between mt-2 mb-2">
                                                {/* Edit and copy buttons on the left */}
                                                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                  <button
                                                    onClick={() => copyToClipboard(currentBranch.userMessage.id, currentBranch.userMessage.content)}
                                                    className="h-8 px-2 text-slate-700 dark:text-muted-foreground transition-colors cursor-pointer text-xs flex items-center hover:bg-accent rounded"
                                                  >
                                                    {copiedMessageId === currentBranch.userMessage.id ? (
                                                      <>
                                                        <Check className="w-3 h-3 mr-1" />
                                                        <span>Copied</span>
                                                      </>
                                                    ) : (
                                                      <>
                                                        <Copy className="w-3 h-3 mr-1" />
                                                      </>
                                                    )}
                                                  </button>
                                                  
                                                  <button
                                                    onClick={() => startEditingMessage(msg.id, currentBranch.userMessage.content)}
                                                    className="h-8 px-2 text-slate-700 dark:text-muted-foreground transition-colors cursor-pointer text-xs flex items-center hover:bg-accent rounded"
                                                  >
                                                    <Edit3 className="w-3 h-3 mr-1" />
                                                  </button>
                                                </div>

                                                {/* Carousel navigation in the center */}
                                                <div className="flex items-center gap-3">
                                                  <div
                                                    onClick={() => switchToBranch(msg.id, Math.max(0, branchData.activeIndex - 1))}
                                                    className="p-1.5 rounded-full hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
                                                  >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                                    </svg>
                                                  </div>
                                                  
                                                  <span className="text-sm text-foreground px-3 py-1">
                                                    {branchData.activeIndex + 1} / {branchData.branches.length}
                                                  </span>
                                                  
                                                  <div
                                                    onClick={() => switchToBranch(msg.id, Math.min(branchData.branches.length - 1, branchData.activeIndex + 1))}
                                                    className="p-1.5 rounded-full hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
                                                  >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                    </svg>
                                                  </div>
                                                </div>

                                                
                                              </div>
                                            </div>
                                          </div>

                                          {/* Assistant Message */}
                                          {currentBranch.assistantMessage && (
                                            <div className="flex gap-4 justify-start group">
                                              <div className="flex max-w-[80%] justify-start">
                                                <div className="flex flex-col gap-2">
                                                  <StreamingMessageWrapper 
                                                    isStreaming={currentBranch.assistantMessage.isStreaming}
                                                    isInitialLoad={currentBranch.assistantMessage.content === '' && currentBranch.assistantMessage.isStreaming}
                                                  >
                                                    <div className="text-sm prose prose-slate dark:prose-invert max-w-none">
                                                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                        {currentBranch.assistantMessage.content}
                                                      </ReactMarkdown>
                                                      {currentBranch.assistantMessage.isStreaming && currentBranch.assistantMessage.content && <BlinkingCursor />}
                                                    </div>
                                                  </StreamingMessageWrapper>
                                                  
                                                  {currentBranch.assistantMessage && currentBranch.assistantMessage.content && !currentBranch.assistantMessage.isStreaming && (
                                                    <div className="flex justify-start opacity-0 group-hover:opacity-100 transition-opacity">
                                                      <button
                                                        onClick={() => copyToClipboard(currentBranch.assistantMessage!.id, currentBranch.assistantMessage!.content)}
                                                        className="h-8 px-2 text-slate-700 dark:text-muted-foreground transition-colors cursor-pointer text-xs flex items-center hover:bg-accent rounded"
                                                      >
                                                        {copiedMessageId === currentBranch.assistantMessage.id ? (
                                                          <>
                                                            <Check className="w-3 h-3 mr-1" />
                                                            <span>Copied</span>
                                                          </>
                                                        ) : (
                                                          <>
                                                            <Copy className="w-3 h-3 mr-1" />
                                                          </>
                                                        )}
                                                      </button>
                                                    </div>
                                                  )}
                                                </div>
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      );
                                    })()}
                                  </div>
                                ) : (
                                  <div className="space-y-6">
                                    {/* Regular user message without carousel */}
                                    <div className="flex gap-4 justify-end group">
                                      <div className="flex flex-col gap-2 max-w-[80%] w-fit ml-auto">
                                        <div className="rounded-lg p-4 dark:bg-neutral-900 bg-muted text-black dark:text-primary-foreground w-fit">
                                          <div className="text-sm prose prose-slate dark:prose-invert max-w-none">
                                            {isEditing ? (
                                              <div className="flex flex-col gap-2">
                                                <Textarea
                                                  value={editingContent}
                                                  onChange={(e) => setEditingContent(e.target.value)}
                                                  className="min-h-[60px] resize-none"
                                                  autoFocus
                                                />
                                                <div className="flex gap-2 justify-end">
                                                  <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={cancelEditingMessage}
                                                  >
                                                    <XIcon className="w-3 h-3 mr-1" />
                                                    Cancel
                                                  </Button>
                                                  <Button
                                                    size="sm"
                                                    onClick={() => saveEditedMessage(msg.id)}
                                                    disabled={!editingContent.trim()}
                                                  >
                                                    <Save className="w-3 h-3 mr-1" />
                                                    Save & Send
                                                  </Button>
                                                </div>
                                              </div>
                                            ) : (
                                              <div className="whitespace-pre-wrap">{msg.content}</div>
                                            )}
                                          </div>
                                        </div>
                                        
                                        {!isEditing && msg.content && (
                                          <div className="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                                            <div className="flex gap-1">
                                              <button
                                                onClick={() => copyToClipboard(msg.id, msg.content)}
                                                className="h-8 px-2 text-slate-700 dark:text-muted-foreground transition-colors cursor-pointer text-xs flex items-center hover:bg-accent rounded"
                                              >
                                                {copiedMessageId === msg.id ? (
                                                  <>
                                                    <Check className="w-3 h-3 mr-1" />
                                                    <span>Copied</span>
                                                  </>
                                                ) : (
                                                  <>
                                                    <Copy className="w-3 h-3 mr-1" />
                                                  </>
                                                )}
                                              </button>
                                              
                                              <button
                                                onClick={() => startEditingMessage(msg.id, msg.content)}
                                                className="h-8 px-2 text-slate-700 dark:text-muted-foreground transition-colors cursor-pointer text-xs flex items-center hover:bg-accent rounded"
                                              >
                                                <Edit3 className="w-3 h-3 mr-1" />
                                              </button>
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>

                                    {/* Assistant message that follows */}
                                    {isAssistantNext && (
                                      <div className="flex gap-4 justify-start group">
                                        <div className="flex max-w-full justify-start">
                                          <div className="flex flex-col gap-2">
                                            <StreamingMessageWrapper 
                                              isStreaming={nextMessage.isStreaming}
                                              isInitialLoad={nextMessage.content === '' && nextMessage.isStreaming}
                                            >
                                              <div className="text-sm prose prose-slate dark:prose-invert max-w-none">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                  {nextMessage.content}
                                                </ReactMarkdown>
                                                {nextMessage.isStreaming && nextMessage.content && <BlinkingCursor />}
                                              </div>
                                            </StreamingMessageWrapper>
                                            
                                            {nextMessage.content && !nextMessage.isStreaming && (
                                              <div className="flex justify-start opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                  onClick={() => copyToClipboard(nextMessage.id, nextMessage.content)}
                                                  className="h-8 px-2 text-slate-700 dark:text-muted-foreground transition-colors cursor-pointer text-xs flex items-center hover:bg-accent rounded"
                                                >
                                                  {copiedMessageId === nextMessage.id ? (
                                                    <>
                                                      <Check className="w-3 h-3 mr-1" />
                                                      <span>Copied</span>
                                                    </>
                                                  ) : (
                                                    <>
                                                      <Copy className="w-3 h-3 mr-1" />
                                                    </>
                                                  )}
                                                </button>
                                              </div>
                                            )}
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                )}
                              </motion.div>
                            );
                          }
                          
                          // Skip assistant messages that are already handled with their user messages
                          return acc;
                        }, [])}
                </AnimatePresence>

                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
                  {!isUserNearBottom && (
                    <div className="absolute right-6 bottom-6">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => {
                          messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
                        }}
                        className="shadow-md"
                      >
                        <ArrowDown className="h-4 w-4 mr-1 text-white" />
                      </Button>
                    </div>
                  )}
                </div>
            </div>
            )}

            {/* Input Area - Centered in initial state, fixed at bottom after conversation starts */}
            <div className={`flex-shrink-0 px-4 pb-4 bg-background ${isInitialState ? 'flex justify-center items-center' : ''}`}>
              <div className={`${isInitialState ? 'w-full max-w-2xl' : 'max-w-4xl mx-auto'}`}>
                {/* Welcome Message - Only show in initial state */}
                {isInitialState && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8 text-center"
                  >
                    <h1 className="text-3xl font-bold text-foreground mb-4">
                      Welcome to CheckThat AI
                    </h1>
                    <p className="text-lg text-muted-foreground mb-6">
                      {user.isGuest 
                        ? "Start chatting with our free Llama 3.3 70B model. No sign-up required!"
                        : `Hello ${user.firstName}! Ready to normalize and fact-check claims?`
                      }
                    </p>
                    {user.isGuest && (
                      <div className="mb-6 p-4 rounded-lg bg-muted border border-border">
                        <p className="text-sm text-muted-foreground">
                          🎉 <strong>You're in Guest Mode!</strong> Try our free AI model or{' '}
                          <button 
                            onClick={() => setShowLoginDialog(true)}
                            className="text-primary hover:underline"
                          >
                            sign in
                          </button>
                          {' '}for premium features.
                        </p>
                      </div>
                    )}
                  </motion.div>
                )}
                {/* File Upload Area */}
                <AnimatePresence>
                  {uploadedFiles.length > 0 && (
                    <motion.div 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mb-4 p-3 bg-muted rounded-lg border border-border"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Upload className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-foreground">Uploaded Files:</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <AnimatePresence>
                          {uploadedFiles.map((file, index) => (
                            <motion.div 
                              key={index}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              exit={{ opacity: 0, scale: 0.8 }}
                              className="flex items-center gap-2 bg-background px-3 py-1 rounded-full text-sm border border-border"
                            >
                              <span className="text-foreground">{file.name}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeFile(index)}
                                className="h-4 w-4 p-0 hover:bg-destructive/20 hover:text-destructive"
                              >
                                <X className="w-3 h-3" />
                              </Button>
                            </motion.div>
                          ))}
                        </AnimatePresence>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".txt,.pdf,.doc,.docx,.csv,.json"
                />

                <div className="border border-border/60 bg-muted/40 rounded-2xl px-3 py-3 shadow-sm">
                  {/* Text input */}
                    <Textarea
                      ref={textareaRef}
                      className="w-full text-foreground resize-none border-0 min-h-7 max-h-[220px] py-2 bg-transparent dark:bg-transparent focus:border-0 focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none placeholder:text-muted-foreground [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] overflow-y-auto"
                      placeholder="Type or paste your input text here..."
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={isStreaming}
                    />
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex items-center gap-2">
                    {/* Attachments */}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => !user?.isGuest && fileInputRef.current?.click()}
                            disabled={user?.isGuest}
                            className={`${
                              user?.isGuest
                                ? 'text-muted-foreground cursor-not-allowed opacity-50'
                                : 'text-slate-300 hover:bg-transparent cursor-pointer'
                            } rounded-full h-10 w-10 p-0 bg-transparent`}
                          >
                            <Paperclip className="w-4 h-4" />
                          </Button>
                        </div>
                      </TooltipTrigger>
                      {user?.isGuest && (
                        <TooltipContent side="top" align="center">
                          <p>File upload is not available for free models</p>
                        </TooltipContent>
                      )}
                    </Tooltip>

                    {/* Model select (compact) */}
                        <Select value={selectedModel} onValueChange={handleModelChange}>
                      <SelectTrigger className="min-w-[220px] h-10 rounded-xl bg-transparent dark:bg-transparent hover:bg-transparent border border-border/60 text-slate-300">
                        <SelectValue placeholder="Auto" />
                          </SelectTrigger>
                      <SelectContent className=" border-border max-h-[30vh] overflow-y-auto shadow-lg">
                            {/* OpenAI Models */}
                            <SelectGroup>
                          <SelectLabel className="font-semibold text-xs text-green-500 uppercase tracking-wider">OpenAI</SelectLabel>
                              {models.filter(m => m.provider === 'OpenAI').map((model) => (
                                <SelectItem key={model.value} value={model.value} className="text-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium">{model.label}</span>
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectGroup>
                            <SelectSeparator className="bg-border" />
                            {/* Anthropic Models */}
                            <SelectGroup>
                          <SelectLabel className="font-semibold text-xs dark:text-claude uppercase tracking-wider">Anthropic</SelectLabel>
                              {models.filter(m => m.provider === 'Anthropic').map((model) => (
                                <SelectItem key={model.value} value={model.value} className="text-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium">{model.label}</span>
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectGroup>
                            <SelectSeparator className="bg-border" />
                            {/* Google Models */}
                            <SelectGroup>
                          <SelectLabel className="font-semibold text-xs text-blue-800 uppercase tracking-wider">Google AI</SelectLabel>
                              {models.filter(m => m.provider === 'Google').map((model) => (
                                <Tooltip key={model.value}>
                                  <TooltipTrigger asChild>
                                    <SelectItem value={model.value} className="text-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer">
                                      <div className="flex items-center gap-2">
                                        <span className="font-medium">{model.label}</span>
                                      </div>
                                    </SelectItem>
                                  </TooltipTrigger>
                                  <TooltipContent side="left" className="max-w-xs">
                                    <p className="text-sm">Available for free till Sep 15. Rate limits apply: 10 Req/min</p>
                                  </TooltipContent>
                                </Tooltip>
                              ))}
                            </SelectGroup>
                            <SelectSeparator className="bg-border" />
                            {/* xAI Models */}
                            <SelectGroup>
                          <SelectLabel className="font-semibold text-xs text-amber-500 uppercase tracking-wider">xAI</SelectLabel>
                              {models.filter(m => m.provider === 'xAI').map((model) => (
                                <SelectItem key={model.value} value={model.value} className="text-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium">{model.label}</span>
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectGroup>
                            <SelectSeparator className="bg-border" />
                            {/* Together AI Models */}
                            <SelectGroup>
                          <SelectLabel className="font-semibold text-xs text-cyan-700 uppercase tracking-wider">Together AI (Free)</SelectLabel>
                              {models.filter(m => m.provider === 'Together AI').map((model) => (
                                <SelectItem key={model.value} value={model.value} className="text-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium">{model.label}</span>
                                {!model.isPaid && (
                                  <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 px-1.5 py-0.5 rounded">FREE</span>
                                )}
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                        
                            </div>

                    {/* Send / Stop */}
                    <motion.div className="ml-auto" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                          {isStreaming ? (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  onClick={stopStreaming}
                              className="rounded-xl bg-destructive/20 hover:bg-destructive/30 text-destructive-foreground h-11 w-11 p-0"
                                >
                                  <Square className="h-4 w-4" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent side="top">
                                <p>Stop streaming response</p>
                              </TooltipContent>
                            </Tooltip>
                          ) : (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  onClick={sendMessage}
                                  disabled={!message.trim() || isStreaming}
                              className="rounded-xl bg-muted/40 hover:bg-muted/60 text-foreground h-11 w-11 p-0 disabled:opacity-50"
                                >
                                  <ArrowUpIcon className="h-4 w-4" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent side="top">
                                <p>{!message.trim() ? 'Type a message to send' : 'Send message (Enter)'}</p>
                              </TooltipContent>
                            </Tooltip>
                          )}
                        </motion.div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </SidebarInset>

        {/* Sign In Dialog for Guest Users */}
        <SignInDialog
          open={showSignInDialog}
          onOpenChange={setShowSignInDialog}
          modelName={models.find(m => m.value === pendingModel)?.label || ''}
          onSuccess={handleSignInSuccess}
        />

        {/* Login Dialog for Guest Users from Dropdown */}
        <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
          <DialogContent className="sm:max-w-[425px]">
            <Login onSuccess={handleLoginSuccess} />
          </DialogContent>
        </Dialog>

        {/* Feedback Popup */}
        <ChatFeedbackPopup
          isOpen={showFeedbackPopup}
          onClose={() => setShowFeedbackPopup(false)}
          onSubmitFeedback={() => setShowFeedbackPopup(false)}
        />
      </div>
      {/* Toast notifications */}
      <Toaster />
    </SidebarProvider>
  );
};

export default ChatInterface;