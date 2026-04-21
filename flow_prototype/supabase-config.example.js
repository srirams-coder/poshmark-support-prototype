/**
 * Copy to supabase-config.js and fill in your Supabase project values.
 * supabase-config.js can be committed for team demos (anon key is public by design; lock down with RLS).
 */
window.PROTOTYPE_SUPABASE = {
  url: 'https://YOUR_PROJECT_REF.supabase.co',
  anonKey: 'YOUR_SUPABASE_ANON_KEY',
  /** Set true after creating table prototype_cases and RLS policies (see supabase/migrations/). */
  enabled: false
};
