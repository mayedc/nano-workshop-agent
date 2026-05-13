export interface WorkshopTemplate {
  id: string;
  name: string;
  description: string;
  inputRoles: string[];
  analysisModules: string[];
  workflowSteps: WorkflowStep[];
  ontology: Record<string, unknown>;
  outputTypes: string[];
  reportStructure: ReportSection[];
}

export interface WorkflowStep {
  id: number;
  name: string;
  agentName: string;
  status: "pending" | "in_progress" | "awaiting_input" | "completed" | "failed";
  dependsOn: number[];
}

export interface ReportSection {
  title: string;
  type: "text" | "chart" | "table" | "image";
  sourceSteps: number[];
}

export interface Project {
  id: string;
  name: string;
  templateId: string;
  status: "draft" | "active" | "completed" | "archived";
  createdAt: string;
  updatedAt: string;
}

export interface AgentRun {
  id: string;
  projectId: string;
  agentName: string;
  stepId: number;
  status: "pending" | "running" | "completed" | "failed";
  confidence?: number;
  evidenceIds: string[];
  reviewStatus: "pending" | "approved" | "rejected" | "revised";
  createdAt: string;
  completedAt?: string;
}

export interface Evidence {
  id: string;
  projectId: string;
  assetId: string;
  type: "text" | "image" | "audio" | "video" | "table";
  content: string;
  metadata: Record<string, unknown>;
  extractedAt: string;
}

export interface ExportRecord {
  id: string;
  projectId: string;
  format: "docx" | "pdf" | "pptx" | "json" | "csv";
  fileUrl: string;
  generatedAt: string;
  generatedBy: string;
}
