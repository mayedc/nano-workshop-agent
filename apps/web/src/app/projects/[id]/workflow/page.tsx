"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Play, RotateCcw, Plus, Trash2, Save } from "lucide-react";
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState, type Node, type Edge } from "reactflow";
import "reactflow/dist/style.css";

const statusColor: Record<string, string> = {
  pending: "bg-gray-100 text-gray-800",
  in_progress: "bg-blue-100 text-blue-800",
  awaiting_input: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

interface AgentConfig {
  id?: string;
  name: string;
  model?: string;
}

interface LLMConfig {
  provider?: string;
  api_key?: string;
  model?: string;
}

export default function WorkflowPage() {
  const { id } = useParams() as { id: string };
  const queryClient = useQueryClient();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const { data: template, isLoading } = useQuery({
    queryKey: ["template", id],
    queryFn: () => api.getProject(id).then((p) => (p.template_id ? api.getTemplate(p.template_id) : null)),
  });

  const { data: agents } = useQuery({
    queryKey: ["agents"],
    queryFn: api.listAgents,
  });

  const { data: configData } = useQuery({
    queryKey: ["project-config", id],
    queryFn: () => api.getProjectConfig(id),
  });

  const [agentsConfig, setAgentsConfig] = useState<AgentConfig[]>([]);
  const [llmConfig, setLlmConfig] = useState<LLMConfig>({ provider: "zhipu", model: "glm-5.1", api_key: "" });
  const [activeTab, setActiveTab] = useState("agents");

  useEffect(() => {
    if (configData) {
      setAgentsConfig(configData.agents?.length ? configData.agents : []);
      setLlmConfig({
        provider: configData.llm_config?.provider || "zhipu",
        model: configData.llm_config?.model || "glm-5.1",
        api_key: configData.llm_config?.api_key || "",
      });
    }
  }, [configData]);

  const saveConfig = useMutation({
    mutationFn: () =>
      api.updateProjectConfig(id, {
        agents: agentsConfig,
        llm_config: {
          provider: llmConfig.provider,
          model: llmConfig.model,
          api_key: llmConfig.api_key,
        },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project-config", id] });
      alert("Configuration saved");
    },
    onError: (err: Error) => alert("Save failed: " + err.message),
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

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedAgent(node.data.agent);
  };

  const addAgent = () => {
    setAgentsConfig((prev) => [...prev, { name: "NewAgent", model: llmConfig.model || "" }]);
  };

  const removeAgent = (index: number) => {
    setAgentsConfig((prev) => prev.filter((_, i) => i !== index));
  };

  const updateAgent = (index: number, field: keyof AgentConfig, value: string) => {
    setAgentsConfig((prev) => prev.map((a, i) => (i === index ? { ...a, [field]: value } : a)));
  };

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

        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-fit">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="config">Config</TabsTrigger>
          </TabsList>

          <TabsContent value="agents">
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
          </TabsContent>

          <TabsContent value="config">
            <Card className="h-fit">
              <CardHeader>
                <CardTitle>Model Config</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Provider</label>
                  <select
                    className="w-full rounded-md border px-3 py-2 text-sm"
                    value={llmConfig.provider}
                    onChange={(e) => {
                      const provider = e.target.value;
                      const model = provider === "zhipu" ? "glm-5.1" : provider === "anthropic" ? "claude-sonnet-4-6" : "mock";
                      setLlmConfig((c) => ({ ...c, provider, model }));
                    }}
                  >
                    <option value="zhipu">Zhipu (GLM)</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="mock">Mock</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">API Key</label>
                  <Input
                    type="password"
                    placeholder={llmConfig.provider === "zhipu" ? "your.zhipu.key" : "sk-..."}
                    value={llmConfig.api_key}
                    onChange={(e) => setLlmConfig((c) => ({ ...c, api_key: e.target.value }))}
                  />
                  <p className="text-xs text-muted-foreground">Leave empty to keep existing key.</p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Model</label>
                  <Input
                    placeholder="claude-sonnet-4-6"
                    value={llmConfig.model}
                    onChange={(e) => setLlmConfig((c) => ({ ...c, model: e.target.value }))}
                  />
                </div>

                <div className="pt-2 border-t">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium">Agents</label>
                    <Button size="sm" variant="ghost" onClick={addAgent}><Plus className="h-4 w-4" /></Button>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {agentsConfig.map((agent, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <Input
                          className="flex-1 text-sm"
                          placeholder="Agent name"
                          value={agent.name}
                          onChange={(e) => updateAgent(idx, "name", e.target.value)}
                        />
                        <Input
                          className="flex-1 text-sm"
                          placeholder="Model"
                          value={agent.model || ""}
                          onChange={(e) => updateAgent(idx, "model", e.target.value)}
                        />
                        <Button size="sm" variant="ghost" onClick={() => removeAgent(idx)}><Trash2 className="h-4 w-4 text-red-500" /></Button>
                      </div>
                    ))}
                    {agentsConfig.length === 0 && <p className="text-xs text-muted-foreground">No custom agents.</p>}
                  </div>
                </div>

                <Button className="w-full" onClick={() => saveConfig.mutate()} disabled={saveConfig.isPending}>
                  {saveConfig.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                  Save Config
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
