"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  Loader2,
  Play,
  Upload,
  CheckCircle,
  XCircle,
  Code2,
  FileSpreadsheet,
  ChevronDown,
  ChevronRight,
  Terminal,
  AlertTriangle,
  Lightbulb,
  ListChecks,
  BarChart3,
} from "lucide-react";

interface StepInfo {
  agent: string;
  status: string;
  output?: unknown;
  error?: string | null;
  stdout?: string;
  result_type?: string;
}

interface ExecutionInfo {
  result?: unknown;
  result_type?: string;
  stdout?: string;
  error?: string | null;
}

interface AnalyzeResult {
  project_id: string;
  steps: StepInfo[];
  final_answer: string;
  code?: string | null;
  execution?: ExecutionInfo | null;
}

const stepMeta: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  DataProfileAgent: { label: "Data Profile", icon: <BarChart3 className="h-4 w-4" />, color: "bg-blue-50 text-blue-700 border-blue-200" },
  PlannerAgent: { label: "Analysis Plan", icon: <ListChecks className="h-4 w-4" />, color: "bg-indigo-50 text-indigo-700 border-indigo-200" },
  CodeAgent: { label: "Code Generation", icon: <Code2 className="h-4 w-4" />, color: "bg-slate-50 text-slate-700 border-slate-200" },
  Executor: { label: "Execution", icon: <Terminal className="h-4 w-4" />, color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  RepairAgent: { label: "Auto Repair", icon: <AlertTriangle className="h-4 w-4" />, color: "bg-amber-50 text-amber-700 border-amber-200" },
  ResultExplainerAgent: { label: "Explanation", icon: <Lightbulb className="h-4 w-4" />, color: "bg-violet-50 text-violet-700 border-violet-200" },
};

function JsonView({ data }: { data: unknown }) {
  return (
    <pre className="rounded-md bg-muted p-3 text-xs overflow-x-auto whitespace-pre-wrap">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

function DataFrameTable({ data }: { data: Record<string, unknown>[] }) {
  if (!Array.isArray(data) || data.length === 0) return <p className="text-xs text-muted-foreground">No data</p>;
  const cols = Object.keys(data[0]);
  return (
    <div className="overflow-x-auto rounded-md border">
      <table className="min-w-full text-xs">
        <thead className="bg-muted">
          <tr>
            {cols.map((c) => (
              <th key={c} className="px-3 py-2 text-left font-semibold whitespace-nowrap">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="border-t">
              {cols.map((c) => (
                <td key={c} className="px-3 py-2 whitespace-nowrap">{String(row[c] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StepCard({ step, isOpen, onToggle }: { step: StepInfo; isOpen: boolean; onToggle: () => void }) {
  const meta = stepMeta[step.agent] || { label: step.agent, icon: null, color: "bg-gray-50 text-gray-700 border-gray-200" };
  const isDone = step.status === "completed";
  const isError = step.status === "failed";

  return (
    <div className={`rounded-lg border ${meta.color} overflow-hidden`}>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-3">
          {isDone ? <CheckCircle className="h-4 w-4 text-green-600" /> : isError ? <XCircle className="h-4 w-4 text-red-600" /> : <div className="h-4 w-4 rounded-full border" />}
          <div className="flex items-center gap-2">
            {meta.icon}
            <span className="text-sm font-semibold">{meta.label}</span>
          </div>
          <Badge variant="outline" className="text-[10px] h-5">
            {step.status}
          </Badge>
        </div>
        {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>

      {isOpen && (
        <div className="px-4 pb-4 space-y-3 border-t bg-white/60">
          {step.error && (
            <div className="mt-3 rounded-md bg-red-50 p-3 text-xs text-red-700 whitespace-pre-wrap">
              {step.error}
            </div>
          )}

          {step.agent === "DataProfileAgent" && typeof step.output === "object" && step.output !== null && (
            <div className="mt-3 space-y-3">
              {typeof (step.output as Record<string, unknown>).overview === "string" && (
                <p className="text-sm font-medium">{(step.output as Record<string, unknown>).overview as string}</p>
              )}
              {Array.isArray((step.output as Record<string, unknown>).columns) && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Columns</p>
                  <DataFrameTable data={(step.output as Record<string, unknown>).columns as Record<string, unknown>[]} />
                </div>
              )}
              {Array.isArray((step.output as Record<string, unknown>).quality_issues) && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Quality Issues</p>
                  <ul className="list-disc list-inside text-xs space-y-1">
                    {((step.output as Record<string, unknown>).quality_issues as { issue: string; severity: string }[]).map((q, i) => (
                      <li key={i}>
                        <span className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-medium ${q.severity === "high" ? "bg-red-100 text-red-700" : q.severity === "medium" ? "bg-amber-100 text-amber-700" : "bg-green-100 text-green-700"}`}>
                          {q.severity}
                        </span>{" "}
                        {q.issue}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {Array.isArray((step.output as Record<string, unknown>).suggested_analyses) && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Suggested Analyses</p>
                  <ul className="list-disc list-inside text-xs space-y-1">
                    {((step.output as Record<string, unknown>).suggested_analyses as string[]).map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}
              <details>
                <summary className="cursor-pointer text-xs text-muted-foreground">Raw JSON</summary>
                <JsonView data={step.output} />
              </details>
            </div>
          )}

          {step.agent === "PlannerAgent" && typeof step.output === "object" && step.output !== null && (
            <div className="mt-3 space-y-3">
              {typeof (step.output as Record<string, unknown>).objective === "string" && (
                <p className="text-sm font-medium">{(step.output as Record<string, unknown>).objective as string}</p>
              )}
              {typeof (step.output as Record<string, unknown>).reasoning === "string" && (
                <p className="text-xs text-muted-foreground leading-relaxed">{(step.output as Record<string, unknown>).reasoning as string}</p>
              )}
              {Array.isArray((step.output as Record<string, unknown>).steps) && (
                <div className="space-y-2">
                  {((step.output as Record<string, unknown>).steps as { step_number: number; title: string; description: string; technique: string; input_columns: string[]; expected_output: string }[]).map((s) => (
                    <div key={s.step_number} className="rounded-md border bg-white p-3">
                      <div className="flex items-center gap-2">
                        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                          {s.step_number}
                        </span>
                        <span className="text-sm font-semibold">{s.title}</span>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">{s.description}</p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        <Badge variant="secondary" className="text-[10px]">{s.technique}</Badge>
                        {s.input_columns.map((c) => (
                          <Badge key={c} variant="outline" className="text-[10px]">{c}</Badge>
                        ))}
                      </div>
                      <p className="mt-1 text-[10px] text-muted-foreground">Output: {s.expected_output}</p>
                    </div>
                  ))}
                </div>
              )}
              <details>
                <summary className="cursor-pointer text-xs text-muted-foreground">Raw JSON</summary>
                <JsonView data={step.output} />
              </details>
            </div>
          )}

          {step.agent === "CodeAgent" && typeof step.output === "object" && step.output !== null && (
            <div className="mt-3">
              <pre className="rounded-md bg-slate-900 p-4 text-xs text-slate-50 overflow-x-auto">
                <code>{(step.output as Record<string, unknown>).code as string}</code>
              </pre>
            </div>
          )}

          {step.agent === "Executor" && (
            <div className="mt-3 space-y-3">
              {step.result_type === "dataframe" && Array.isArray(step.output) && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Result Table</p>
                  <DataFrameTable data={step.output} />
                </div>
              )}
              {step.result_type !== "dataframe" && step.output !== undefined && step.output !== null && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Result</p>
                  <JsonView data={step.output} />
                </div>
              )}
              {step.stdout && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Stdout</p>
                  <pre className="rounded-md bg-black p-3 text-xs text-green-400 overflow-x-auto whitespace-pre-wrap">
                    {step.stdout}
                  </pre>
                </div>
              )}
            </div>
          )}

          {step.agent === "RepairAgent" && typeof step.output === "object" && step.output !== null && (
            <div className="mt-3">
              <p className="text-xs font-semibold text-muted-foreground mb-1">Fixed Code</p>
              <pre className="rounded-md bg-slate-900 p-4 text-xs text-slate-50 overflow-x-auto">
                <code>{(step.output as Record<string, unknown>).code as string}</code>
              </pre>
            </div>
          )}

          {step.agent === "ResultExplainerAgent" && typeof step.output === "object" && step.output !== null && (
            <div className="mt-3 space-y-3">
              {typeof (step.output as Record<string, unknown>).summary === "string" && (
                <div className="rounded-md bg-violet-50 p-3">
                  <p className="text-sm font-medium text-violet-900">{(step.output as Record<string, unknown>).summary as string}</p>
                </div>
              )}
              {Array.isArray((step.output as Record<string, unknown>).key_findings) && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Key Findings</p>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {((step.output as Record<string, unknown>).key_findings as string[]).map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}
              {typeof (step.output as Record<string, unknown>).details === "string" && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Details</p>
                  <p className="text-sm leading-relaxed">{(step.output as Record<string, unknown>).details as string}</p>
                </div>
              )}
              {Array.isArray((step.output as Record<string, unknown>).recommendations) && (
                <div className="grid gap-2 sm:grid-cols-2">
                  {((step.output as Record<string, unknown>).recommendations as string[]).map((r, i) => (
                    <div key={i} className="rounded-md border bg-white p-3 text-sm">
                      {r}
                    </div>
                  ))}
                </div>
              )}
              {typeof (step.output as Record<string, unknown>).confidence === "string" && (
                <Badge className="text-[10px]">
                  Confidence: {(step.output as Record<string, unknown>).confidence as string}
                </Badge>
              )}
              {typeof (step.output as Record<string, unknown>).limitations === "string" && (
                <p className="text-xs text-muted-foreground">
                  Limitations: {(step.output as Record<string, unknown>).limitations as string}
                </p>
              )}
              <details>
                <summary className="cursor-pointer text-xs text-muted-foreground">Raw JSON</summary>
                <JsonView data={step.output} />
              </details>
            </div>
          )}

          {/* Fallback raw view for any other agent or non-object output */}
          {!["DataProfileAgent", "PlannerAgent", "CodeAgent", "Executor", "RepairAgent", "ResultExplainerAgent"].includes(step.agent) && (
            <div className="mt-3">
              <JsonView data={step.output} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function AnalyzePage() {
  const { id } = useParams() as { id: string };
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("分析用户对eHMI各类需求的编码分布情况");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [openSteps, setOpenSteps] = useState<Set<string>>(new Set());

  const { data: assets } = useQuery({
    queryKey: ["assets", id],
    queryFn: () => api.listAssets(id),
  });

  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => api.uploadAsset(id, formData),
  });

  const analyzeMutation = useMutation({
    mutationFn: async ({ assetId, userQuestion }: { assetId: string; userQuestion: string }) =>
      api.analyzeProjectData(id, { asset_id: assetId, user_question: userQuestion }),
    onSuccess: (data) => {
      setResult(data);
      // Auto-open first step and explainer
      const toOpen = new Set<string>();
      if (data.steps[0]) toOpen.add(data.steps[0].agent);
      const explainer = data.steps.find((s) => s.agent === "ResultExplainerAgent");
      if (explainer) toOpen.add("ResultExplainerAgent");
      setOpenSteps(toOpen);
    },
    onError: (err: Error) => alert("Analysis failed: " + err.message),
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const runAnalysis = async () => {
    let assetId = "";
    if (file) {
      const formData = new FormData();
      formData.append("file", file);
      const uploaded = await uploadMutation.mutateAsync(formData);
      assetId = uploaded.id;
    } else {
      const latest = assets?.find((a) => a.mime_type === "text/csv" || a.filename.endsWith(".xlsx") || a.filename.endsWith(".xls"));
      if (!latest) {
        alert("Please upload an Excel/CSV file first.");
        return;
      }
      assetId = latest.id;
    }
    setResult(null);
    analyzeMutation.mutate({ assetId, userQuestion: question });
  };

  const stepOrder = ["DataProfileAgent", "PlannerAgent", "CodeAgent", "Executor", "RepairAgent", "ResultExplainerAgent"];
  const visibleSteps = result
    ? stepOrder
        .map((name) => result.steps.find((s) => s.agent === name))
        .filter(Boolean) as StepInfo[]
    : [];

  const completedCount = visibleSteps.filter((s) => s.status === "completed").length;
  const progress = visibleSteps.length > 0 ? (completedCount / visibleSteps.length) * 100 : 0;

  const toggleStep = (agent: string) => {
    setOpenSteps((prev) => {
      const next = new Set(prev);
      if (next.has(agent)) next.delete(agent);
      else next.add(agent);
      return next;
    });
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Data Analysis</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Input</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Upload Excel/CSV</label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer rounded-md border px-4 py-2 text-sm hover:bg-accent">
                <Upload className="h-4 w-4" />
                {file ? file.name : "Choose file"}
                <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handleFileChange} />
              </label>
              {assets && assets.length > 0 && (
                <span className="text-xs text-muted-foreground">
                  Or use latest: {assets[assets.length - 1].filename}
                </span>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Your Question</label>
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., Analyze the distribution of eHMI requirement codes"
            />
          </div>

          <Button onClick={runAnalysis} disabled={analyzeMutation.isPending || uploadMutation.isPending}>
            {analyzeMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Play className="mr-2 h-4 w-4" />
            )}
            Run Analysis
          </Button>
        </CardContent>
      </Card>

      {analyzeMutation.isPending && !result && (
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Running analysis pipeline...
            </div>
            <Progress value={33} className="w-full" />
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="space-y-4">
          {/* Progress */}
          <Card>
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Pipeline Progress</span>
                <span className="text-xs text-muted-foreground">{completedCount} / {visibleSteps.length} completed</span>
              </div>
              <Progress value={progress} className="w-full" />
              <div className="flex flex-wrap gap-2">
                {visibleSteps.map((s) => {
                  const meta = stepMeta[s.agent] || { label: s.agent };
                  return (
                    <Badge
                      key={s.agent}
                      variant={s.status === "completed" ? "default" : s.status === "failed" ? "destructive" : "outline"}
                      className="text-[10px]"
                    >
                      {meta.label}
                    </Badge>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Step cards */}
          <div className="space-y-3">
            {visibleSteps.map((step) => (
              <StepCard
                key={step.agent + (step.error ?? "")}
                step={step}
                isOpen={openSteps.has(step.agent)}
                onToggle={() => toggleStep(step.agent)}
              />
            ))}
          </div>

          {/* Final answer */}
          <Card className="bg-primary/5">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Final Answer</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed">{result.final_answer}</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
