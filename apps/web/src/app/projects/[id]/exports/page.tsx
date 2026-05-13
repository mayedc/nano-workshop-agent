"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, Download, FileText, FileSpreadsheet, Presentation } from "lucide-react";

const formatIcon: Record<string, React.ReactNode> = {
  docx: <FileText className="h-4 w-4" />,
  pdf: <FileText className="h-4 w-4" />,
  pptx: <Presentation className="h-4 w-4" />,
  xlsx: <FileSpreadsheet className="h-4 w-4" />,
};

export default function ExportsPage() {
  const { data: exports, isLoading } = useQuery({
    queryKey: ["exports"],
    queryFn: api.listAgentRuns,
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Exports</h1>
        <Button><Download className="mr-2 h-4 w-4" />Export All</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Generated Exports</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin" /></div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Format</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Generated</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(exports || []).length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center text-muted-foreground">No exports yet.</TableCell>
                  </TableRow>
                ) : (
                  (exports || []).map((ex: any) => (
                    <TableRow key={ex.id}>
                      <TableCell><div className="flex items-center gap-2">{formatIcon[ex.format] || <FileText className="h-4 w-4" />}<span className="uppercase">{ex.format}</span></div></TableCell>
                      <TableCell><Badge variant="outline">{ex.status}</Badge></TableCell>
                      <TableCell>{new Date(ex.created_at).toLocaleDateString()}</TableCell>
                      <TableCell><Button variant="outline" size="sm">Download</Button></TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
