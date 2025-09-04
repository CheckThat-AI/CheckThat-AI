import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
// Check if Supabase is properly configured
const isSupabaseConfigured = 
  import.meta.env.VITE_SUPABASE_URL && 
  import.meta.env.VITE_SUPABASE_ANON_KEY && 
  !import.meta.env.VITE_SUPABASE_URL.includes('placeholder') && 
  !import.meta.env.VITE_SUPABASE_ANON_KEY.includes('placeholder')

if (!isSupabaseConfigured) {
  console.warn('Supabase not configured - running in guest-only mode')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: isSupabaseConfigured,
    autoRefreshToken: isSupabaseConfigured,
    detectSessionInUrl: isSupabaseConfigured,
    storageKey: 'supabase-auth-token',
    storage: window.localStorage
  }
})

export { isSupabaseConfigured } 