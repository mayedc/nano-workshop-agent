import { create } from "zustand";

import type { Project } from "@/types";

interface AppState {
  activeProject: Project | null;
  setActiveProject: (project: Project | null) => void;
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  toast: { message: string; type: "success" | "error" | "info" } | null;
  setToast: (toast: { message: string; type: "success" | "error" | "info" } | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeProject: null,
  setActiveProject: (project) => set({ activeProject: project }),
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toast: null,
  setToast: (toast) => set({ toast }),
}));
