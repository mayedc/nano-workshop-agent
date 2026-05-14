"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, CheckCircle, XCircle, MessageSquare, AlertCircle, RefreshCw, Send } from "lucide-react";
import { TARGET_TYPES, REVIEW_ACTIONS } from "@/types";
import type { ExpertFeedback, AgentRun } from "@/types";

const actionIcons: Record<string, React.ReactNode> = {
  approve: <CheckCircle className="h-4 w-4 text-green-600" />,
  reject: <XCircle className="h-4 w-4 text-red-600" />,
  revise: <MessageSquare className="h-4 w-4 text-yellow-600" />,
  merge: <MessageSquare className="h-4 w-4 text-blue-600" />,
  split: <MessageSquare className="h-4 w-4 text-purple-600" />,
  score: <MessageSquare className="h-4 w-4 text-orange-600" />,
  comment: <MessageSquare className="h-4 w-4 text-gray-600" />,
  request_rerun: <RefreshCw className="h-4 w-4 text-red-600" />,
};

const statusBadge: Record<string, string> = {
  pending: "bg-gray-100 text-gray-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  revised: "bg-yellow-100 text-yellow-800",
  pending_rerun: "bg-orange-100 text-orange-800",
};

export default function ReviewPage() {
  const { id: projectId } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    target_type: "themes",
    target_id: "",
    action: "approve",
    score: 0,
    comment: "",
    suggested_revision: "",
  });
  const [message, setMessage] = useState("");

  const { data: feedbackList, isLoading: fbLoading } = useQuery({
    queryKey: ["feedback", projectId],
    queryFn: () => api.listFeedback({ project_id: projectId }),
  });

  const { data: agentRuns } = useQuery({
    queryKey: ["agentRuns"],
    queryFn: api.listAgentRuns,
  });

  const createMutation = useMutation({
    mutationFn: () => {
      const data: Record<string, unknown> = {
        project_id: projectId,
        target_type: form.target_type,
        target_id: form.target_id,
        action: form.action,
      };
      if (form.score > 0) data.score = form.score;
      if (form.comment.trim()) data.comment = form.comment.trim();
      if (form.suggested_revision.trim()) {
        try {
          data.suggested_revision = JSON.parse(form.suggested_revision.trim());
        } catch {
          setMessage("Invalid JSON in suggested revision");
          throw new Error("Invalid JSON");
        }
      }
      return api.createFeedback(data as Parameters<typeof api.createFeedback>[0]);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["feedback", projectId] });
      setForm({ ...form, target_id: "", score: 0, comment: "", suggested_revision: "" });
      setMessage("Feedback submitted successfully");
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const runWorkflowMutation = useMutation({
    mutationFn: () =>
      api.runWorkflow({
        project_id: projectId,
        steps: [
          { id: 1, agent: "IterationAgent", depends_on: [], inputs: { iteration: 1, feedback: feedbackList || [] } },
        ],
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["feedback", projectId] });
      queryClient.invalidateQueries({ queryKey: ["agentRuns"] });
      setMessage("Rerun workflow started");
    },
  });

  const fb = feedbackList || [];
  const runs = (agentRuns as AgentRun[]) || [];

  const counts = {
    pending: fb.filter((f) => f.review_status === "pending").length,
    approved: fb.filter((f) => f.action === "approve").length,
    rejected: fb.filter((f) => f.action === "reject").length,
    revised: fb.filter((f) => f.action === "revise").length,
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Expert Review</h1>
        <Button onClick={() => runWorkflowMutation.mutate()} disabled={runWorkflowMutation.isPending}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Rerun Iteration
        </Button>
      </div>

      {message && (
        <div className="rounded-md bg-muted px-4 py-2 text-sm">{message}</div>
      )}

      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Pending</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{counts.pending}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Approved</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{counts.approved}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Rejected</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{counts.rejected}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Revised</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{counts.revised}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Submit Expert Feedback</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Target Type</label>
              <Select value={form.target_type} onChange={(e) => setForm({ ...form, target_type: e.target.value })}>
                {TARGET_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Target ID</label>
              <Input
                placeholder="e.g. theme UUID"
                value={form.target_id}
                onChange={(e) => setForm({ ...form, target_id: e.target.value })}
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Action</label>
              <Select value={form.action} onChange={(e) => setForm({ ...form, action: e.target.value })}>
                {REVIEW_ACTIONS.map((a) => (
                  <option key={a} value={a}>{a.replace("_", " ")}</option>
                ))}
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Score (1-5, optional)</label>
              <Input
                type="number"
                min={1}
                max={5}
                value={form.score || ""}
                onChange={(e) => setForm({ ...form, score: parseInt(e.target.value) || 0 })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Comment</label>
            <Textarea
              placeholder="Review comment..."
              value={form.comment}
              onChange={(e) => setForm({ ...form, comment: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Suggested Revision (JSON, optional)</label>
            <Textarea
              placeholder='{"field": "name", "value": "Updated name"}'
              value={form.suggested_revision}
              onChange={(e) => setForm({ ...form, suggested_revision: e.target.value })}
            />
          </div>

          <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !form.target_id}>
            <Send className="mr-2 h-4 w-4" />
            {createMutation.isPending ? "Submitting..." : "Submit Feedback"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Review History</CardTitle></CardHeader>
        <CardContent>
          {fbLoading ? (
            <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin" /></div>
          ) : fb.length === 0 ? (
            <p className="text-center text-muted-foreground py-10">No feedback yet. Submit your first review above.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Action</TableHead>
                  <TableHead>Target</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Comment</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {fb.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {actionIcons[f.action] || <AlertCircle className="h-4 w-4" />}
                        <span className="capitalize">{f.action.replace("_", " ")}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{f.target_type}</Badge>
                      <span className="ml-2 text-xs text-muted-foreground">{f.target_id.slice(0, 8)}...</span>
                    </TableCell>
                    <TableCell>{f.score ?? "--"}</TableCell>
                    <TableCell className="max-w-xs truncate">{f.comment || "--"}</TableCell>
                    <TableCell>
                      <Badge className={statusBadge[f.review_status] || "bg-gray-100"}>{f.review_status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(f.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Agent Run Review Status</CardTitle></CardHeader>
        <CardContent>
          {runs.length === 0 ? (
            <p className="text-center text-muted-foreground py-10">No agent runs yet.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agent</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Review</TableHead>
                  <TableHead>Confidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.map((run) => (
                  <TableRow key={run.id}>
                    <TableCell className="font-medium">{run.agent_name}</TableCell>
                    <TableCell><Badge variant="outline">{run.status}</Badge></TableCell>
                    <TableCell>
                      <Badge className={statusBadge[run.review_status] || "bg-gray-100"}>{run.review_status}</Badge>
                    </TableCell>
                    <TableCell>{run.confidence ? (run.confidence * 100).toFixed(0) + "%" : "--"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
