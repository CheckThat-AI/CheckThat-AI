import { supabase } from './supabase';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  model?: string;
  isStreaming?: boolean;
}

export interface ConversationBranch {
  id: string;
  userMessage: Message;
  assistantMessage?: Message;
  timestamp: Date;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  userId: string;
}

export interface ConversationRow {
  id: string;
  title: string;
  messages: any[];
  created_at: string;
  updated_at: string;
  user_id: string;
}

class ConversationService {
  // Initialize user's conversation table if it doesn't exist
  async initializeUserConversations(userId: string) {
    try {
      // Check if user has any conversations
      const { error } = await supabase
        .from('conversations')
        .select('id')
        .eq('user_id', userId)
        .limit(1);

      if (error && error.code !== 'PGRST116') {
        console.error('Error checking conversations:', error);
      }

      return true;
    } catch (error) {
      console.error('Error initializing conversations:', error);
      return false;
    }
  }

  // Save a conversation to Supabase
  async saveConversation(conversation: Conversation): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('conversations')
        .upsert({
          id: conversation.id,
          title: conversation.title,
          messages: conversation.messages,
          created_at: conversation.createdAt.toISOString(),
          updated_at: conversation.updatedAt.toISOString(),
          user_id: conversation.userId,
        });

      if (error) {
        console.error('Error saving conversation:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error saving conversation:', error);
      return false;
    }
  }

  // Load all conversations for a user
  async loadConversations(userId: string): Promise<Conversation[]> {
    try {
      const { data, error } = await supabase
        .from('conversations')
        .select('*')
        .eq('user_id', userId)
        .order('updated_at', { ascending: false });

      if (error) {
        console.error('Error loading conversations:', error);
        return [];
      }

      if (!data) return [];

      return data.map((row: ConversationRow) => ({
        id: row.id,
        title: row.title,
        messages: row.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
        createdAt: new Date(row.created_at),
        updatedAt: new Date(row.updated_at),
        userId: row.user_id,
      }));
    } catch (error) {
      console.error('Error loading conversations:', error);
      return [];
    }
  }

  // Delete a conversation
  async deleteConversation(conversationId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('conversations')
        .delete()
        .eq('id', conversationId);

      if (error) {
        console.error('Error deleting conversation:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      return false;
    }
  }

  // Update conversation title
  async updateConversationTitle(conversationId: string, title: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('conversations')
        .update({ 
          title,
          updated_at: new Date().toISOString()
        })
        .eq('id', conversationId);

      if (error) {
        console.error('Error updating conversation title:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error updating conversation title:', error);
      return false;
    }
  }

  // Auto-save conversation (debounced)
  private saveTimeouts: Map<string, NodeJS.Timeout> = new Map();

  autoSaveConversation(conversation: Conversation, delay: number = 2000) {
    // Clear existing timeout for this conversation
    const existingTimeout = this.saveTimeouts.get(conversation.id);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }

    // Set new timeout
    const timeout = setTimeout(() => {
      this.saveConversation(conversation);
      this.saveTimeouts.delete(conversation.id);
    }, delay);

    this.saveTimeouts.set(conversation.id, timeout);
  }

  // Create SQL table if it doesn't exist (run this once during setup)
  async createConversationsTable() {
    try {
      const { error } = await supabase.rpc('create_conversations_table');
      if (error) {
        console.error('Error creating conversations table:', error);
        return false;
      }
      return true;
    } catch (error) {
      console.error('Error creating conversations table:', error);
      return false;
    }
  }
}

export const conversationService = new ConversationService(); 