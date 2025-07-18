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
export type ModelOption = 'grok-3' | 'grok-3-mini' | 'grok-3-mini-fast' | 'claude-sonnet-4-20250514' | 'claude-opus-4-20250514' | 'gpt-4o-2024-11-20' | 'gpt-4.1-2025-04-14' | 'gpt-4.1-nano-2025-04-14' | 'gemini-2.5-pro-preview-05-06' | 'gemini-2.5-flash-preview-04-17' | 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free';

// Prompt style options
export type PromptStyleOption = 'Zero-shot' | 'Few-shot' | 'Zero-shot-CoT' | 'Few-shot-CoT';

// Field mapping for dataset columns
export interface FieldMapping {
  inputText: string | null;                // The input provided to the model
  expectedOutput: string | null;           // Reference/expected output for reference-based metrics
  actualOutput?: string | null;            // Model's actual output for evaluation
  context?: string | null;                 // Context information for the evaluation
  retrievalContext?: string | null;        // Context used for retrieval-based metrics
  metadata?: string | null;                // Additional metadata field
  comments?: string | null;                // Comments or notes field
  // Prompt information for dataset creation
  promptInfo?: {
    isCustom: boolean;                     // Whether a custom prompt was used
    promptContent?: string | null;         // Full custom prompt text if custom=true
    promptStyleId?: PromptStyleOption | null; // Prompt style identifier if custom=false
  } | null;
}

// Evaluation form data
export type EvaluationData = {
  file: File | null;
  selectedModels: ModelOption[];
  selectedPromptStyles: PromptStyleOption[];
  customPrompt?: string | null;
  crossRefineModel?: ModelOption | null;
  fieldMapping?: FieldMapping | null;
  evalMetric?: string | null;
};

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
