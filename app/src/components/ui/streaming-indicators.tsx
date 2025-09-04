import React from 'react';
import { Skeleton } from './skeleton';
import { Badge } from './badge';
import { cn } from '@/lib/utils';

interface TypingIndicatorProps {
  className?: string;
}

export function TypingIndicator({ className }: TypingIndicatorProps) {
  return (
    <div className={cn("flex items-center gap-1", className)}>
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
      </div>
    </div>
  );
}

interface StreamingSkeletonProps {
  className?: string;
}

export function StreamingSkeleton({ className }: StreamingSkeletonProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center space-x-2">
        <Skeleton className="h-3 w-3 rounded-full" />
        <Skeleton className="h-3 w-16" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-3/5" />
      </div>
    </div>
  );
}

interface StreamingMessageWrapperProps {
  isStreaming?: boolean;
  isInitialLoad?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function StreamingMessageWrapper({ 
  isStreaming, 
  isInitialLoad, 
  children, 
  className 
}: StreamingMessageWrapperProps) {
  // Debug logging
  React.useEffect(() => {
    if (isStreaming !== undefined) {
      console.log('StreamingMessageWrapper - isStreaming:', isStreaming, 'isInitialLoad:', isInitialLoad);
    }
  }, [isStreaming, isInitialLoad]);

  if (isInitialLoad) {
    return (
      <div className={cn("rounded-lg p-4 bg-transparent dark:bg-black dark:text-slate-300", className)}>
        <StreamingSkeleton />
      </div>
    );
  }

  return (
    <div className={cn(
      "rounded-lg p-4 bg-transparent dark:bg-black dark:text-slate-300 transition-all duration-200",
      isStreaming && "animate-pulse",
      className
    )}>
      {children}
      {isStreaming && (
        <div className="mt-2 flex items-center gap-2">
          <TypingIndicator />
          <span className="text-xs text-muted-foreground">AI is typing...</span>
        </div>
      )}
    </div>
  );
}

interface StreamingStatusBadgeProps {
  model?: string;
  isStreaming?: boolean;
  className?: string;
}

export function StreamingStatusBadge({ model, isStreaming, className }: StreamingStatusBadgeProps) {
  if (!isStreaming) return null;

  return (
    <Badge 
      variant="secondary" 
      className={cn(
        "text-xs animate-pulse",
        className
      )}
    >
      <div className="flex items-center gap-1">
        <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping"></div>
        {model ? `${model} responding...` : 'AI responding...'}
      </div>
    </Badge>
  );
}

interface BlinkingCursorProps {
  className?: string;
}

export function BlinkingCursor({ className }: BlinkingCursorProps) {
  return (
    <span 
      className={cn(
        "inline-block w-0.5 h-4 bg-current ml-0.5 animate-pulse",
        className
      )}
    />
  );
}
