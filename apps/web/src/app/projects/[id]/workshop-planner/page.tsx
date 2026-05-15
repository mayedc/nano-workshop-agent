"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Loader2,
  Play,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Lightbulb,
  ListChecks,
  FileText,
  Save,
  Compass,
  ArrowRight,
} from "lucide-react";
import type { WorkshopPlanResponse, SuggestedWorkflowStep, Asset } from "@/types";

const agentCategoryColors: Record<string, string> = {
  ProjectSetupAgent: "bg-slate-100 text-slate-800 border-slate-300",
  MaterialIntakeAgent: "bg-slate-100 text-slate-800 border-slate-300",
  PreprocessingAgent: "bg-blue-100 text-blue-800 border-blue-300",
  MetadataFusionAgent: "bg-blue-100 text-blue-800 border-blue-300",
  GoalUnderstandingAgent: "bg-cyan-100 text-cyan-800 border-cyan-300",
  WorkshopPlannerAgent: "bg-violet-100 text-violet-800 border-violet-300",
  QualitativeAnalysisAgent: "bg-green-100 text-green-800 border-green-300",
  CodingAgent: "bg-green-100 text-green-800 border-green-300",
  ThemeExtractionAgent: "bg-green-100 text-green-800 border-green-300",
  QuantitativeAnalysisAgent: "bg-emerald-100 text-emerald-800 border-emerald-300",
  DataProfileAgent: "bg-emerald-100 text-emerald-800 border-emerald-300",
  PlannerAgent: "bg-emerald-100 text-emerald-800 border-emerald-300",
  CodeAgent: "bg-emerald-100 text-emerald-800 border-emerald-300",
  RepairAgent: "bg-emerald-100 text-emerald-800 border-emerald-300",
  ResultExplainerAgent: "bg-emerald-100 text-emerald-800 border-emerald-300",
  PrototypeAnalysisAgent: "bg-purple-100 text-purple-800 border-purple-300",
  DesignInsightAgent: "bg-purple-100 text-purple-800 border-purple-300",
  DesignConceptAgent: "bg-purple-100 text-purple-800 border-purple-300",
  ExpertReviewAgent: "bg-amber-100 text-amber-800 border-amber-300",
  IterationAgent: "bg-amber-100 text-amber-800 border-amber-300",
  ReportGenerationAgent: "bg-orange-100 text-orange-800 border-orange-300",
  ExportAgent: "bg-orange-100 text-orange-800 border-orange-300",
  EvaluationAgent: "bg-red-100 text-red-800 border-red-300",
  MeetingRealtimeAgent: "bg-pink-100 text-pink-800 border-pink-300",
  MCPConnectorAgent: "bg-pink-100 text-pink-800 border-pink-300",
};

function getAgentColor(agentName: string): string {
  return agentCategoryColors[agentName] || "bg-gray-100 text-gray-800 border-gray-300";
}

const mimeTypeLabels: Record<string, string> = {
  "text/csv": "CSV",
  "text/plain": "TXT",
  "text/markdown": "MD",
  "application/json": "JSON",
  "application/pdf": "PDF",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
  "application/vnd.ms-excel": "XLS",
  "image/png": "PNG",
  "image/jpeg": "JPEG",
  "audio/mpeg": "MP3",
  "audio/wav": "WAV",
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface LLMConfig {
  provider?: string;
  api_key?: string;
  model?: string;
  base_url?: string;
}

function WorkflowStepCard({
  step,
  isOpen,
  onToggle,
}: {
  step: SuggestedWorkflowStep;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const colorClass = getAgentColor(step.agent_name);
  const depsLabel =
    step.depends_on.length > 0 ? `depends on: [${step.depends_on.join(", ")}]` : "no dependencies";

  return (
    <Card className={`border-l-4 ${colorClass.split(" ")[2] || "border-gray-300"}`}>
      <button
        className="w-full text-left p-4 flex items-center gap-3 hover:bg-accent/50 transition-colors"
        onClick={onToggle}
      >
        <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-bold">
          {step.id}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold">{step.name}</span>
            <Badge variant="outline" className={colorClass}>
              {step.agent_name}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">{depsLabel}</p>
        </div>
        {isOpen ? <ChevronDown className="h-4 w-4 flex-shrink-0" /> : <ChevronRight className="h-4 w-4 flex-shrink-0" />}
      </button>
      {isOpen && (
        <div className="px-4 pb-4 space-y-3 border-t pt-3">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase">Description</p>
            <p className="text-sm mt-1">{step.description}</p>
          </div>
          {step.depends_on.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase">Depends On</p>
              <div className="flex items-center gap-1 mt-1 flex-wrap">
                {step.depends_on.map((depId) => (
                  <Badge key={depId} variant="secondary" className="text-xs">
                    Step {depId}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          {step.expected_output && (
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase">Expected Output</p>
              <p className="text-sm mt-1 text-muted-foreground">{step.expected_output}</p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

function JsonView({ data }: { data: unknown }) {
  return (
    <pre className="text-xs bg-muted rounded-md p-3 overflow-auto max-h-64">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

export default function WorkshopPlannerPage() {
  const { id } = useParams() as { id: string };
  const queryClient = useQueryClient();

  const [selectedAssetIds, setSelectedAssetIds] = useState<Set<string>>(new Set());
  const [workshopPurpose, setWorkshopPurpose] = useState("");
  const [result, setResult] = useState<WorkshopPlanResponse | null>(null);
  const [openSteps, setOpenSteps] = useState<Set<number>>(new Set());
  const [activeMainTab, setActiveMainTab] = useState("input");

  const [llmConfig, setLlmConfig] = useState<LLMConfig>({ provider: "zhipu", model: "glm-5.1", api_key: "", base_url: "" });

  const { data: assets } = useQuery({
    queryKey: ["assets", id],
    queryFn: () => api.listAssets(id),
  });

  const { data: configData } = useQuery({
    queryKey: ["project-config", id],
    queryFn: () => api.getProjectConfig(id),
  });

  useEffect(() => {
    if (configData) {
      setLlmConfig({
        provider: configData.llm_config?.provider || "zhipu",
        model: configData.llm_config?.model || "glm-5.1",
        api_key: configData.llm_config?.api_key || "",
        base_url: (configData.llm_config as Record<string, unknown>)?.base_url as string || "",
      });
    }
  }, [configData]);

  const planMutation = useMutation({
    mutationFn: () =>
      api.planWorkshop(id, {
        asset_ids: Array.from(selectedAssetIds),
        workshop_purpose: workshopPurpose,
      }),
    onSuccess: (data) => {
      setResult(data);
      const allStepIds = data.workflow_steps.map((s) => s.id);
      setOpenSteps(new Set(allStepIds));
    },
    onError: (err: Error) => alert("Planning failed: " + err.message),
  });

  const saveConfig = useMutation({
    mutationFn: () =>
      api.updateProjectConfig(id, {
        llm_config: {
          provider: llmConfig.provider,
          model: llmConfig.model,
          api_key: llmConfig.api_key,
          base_url: llmConfig.base_url,
        },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project-config", id] });
      alert("Configuration saved");
    },
    onError: (err: Error) => alert("Save failed: " + err.message),
  });

  const toggleAsset = (assetId: string) => {
    setSelectedAssetIds((prev) => {
      const next = new Set(prev);
      if (next.has(assetId)) next.delete(assetId);
      else next.add(assetId);
      return next;
    });
  };

  const selectAllAssets = () => {
    if (!assets) return;
    setSelectedAssetIds(new Set(assets.map((a) => a.id)));
  };

  const deselectAllAssets = () => {
    setSelectedAssetIds(new Set());
  };

  const toggleStep = (stepId: number) => {
    setOpenSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepId)) next.delete(stepId);
      else next.add(stepId);
      return next;
    });
  };

  const canSubmit = selectedAssetIds.size > 0 && workshopPurpose.trim().length >= 10;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Compass className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">Workshop Planner</h1>
      </div>

      <Tabs value={activeMainTab} onValueChange={setActiveMainTab}>
        <TabsList className="grid w-full grid-cols-2 max-w-sm">
          <TabsTrigger value="input">Input</TabsTrigger>
          <TabsTrigger value="config">Config</TabsTrigger>
        </TabsList>

        <TabsContent value="input" className="mt-4 space-y-4">
          {/* Asset Selection */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Select Assets</CardTitle>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={selectAllAssets}>
                    Select All
                  </Button>
                  <Button size="sm" variant="outline" onClick={deselectAllAssets}>
                    Deselect All
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {!assets || assets.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No assets uploaded yet. Go to Upload to add files first.
                </p>
              ) : (
                <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                  {assets.map((asset: Asset) => {
                    const isSelected = selectedAssetIds.has(asset.id);
                    const typeLabel = mimeTypeLabels[asset.mime_type] || asset.mime_type.split("/")[0]?.toUpperCase() || "?";
                    return (
                      <div
                        key={asset.id}
                        role="checkbox"
                        aria-checked={isSelected}
                        tabIndex={0}
                        className={`flex items-start gap-3 rounded-lg border p-3 text-left transition-colors cursor-pointer ${
                          isSelected
                            ? "border-primary bg-primary/5 ring-1 ring-primary"
                            : "hover:bg-accent"
                        }`}
                        onClick={() => toggleAsset(asset.id)}
                        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggleAsset(asset.id); } }}
                      >
                        <div className={`mt-0.5 h-5 w-5 flex-shrink-0 rounded border-2 flex items-center justify-center transition-colors ${
                          isSelected ? "bg-primary border-primary text-primary-foreground" : "border-muted-foreground/30"
                        }`}>
                          {isSelected && <CheckCircle className="h-4 w-4" />}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <p className="text-sm font-medium truncate">{asset.filename}</p>
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="secondary" className="text-xs">
                              {typeLabel}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {formatSize(asset.size)}
                            </span>
                            {asset.semantic_role && (
                              <span className="text-xs text-muted-foreground">· {asset.semantic_role}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
              {assets && assets.length > 0 && (
                <p className="text-xs text-muted-foreground mt-3">
                  {selectedAssetIds.size} of {assets.length} assets selected
                </p>
              )}
            </CardContent>
          </Card>

          {/* Workshop Purpose */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Workshop Purpose</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Describe what this workshop aims to achieve. For example: '分析 pedestrian 在 eHMI 场景下的行为模式，评估三种交互设计方案的有效性，并生成量化研究报告...'"
                value={workshopPurpose}
                onChange={(e) => setWorkshopPurpose(e.target.value)}
                className="min-h-32"
              />
              <p className="text-xs text-muted-foreground mt-1">
                {workshopPurpose.length < 10
                  ? `At least ${10 - workshopPurpose.length} more characters needed`
                  : `${workshopPurpose.length} characters`}
              </p>
            </CardContent>
          </Card>

          {/* Submit */}
          <Button
            size="lg"
            className="w-full"
            disabled={!canSubmit || planMutation.isPending}
            onClick={() => planMutation.mutate()}
          >
            {planMutation.isPending ? (
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            ) : (
              <Play className="mr-2 h-5 w-5" />
            )}
            Generate Workflow Plan
          </Button>
        </TabsContent>

        <TabsContent value="config" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Model Config</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Provider</label>
                <select
                  className="w-full rounded-md border px-3 py-2 text-sm"
                  value={llmConfig.provider}
                  onChange={(e) => {
                    const provider = e.target.value;
                    const defaults: Record<string, { model: string; base_url: string }> = {
                      zhipu: { model: "glm-5.1", base_url: "" },
                      anthropic: { model: "claude-sonnet-4-6", base_url: "" },
                      openai: { model: "gpt-4o", base_url: "https://api.openai.com/v1" },
                      deepseek: { model: "deepseek-chat", base_url: "https://api.deepseek.com/v1" },
                      gemini: { model: "gemini-2.5-flash", base_url: "https://generativelanguage.googleapis.com/v1beta/openai/" },
                      mock: { model: "mock", base_url: "" },
                    };
                    const d = defaults[provider] || { model: "", base_url: "" };
                    setLlmConfig((c) => ({ ...c, provider, model: d.model, base_url: d.base_url }));
                  }}
                >
                  <option value="zhipu">Zhipu (GLM)</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="openai">OpenAI (GPT)</option>
                  <option value="deepseek">DeepSeek</option>
                  <option value="gemini">Google Gemini</option>
                  <option value="mock">Mock</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">API Key</label>
                <Input
                  type="password"
                  placeholder={
                    llmConfig.provider === "zhipu" ? "your.zhipu.key" :
                    llmConfig.provider === "anthropic" ? "sk-ant-..." :
                    llmConfig.provider === "gemini" ? "AIza..." :
                    "sk-..."
                  }
                  value={llmConfig.api_key}
                  onChange={(e) => setLlmConfig((c) => ({ ...c, api_key: e.target.value }))}
                />
                <p className="text-xs text-muted-foreground">Leave empty to keep existing key.</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Base URL</label>
                <Input
                  placeholder="https://api.openai.com/v1"
                  value={llmConfig.base_url || ""}
                  onChange={(e) => setLlmConfig((c) => ({ ...c, base_url: e.target.value }))}
                />
                <p className="text-xs text-muted-foreground">
                  {llmConfig.provider === "zhipu" || llmConfig.provider === "anthropic"
                    ? "Optional override for API endpoint."
                    : "API endpoint URL for OpenAI-compatible providers."}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Model</label>
                <Input
                  placeholder={
                    llmConfig.provider === "openai" ? "gpt-4o" :
                    llmConfig.provider === "deepseek" ? "deepseek-chat" :
                    llmConfig.provider === "gemini" ? "gemini-2.5-flash" :
                    llmConfig.provider === "zhipu" ? "glm-5.1" :
                    llmConfig.provider === "anthropic" ? "claude-sonnet-4-6" :
                    "model-name"
                  }
                  value={llmConfig.model}
                  onChange={(e) => setLlmConfig((c) => ({ ...c, model: e.target.value }))}
                />
              </div>

              <Button className="w-full" onClick={() => saveConfig.mutate()} disabled={saveConfig.isPending}>
                {saveConfig.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                Save Config
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Loading */}
      {planMutation.isPending && !result && (
        <Card>
          <CardContent className="py-8 flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Analyzing assets and generating workflow plan...</p>
            <Progress value={50} className="w-64" />
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Summary Card */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <Lightbulb className="h-6 w-6 text-amber-500 flex-shrink-0 mt-0.5" />
                <div className="space-y-3">
                  <h2 className="text-xl font-bold">{result.workshop_title}</h2>
                  <p className="text-muted-foreground">{result.reasoning}</p>
                  <div className="flex items-center gap-3 flex-wrap">
                    <Badge
                      variant="outline"
                      className={
                        result.confidence === "high"
                          ? "bg-green-100 text-green-800"
                          : result.confidence === "medium"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                      }
                    >
                      Confidence: {result.confidence}
                    </Badge>
                    {result.estimated_duration && (
                      <span className="text-xs text-muted-foreground">
                        Est. duration: {result.estimated_duration}
                      </span>
                    )}
                  </div>
                  {result.suggested_modules.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-medium text-muted-foreground">Modules:</span>
                      {result.suggested_modules.map((mod) => (
                        <Badge key={mod} variant="secondary" className="text-xs">
                          {mod}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Workflow Steps */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <ListChecks className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">
                  Suggested Workflow ({result.workflow_steps.length} steps)
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              {result.workflow_steps.length === 0 ? (
                <p className="text-sm text-muted-foreground">No workflow steps were generated.</p>
              ) : (
                result.workflow_steps.map((step) => (
                  <WorkflowStepCard
                    key={step.id}
                    step={step}
                    isOpen={openSteps.has(step.id)}
                    onToggle={() => toggleStep(step.id)}
                  />
                ))
              )}
            </CardContent>
          </Card>

          {/* Assumptions */}
          {result.assumptions.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Assumptions</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1">
                  {result.assumptions.map((a, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                      <ArrowRight className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                      {a}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Raw JSON toggle */}
          <details className="text-xs">
            <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
              Raw Response (JSON)
            </summary>
            <JsonView data={result} />
          </details>
        </div>
      )}
    </div>
  );
}
