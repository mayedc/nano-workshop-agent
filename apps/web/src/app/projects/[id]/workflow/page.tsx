"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Play, RotateCcw } from "lucide-react";
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState, type Node, type Edge } from "reactflow";
import "reactflow/dist/style.css";

const statusColor: Record<string, string> = {
  pending: "bg-gray-100 text-gray-800",
  in_progress: "bg-blue-100 text-blue-800",
  awaiting_input: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

export default function WorkflowPage() {
  const { id } = useParams() as { id: string };
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const { data: template, isLoading } = useQuery({
    queryKey: ["template", id],
    queryFn: () => api.getProject(id).then((p) => (p.template_id ? api.getTemplate(p.template_id) : null)),
  });

  const { data: agents } = useQuery({
    queryKey: ["agents"],
    queryFn: api.listAgents,
  });

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!template?.workflow_steps) return;
    const newNodes: Node[] = template.workflow_steps.map((step, i) => ({
      id: String(step.id),
      data: { label: step.name, agent: step.agent_name, status: step.status },
      position: { x: 200 + i * 20, y: 100 + i * 120 },
      style: {
        borderRadius: 8,
        padding: 10,
        border: "1px solid #e2e8f0",
        background: "white",
        width: 220,
      },
    }));
    const newEdges: Edge[] = template.workflow_steps.flatMap((step) =>
      (step.depends_on || []).map((dep) => ({
        id: `${dep}-${step.id}`,
        source: String(dep),
        target: String(step.id),
        animated: step.status === "in_progress",
        style: { stroke: step.status === "completed" ? "#22c55e" : "#94a3b8" },
      }))
    );
    setNodes(newNodes);
    setEdges(newEdges);
  }, [template, setNodes, setEdges]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedAgent(node.data.agent);
  }, []);

  return (
    <div className="p-6 space-y-6 h-[calc(100vh-3rem)]">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Workflow</h1>
        <div className="flex gap-2">
          <Button variant="outline"><RotateCcw className="mr-2 h-4 w-4" />Reset</Button>
          <Button><Play className="mr-2 h-4 w-4" />Run All</Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4 h-full">
        <Card className="lg:col-span-3 h-full">
          <CardContent className="h-full p-0">
            {isLoading ? (
              <div className="flex items-center justify-center h-full"><Loader2 className="h-8 w-8 animate-spin" /></div>
            ) : (
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
                fitView
              >
                <Background />
                <Controls />
                <MiniMap />
              </ReactFlow>
            )}
          </CardContent>
        </Card>

        <Card className="h-fit">
          <CardHeader><CardTitle>Agents</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {agents?.map((agent) => (
              <div
                key={agent}
                className={`rounded-md border p-3 cursor-pointer transition-colors ${selectedAgent === agent ? "border-primary bg-primary/5" : "hover:bg-accent"}`}
                onClick={() => setSelectedAgent(agent)}
              >
                <p className="text-sm font-medium">{agent}</p>
              </div>
            )) || <p className="text-sm text-muted-foreground">No agents registered.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
