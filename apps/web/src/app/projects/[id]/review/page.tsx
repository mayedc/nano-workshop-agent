"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CheckCircle, XCircle, AlertCircle, MessageSquare } from "lucide-react";

interface ReviewItem {
  id: string;
  type: "code" | "theme" | "insight";
  name: string;
  reviewer: string;
  status: "pending" | "approved" | "rejected" | "revised";
  comment: string;
  confidence: number;
}

export default function ReviewPage() {
  const [items] = useState<ReviewItem[]>([
    { id: "1", type: "code", name: "Trust", reviewer: "Dr. Smith", status: "approved", comment: "Well-defined", confidence: 0.92 },
    { id: "2", type: "theme", name: "Trust Building", reviewer: "Dr. Smith", status: "approved", comment: "Good coverage", confidence: 0.88 },
    { id: "3", type: "insight", name: "Color-coded intent signals", reviewer: "Dr. Lee", status: "pending", comment: "", confidence: 0.91 },
    { id: "4", type: "insight", name: "Frontal displays preferred", reviewer: "Dr. Lee", status: "rejected", comment: "Needs more evidence", confidence: 0.65 },
  ]);

  const statusIcon = (status: string) => {
    switch (status) {
      case "approved": return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "rejected": return <XCircle className="h-4 w-4 text-red-600" />;
      case "revised": return <MessageSquare className="h-4 w-4 text-yellow-600" />;
      default: return <AlertCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const typeColor: Record<string, string> = {
    code: "bg-purple-100 text-purple-800",
    theme: "bg-blue-100 text-blue-800",
    insight: "bg-yellow-100 text-yellow-800",
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Expert Review</h1>

      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Pending</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{items.filter((i) => i.status === "pending").length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Approved</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{items.filter((i) => i.status === "approved").length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Rejected</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{items.filter((i) => i.status === "rejected").length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Avg Confidence</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{(items.reduce((a, b) => a + b.confidence, 0) / items.length).toFixed(2)}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Review Queue</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Reviewer</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Comment</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell><Badge className={typeColor[item.type]}>{item.type}</Badge></TableCell>
                  <TableCell className="font-medium">{item.name}</TableCell>
                  <TableCell>{item.reviewer}</TableCell>
                  <TableCell><div className="flex items-center gap-2">{statusIcon(item.status)}<span className="capitalize">{item.status}</span></div></TableCell>
                  <TableCell><Progress value={item.confidence * 100} max={100} className="w-24" /></TableCell>
                  <TableCell className="max-w-xs truncate">{item.comment || "--"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
