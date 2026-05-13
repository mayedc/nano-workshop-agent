"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Upload,
  GitBranch,
  FileText,
  Tag,
  Palette,
  BarChart3,
  Lightbulb,
  Box,
  ClipboardCheck,
  FileOutput,
  Download,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { useAppStore } from "@/lib/store";

const nav = [
  { label: "Dashboard", href: "dashboard", icon: LayoutDashboard },
  { label: "Upload", href: "upload", icon: Upload },
  { label: "Workflow", href: "workflow", icon: GitBranch },
  { label: "Evidence", href: "evidence", icon: FileText },
  { label: "Coding", href: "coding", icon: Tag },
  { label: "Themes", href: "themes", icon: Palette },
  { label: "Quantitative", href: "quantitative", icon: BarChart3 },
  { label: "Insights", href: "insights", icon: Lightbulb },
  { label: "Prototypes", href: "prototypes", icon: Box },
  { label: "Review", href: "review", icon: ClipboardCheck },
  { label: "Report", href: "report", icon: FileOutput },
  { label: "Exports", href: "exports", icon: Download },
];

export function ProjectSidebar({ projectId }: { projectId: string }) {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useAppStore();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col border-r bg-card transition-all duration-300",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      <div className="flex h-14 items-center justify-between border-b px-3">
        {sidebarOpen && (
          <Link href="/projects" className="text-sm font-semibold tracking-tight">
            Nano Workshop
          </Link>
        )}
        <button onClick={toggleSidebar} className="rounded-md p-1.5 hover:bg-accent">
          {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeft className="h-4 w-4" />}
        </button>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        {nav.map((item) => {
          const href = `/projects/${projectId}/${item.href}`;
          const active = pathname === href || pathname.startsWith(href + "/");
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent hover:text-foreground",
                !sidebarOpen && "justify-center px-2"
              )}
              title={!sidebarOpen ? item.label : undefined}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
