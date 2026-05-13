const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetcher<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Projects
  listProjects: () => fetcher<Project[]>("/api/projects"),
  getProject: (id: string) => fetcher<Project>(`/api/projects/${id}`),
  createProject: (data: Partial<Project>) =>
    fetcher<Project>("/api/projects", { method: "POST", body: JSON.stringify(data) }),
  updateProject: (id: string, data: Partial<Project>) =>
    fetcher<Project>(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteProject: (id: string) =>
    fetcher<void>(`/api/projects/${id}`, { method: "DELETE" }),

  // Assets
  listAssets: (projectId: string) =>
    fetcher<Asset[]>(`/api/assets/project/${projectId}`),
  uploadAsset: (projectId: string, formData: FormData) =>
    fetcher<Asset>(`/api/assets/project/${projectId}/upload`, {
      method: "POST",
      body: formData,
    }),
  processAssetSync: (assetId: string, projectId: string) =>
    fetcher<unknown>(`/api/assets/${assetId}/process-sync?project_id=${projectId}`, {
      method: "POST",
    }),

  // Evidence
  listEvidence: () => fetcher<Evidence[]>("/api/evidence"),

  // Agent Runs
  listAgentRuns: () => fetcher<AgentRun[]>("/api/runs"),

  // Templates
  listTemplates: () => fetcher<WorkshopTemplateDSL[]>("/api/templates/dsl"),
  getTemplate: (id: string) => fetcher<WorkshopTemplateDSL>(`/api/templates/dsl/${id}`),

  // Workflows
  runWorkflow: (data: unknown) =>
    fetcher<unknown>("/api/workflows/run", { method: "POST", body: JSON.stringify(data) }),
  listAgents: () => fetcher<string[]>("/api/workflows/agents"),

  // Health
  health: () => fetcher<{ status: string }>("/api/health/"),
};

// Type imports for the global scope augmentation
import type {
  AgentRun,
  Asset,
  Code,
  DesignConcept,
  DesignInsight,
  Evidence,
  ExportRecord,
  Project,
  QuantitativeResult,
  Requirement,
  Theme,
  WorkshopTemplateDSL,
} from "@/types";
