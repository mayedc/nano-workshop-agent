"use client";

import { ProjectSidebar } from "./ProjectSidebar";
import { useAppStore } from "@/lib/store";
import { cn } from "@/lib/utils";

export function AppShell({ children, projectId }: { children: React.ReactNode; projectId?: string }) {
  const { sidebarOpen } = useAppStore();
  return (
    <div className="min-h-screen">
      {projectId && <ProjectSidebar projectId={projectId} />}
      <main
        className={cn(
          "transition-all duration-300",
          projectId ? (sidebarOpen ? "ml-64" : "ml-16") : ""
        )}
      >
        {children}
      </main>
    </div>
  );
}
