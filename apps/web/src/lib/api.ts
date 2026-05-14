const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetcher<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const isFormData = options?.body instanceof FormData;
  const res = await fetch(url, {
    headers: isFormData ? {} : { "Content-Type": "application/json" },
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
  listProjectEvidence: (projectId: string) =>
    fetcher<Evidence[]>(`/api/evidence/project/${projectId}`),

  // Exports
  listExports: () => fetcher<ExportRecord[]>("/api/exports"),

  // Agent Runs
  listAgentRuns: () => fetcher<AgentRun[]>("/api/runs"),

  // Templates
  listTemplates: () => fetcher<WorkshopTemplateDSL[]>("/api/templates/dsl"),
  getTemplate: (id: string) => fetcher<WorkshopTemplateDSL>(`/api/templates/dsl/${id}`),

  // Workflows
  runWorkflow: (data: unknown) =>
    fetcher<unknown>("/api/workflows/run", { method: "POST", body: JSON.stringify(data) }),
  listAgents: () => fetcher<string[]>("/api/workflows/agents"),

  // Feedback
  listFeedback: (params?: {
    project_id?: string;
    target_type?: string;
    target_id?: string;
    action?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params?.project_id) qs.set("project_id", params.project_id);
    if (params?.target_type) qs.set("target_type", params.target_type);
    if (params?.target_id) qs.set("target_id", params.target_id);
    if (params?.action) qs.set("action", params.action);
    const suffix = qs.toString() ? `?${qs.toString()}` : "";
    return fetcher<ExpertFeedback[]>(`/api/feedback/${suffix}`);
  },
  createFeedback: (data: {
    project_id: string;
    target_type: string;
    target_id: string;
    action: string;
    score?: number;
    comment?: string;
    suggested_revision?: Record<string, unknown>;
  }) =>
    fetcher<ExpertFeedback>("/api/feedback/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getFeedback: (id: string) => fetcher<ExpertFeedback>(`/api/feedback/${id}`),
  updateFeedback: (id: string, data: Partial<ExpertFeedback>) =>
    fetcher<ExpertFeedback>(`/api/feedback/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteFeedback: (id: string) =>
    fetcher<void>(`/api/feedback/${id}`, { method: "DELETE" }),
  listTargetTypes: () => fetcher<string[]>("/api/feedback/targets/types"),
  listReviewActions: () => fetcher<string[]>("/api/feedback/actions/list"),

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
  ExpertFeedback,
  ExportRecord,
  Project,
  QuantitativeResult,
  Requirement,
  Theme,
  WorkshopTemplateDSL,
} from "@/types";
