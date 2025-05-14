import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatMarkdown(content: string): string {
  // Replace markdown-like bold text with HTML strong tags
  return content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

// Format file size
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Validate file type
export function isValidFileType(file: File): boolean {
  const allowedTypes = [
    'text/csv',
    'application/vnd.ms-excel',
    'application/json',
    'application/x-jsonlines',
    'text/plain'
  ];
  
  // Check both MIME type and file extension
  return allowedTypes.includes(file.type) || 
         file.name.endsWith('.csv') ||
         file.name.endsWith('.json') ||
         file.name.endsWith('.jsonl') ||
         file.name.endsWith('.txt');
}
