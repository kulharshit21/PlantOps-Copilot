"use client";

import type { User } from "@supabase/supabase-js";
import { usePathname, useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  defaultDemoUser,
  demoUsers,
  type DemoUser,
  type UserRole,
} from "@/lib/demo-data";
import {
  createSupabaseBrowserClient,
  isSupabaseConfigured,
} from "@/lib/supabase/client";

type AuthState = {
  user: DemoUser;
  supabaseUser: User | null;
  isDemoMode: boolean;
  isLoading: boolean;
  isAuthenticated: boolean;
  signInWithDemoRole: (role: UserRole) => void;
  signInWithPassword: (email: string, password: string) => Promise<string | null>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);
const demoStorageKey = "plantops.demo.user";

function demoUserForRole(role: UserRole): DemoUser {
  return demoUsers.find((candidate) => candidate.role === role) ?? defaultDemoUser;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<DemoUser>(defaultDemoUser);
  const [supabaseUser, setSupabaseUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const isDemoMode = !isSupabaseConfigured();
  const supabase = useMemo(() => createSupabaseBrowserClient(), []);

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      if (!supabase) {
        const stored =
          typeof window !== "undefined"
            ? window.localStorage.getItem(demoStorageKey)
            : null;
        if (stored) {
          setUser(JSON.parse(stored) as DemoUser);
        }
        setIsLoading(false);
        return;
      }

      const { data } = await supabase.auth.getUser();
      if (!isMounted) return;

      setSupabaseUser(data.user);
      setUser({
        ...defaultDemoUser,
        email: data.user?.email ?? defaultDemoUser.email,
        name: data.user?.email?.split("@")[0] ?? defaultDemoUser.name,
      });
      setIsLoading(false);
    }

    void loadUser();

    const subscription = supabase?.auth.onAuthStateChange((_event, session) => {
      setSupabaseUser(session?.user ?? null);
    });

    return () => {
      isMounted = false;
      subscription?.data.subscription.unsubscribe();
    };
  }, [supabase]);

  useEffect(() => {
    if (isLoading || pathname === "/login" || pathname === "/") return;
    if (!isDemoMode && !supabaseUser) {
      router.replace("/login");
    }
  }, [isDemoMode, isLoading, pathname, router, supabaseUser]);

  const signInWithDemoRole = useCallback(
    (role: UserRole) => {
      const nextUser = demoUserForRole(role);
      setUser(nextUser);
      window.localStorage.setItem(demoStorageKey, JSON.stringify(nextUser));
      router.push("/dashboard");
    },
    [router],
  );

  const signInWithPassword = useCallback(
    async (email: string, password: string) => {
      if (!supabase) {
        signInWithDemoRole("supervisor");
        return null;
      }

      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) return error.message;

      router.push("/dashboard");
      return null;
    },
    [router, signInWithDemoRole, supabase],
  );

  const signOut = useCallback(async () => {
    if (supabase) {
      await supabase.auth.signOut();
    }
    window.localStorage.removeItem(demoStorageKey);
    setSupabaseUser(null);
    setUser(defaultDemoUser);
    router.push("/login");
  }, [router, supabase]);

  const value = useMemo<AuthState>(
    () => ({
      user,
      supabaseUser,
      isDemoMode,
      isLoading,
      isAuthenticated: isDemoMode || Boolean(supabaseUser),
      signInWithDemoRole,
      signInWithPassword,
      signOut,
    }),
    [
      isDemoMode,
      isLoading,
      signInWithDemoRole,
      signInWithPassword,
      signOut,
      supabaseUser,
      user,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
