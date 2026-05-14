"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, FileText } from "lucide-react";

export default function EvidencePage() {
  const { id } = useParams() as { id: string };
  const { data: evidence, isLoading } = useQuery({
    queryKey: ["evidence", id],
    queryFn: () => api.listProjectEvidence(id),
  });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Evidence</h1>
      <Card>
        <CardHeader><CardTitle>All Evidence</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin" /></div>
          ) : !evidence?.length ? (
            <div className="flex flex-col items-center justify-center py-10 text-muted-foreground">
              <FileText className="mb-2 h-8 w-8" />
              <p>No evidence yet.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Content</TableHead>
                  <TableHead>Asset</TableHead>
                  <TableHead>Extracted</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {evidence.map((e) => (
                  <TableRow key={e.id}>
                    <TableCell><Badge variant="outline">{e.type}</Badge></TableCell>
                    <TableCell className="max-w-xs truncate">{e.content}</TableCell>
                    <TableCell>{e.asset_id || "--"}</TableCell>
                    <TableCell>{new Date(e.extracted_at).toLocaleDateString()}</TableCell>
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
