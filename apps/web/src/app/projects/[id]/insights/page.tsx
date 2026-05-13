"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Lightbulb, CheckCircle, XCircle, MessageSquare } from "lucide-react";

interface Insight {
  id: string;
  title: string;
  confidence: number;
  supporting: string[];
  status: "pending" | "approved" | "rejected" | "revised";
  comment: string;
}

export default function InsightsPage() {
  const [insights, setInsights] = useState<Insight[]>([
    { id: "1", title: "Color-coded intent signals improve trust", confidence: 0.91, supporting: ["ev-1", "ev-3"], status: "approved", comment: "" },
    { id: "2", title: "Pedestrians prefer frontal displays", confidence: 0.87, supporting: ["ev-2"], status: "pending", comment: "" },
    { id: "3", title: "Audio cues reduce reaction time by 200ms", confidence: 0.76, supporting: ["ev-4", "ev-5"], status: "pending", comment: "" },
  ]);

  const setStatus = (id: string, status: Insight["status"]) => {
    setInsights((prev) => prev.map((i) => (i.id === id ? { ...i, status } : i)));
  };

  const statusBadge = (status: string) => {
    switch (status) {
      case "approved": return <Badge className="bg-green-100 text-green-800"><CheckCircle className="mr-1 h-3 w-3" />Approved</Badge>;
      case "rejected": return <Badge className="bg-red-100 text-red-800"><XCircle className="mr-1 h-3 w-3" />Rejected</Badge>;
      case "revised": return <Badge className="bg-yellow-100 text-yellow-800">Revised</Badge>;
      default: return <Badge variant="outline">Pending</Badge>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Design Insights</h1>

      <Tabs value="all" onValueChange={() => {}}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="approved">Approved</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="grid gap-4">
        {insights.map((insight) => (
          <Card key={insight.id}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-yellow-500" />
                  <CardTitle className="text-base">{insight.title}</CardTitle>
                </div>
                {statusBadge(insight.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span>Confidence</span>
                  <span className="font-medium">{Math.round(insight.confidence * 100)}%</span>
                </div>
                <Progress value={insight.confidence * 100} max={100} />
              </div>

              <div className="flex flex-wrap gap-2">
                {insight.supporting.map((ev) => (
                  <Badge key={ev} variant="secondary">{ev}</Badge>
                ))}
              </div>

              {insight.status === "pending" && (
                <div className="flex gap-2">
                  <button onClick={() => setStatus(insight.id, "approved")} className="inline-flex items-center gap-1 rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700">
                    <CheckCircle className="h-3 w-3" /> Approve
                  </button>
                  <button onClick={() => setStatus(insight.id, "rejected")} className="inline-flex items-center gap-1 rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700">
                    <XCircle className="h-3 w-3" /> Reject
                  </button>
                  <button onClick={() => setStatus(insight.id, "revised")} className="inline-flex items-center gap-1 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent">
                    <MessageSquare className="h-3 w-3" /> Revise
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
