export interface Project {
  id: string;
  name: string;
  description: string | null;
  template_id: string | null;
  status: "draft" | "active" | "completed" | "archived";
  owner_id: string;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  project_id: string;
  filename: string;
  mime_type: string;
  asset_type: string;
  size: number;
  storage_key: string;
  semantic_role: string | null;
  source_stage: string | null;
  uploaded_by: string | null;
  processing_status: "pending" | "in_progress" | "completed" | "failed";
  extra_metadata: Record<string, unknown>;
  created_at: string;
}

export interface Evidence {
  id: string;
  project_id: string;
  asset_id: string | null;
  type: string;
  content: string;
  extra_metadata: Record<string, unknown>;
  extracted_at: string;
}

export interface AgentRun {
  id: string;
  project_id: string;
  agent_name: string;
  step_id: number | null;
  status: "pending" | "running" | "completed" | "failed";
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
  confidence: number | null;
  evidence_ids: string[];
  review_status: "pending" | "approved" | "rejected" | "revised";
  error: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface WorkshopTemplateDSL {
  id: string;
  name: string;
  description: string;
  input_roles: string[];
  analysis_modules: string[];
  workflow_steps: WorkflowStep[];
  ontology: {
    concepts: string[];
    relationships: string[];
    participant_groups: string[];
    need_categories: string[];
  };
  output_types: string[];
  report_structure: ReportSection[];
}

export interface WorkflowStep {
  id: number;
  name: string;
  agent_name: string;
  status: "pending" | "in_progress" | "awaiting_input" | "completed" | "failed";
  depends_on: number[];
}

export interface ReportSection {
  title: string;
  type: string;
  source_steps: number[];
}

export interface ExportRecord {
  id: string;
  project_id: string;
  format: string;
  file_url: string;
  config: Record<string, unknown>;
  generated_at: string;
  generated_by: string | null;
}

export interface Code {
  id: string;
  project_id: string;
  name: string;
  description: string | null;
  evidence_ids: string[];
  created_by: string | null;
  created_at: string;
}

export interface Theme {
  id: string;
  project_id: string;
  name: string;
  description: string | null;
  code_ids: string[];
  evidence_ids: string[];
  confidence: number | null;
  created_at: string;
}

export interface Requirement {
  id: string;
  project_id: string;
  text: string;
  priority: string;
  source_evidence_ids: string[];
  status: string;
  created_at: string;
}

export interface QuantitativeResult {
  sample_size: number;
  descriptive_stats: {
    mean: number;
    median: number;
    std: number;
    min: number;
    max: number;
  };
  scale_stats: {
    cronbach_alpha: number;
    factors: number;
  };
  chart_data: Record<string, unknown>;
  significance_tests: Array<{
    test: string;
    p_value: number;
    significant: boolean;
  }>;
}

export interface DesignInsight {
  id: string;
  title: string;
  confidence: number;
  supporting_evidence: string[];
}

export interface DesignConcept {
  id: string;
  name: string;
  description: string;
  prompt: string;
}

export interface ExpertFeedback {
  id: string;
  project_id: string;
  reviewer_id: string | null;
  target_type: string;
  target_id: string;
  action: string;
  score: number | null;
  comment: string | null;
  suggested_revision: Record<string, unknown> | null;
  review_status: string;
  created_at: string;
}

export const TARGET_TYPES = [
  "codes",
  "themes",
  "requirements",
  "insights",
  "concepts",
  "report_sections",
] as const;

export const REVIEW_ACTIONS = [
  "approve",
  "reject",
  "revise",
  "merge",
  "split",
  "score",
  "comment",
  "request_rerun",
] as const;
