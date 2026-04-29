import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// `null` lets the rest of the app detect dev-mode (no Supabase project linked)
// and route through the legacy unauthenticated dashboard.
export const supabase = url && anonKey ? createClient(url, anonKey) : null

export const supabaseConfigured = Boolean(supabase)
