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
  deleteAsset: (assetId: string) =>
    fetcher<void>(`/api/assets/${assetId}`, { method: "DELETE" }),
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
  listProjectExports: (projectId: string) =>
    fetcher<ExportRecord[]>(`/api/exports/project/${projectId}`),
  generateExport: async (projectId: string, format: string) => {
    const url = `${API_BASE}/api/exports/generate/${projectId}?format=${format}`;
    const response = await fetch(url);
    if (!response.ok) {
      const err = await response.text();
      throw new Error(err || `Export failed`);
    }
    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition");
    const filenameMatch = disposition?.match(/filename="(.+)"/);
    const filename = filenameMatch?.[1] || `export.${format === "csv" ? "zip" : format}`;
    const objectUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(objectUrl);
  },

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

  // Project Config
  getProjectConfig: (id: string) =>
    fetcher<{ agents: Array<{ id?: string; name: string; model?: string }>; llm_config: { provider?: string; api_key?: string; model?: string; base_url?: string } }>(`/api/projects/${id}/config`),
  updateProjectConfig: (id: string, data: { agents?: Array<{ id?: string; name: string; model?: string }>; llm_config?: { provider?: string; api_key?: string; model?: string; base_url?: string } }) =>
    fetcher<{ agents: Array<{ id?: string; name: string; model?: string }>; llm_config: { provider?: string; api_key?: string; model?: string; base_url?: string } }>(`/api/projects/${id}/config`, { method: "PUT", body: JSON.stringify(data) }),

  // Data Analysis
  analyzeProjectData: (projectId: string, data: { asset_id: string; user_question: string }) =>
    fetcher<{
      project_id: string;
      steps: Array<{
        agent: string;
        status: string;
        output?: unknown;
        error?: string | null;
        stdout?: string;
        result_type?: string;
      }>;
      final_answer: string;
      code?: string | null;
      execution?: {
        result?: unknown;
        result_type?: string;
        stdout?: string;
        error?: string | null;
      } | null;
    }>(`/api/projects/${projectId}/analyze`, { method: "POST", body: JSON.stringify(data) }),

  // Workshop Planner
  planWorkshop: (projectId: string, data: { asset_ids: string[]; workshop_purpose: string }) =>
    fetcher<import("@/types").WorkshopPlanResponse>(`/api/projects/${projectId}/workshop-planner/plan`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

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
