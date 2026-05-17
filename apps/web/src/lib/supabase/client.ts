import { createBrowserClient } from "@supabase/ssr";

function isConfigured(value: string | undefined) {
  return Boolean(value && !value.startsWith("replace-with") && !value.includes("your-project"));
}

export function isSupabaseConfigured() {
  return (
    isConfigured(process.env.NEXT_PUBLIC_SUPABASE_URL) &&
    isConfigured(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
  );
}

export function createSupabaseBrowserClient() {
  if (!isSupabaseConfigured()) {
    return null;
  }

  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
