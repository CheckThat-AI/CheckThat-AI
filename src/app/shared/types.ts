// Define types for claim normalization app

// Chat message type
export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'system' | 'assistant';
  timestamp: Date;
  files?: File[];
  isStreaming?: boolean;
}

// Model options
export type ModelOption = 'grok-3-latest' | 'claude-3.7-sonnet-latest' | 'gpt-4o-2024-11-20' | 'gpt-4.1-2025-04-14' | 'gpt-4.1-nano-2025-04-14' | 'gemini-2.5-pro-preview-05-06' | 'gemini-2.5-flash-preview-04-17' | 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free';

// Prompt style options
export type PromptStyleOption = 'Zero-shot' | 'Few-shot' | 'Zero-shot-CoT' | 'Few-shot-CoT';

// Evaluation form data
export interface EvaluationData {
  file: File | null;
  selectedModels: ModelOption[];
  selectedPromptStyles: PromptStyleOption[];
  customPrompt?: string;
}

// API response types
export interface NormalizationResponse {
  normalizedClaim: string;
  model: string;
  prompt_style: string;
  meteor_score: number;
}

export interface EvaluationResponse {
  success: boolean;
  message: string;
  id?: string;
}

// Progress response for tracking backend operations
export interface ProgressResponse {
  progress: number; // Progress percentage (0-100)
  status: 'pending' | 'processing' | 'completed' | 'error';
  message?: string;
}

// Evaluation results data
export interface MeteorScore {
  model: string;
  promptStyle: string;
  score: number;
}

export interface EvaluationResults {
  scores: MeteorScore[];
  timestamp: Date;
}

// File upload response
export interface FileUploadResponse {
  fileUrl: string;
  fileId: string;
  message: string;
}

export interface ErrorResponse {
  detail: string;
}
