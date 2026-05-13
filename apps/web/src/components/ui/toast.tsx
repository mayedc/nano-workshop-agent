"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

interface ToastProps {
  message: string;
  type?: "success" | "error" | "info";
  onClose?: () => void;
}

export function Toast({ message, type = "info", onClose }: ToastProps) {
  React.useEffect(() => {
    const t = setTimeout(() => onClose?.(), 4000);
    return () => clearTimeout(t);
  }, [onClose]);

  const bg =
    type === "success" ? "bg-green-600" : type === "error" ? "bg-red-600" : "bg-slate-800";

  return (
    <div className={cn("fixed bottom-4 right-4 z-50 flex items-center gap-3 rounded-lg px-4 py-3 text-white shadow-lg", bg)}>
      <span className="text-sm font-medium">{message}</span>
      {onClose && (
        <button onClick={onClose} className="rounded p-1 hover:bg-white/20">
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
