"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/query-client";
import { useAppStore } from "@/lib/store";
import { Toast } from "@/components/ui/toast";

export function Providers({ children }: { children: React.ReactNode }) {
  const { toast, setToast } = useAppStore();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </QueryClientProvider>
  );
}
