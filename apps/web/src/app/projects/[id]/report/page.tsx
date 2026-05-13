"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { FileText, Download, CheckCircle } from "lucide-react";

interface ReportSection {
  title: string;
  type: string;
  status: "pending" | "completed";
  source_steps: number[];
}

export default function ReportPage() {
  const sections: ReportSection[] = [
    { title: "Executive Summary", type: "summary", status: "completed", source_steps: [1] },
    { title: "Methodology", type: "method", status: "completed", source_steps: [2] },
    { title: "Findings", type: "findings", status: "completed", source_steps: [3, 4] },
    { title: "Recommendations", type: "recommendations", status: "pending", source_steps: [5] },
  ];

  const completed = sections.filter((s) => s.status === "completed").length;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Report</h1>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Report Generation Progress</CardTitle>
            <Button><Download className="mr-2 h-4 w-4" />Export</Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span>{completed} of {sections.length} sections complete</span>
              <span className="font-medium">{Math.round((completed / sections.length) * 100)}%</span>
            </div>
            <Progress value={completed} max={sections.length} />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {sections.map((s) => (
          <Card key={s.title} className={s.status === "completed" ? "border-green-200" : ""}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <CardTitle className="text-base">{s.title}</CardTitle>
                </div>
                {s.status === "completed" ? (
                  <Badge className="bg-green-100 text-green-800"><CheckCircle className="mr-1 h-3 w-3" />Completed</Badge>
                ) : (
                  <Badge variant="outline">Pending</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                <span className="text-xs text-muted-foreground">Source steps:</span>
                {s.source_steps.map((step) => (
                  <Badge key={step} variant="secondary">Step {step}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
