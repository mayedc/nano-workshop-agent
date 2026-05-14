"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, Download, FileText, FileSpreadsheet, Presentation, FileJson } from "lucide-react";
import { EXPORT_FORMATS } from "@/types";
import type { ExportRecord } from "@/types";

const formatMeta: Record<string, { icon: React.ReactNode; label: string; color: string }> = {
  docx: { icon: <FileText className="h-5 w-5" />, label: "Word Report", color: "bg-blue-100 text-blue-800" },
  pptx: { icon: <Presentation className="h-5 w-5" />, label: "PowerPoint", color: "bg-orange-100 text-orange-800" },
  json: { icon: <FileJson className="h-5 w-5" />, label: "JSON Metadata", color: "bg-green-100 text-green-800" },
  csv: { icon: <FileSpreadsheet className="h-5 w-5" />, label: "CSV Tables", color: "bg-purple-100 text-purple-800" },
};

const formatDescriptions: Record<string, string> = {
  docx: "12-section academic report with tables (codes, themes, requirements)",
  pptx: "11-slide presentation covering all workshop stages",
  json: "Complete project metadata including all entities and agent runs",
  csv: "ZIP archive with codes, themes, requirements, questionnaire_stats, expert_feedback CSVs",
};

export default function ExportsPage() {
  const { id: projectId } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const { data: exports, isLoading } = useQuery({
    queryKey: ["exports", projectId],
    queryFn: () => api.listProjectExports(projectId!),
  });

  const exportMutation = useMutation({
    mutationFn: (format: string) => api.generateExport(projectId!, format),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["exports", projectId] });
    },
  });

  const items = (exports || []) as ExportRecord[];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Exports</h1>
          <p className="text-sm text-muted-foreground mt-1">Generate and download project deliverables</p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {EXPORT_FORMATS.map((format) => {
          const meta = formatMeta[format] || { icon: <Download className="h-5 w-5" />, label: format, color: "bg-gray-100" };
          return (
            <Card key={format}>
              <CardContent className="pt-6 space-y-3">
                <div className="flex items-center gap-2">
                  <Badge className={meta.color}>{meta.icon}</Badge>
                  <span className="font-semibold uppercase text-sm">{format}</span>
                </div>
                <p className="text-xs text-muted-foreground">{formatDescriptions[format]}</p>
                <Button
                  className="w-full"
                  variant="outline"
                  size="sm"
                  onClick={() => exportMutation.mutate(format)}
                  disabled={exportMutation.isPending}
                >
                  {exportMutation.isPending && exportMutation.variables === format ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="mr-2 h-4 w-4" />
                  )}
                  {meta.label}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader><CardTitle>Export History</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin" /></div>
          ) : items.length === 0 ? (
            <p className="text-center text-muted-foreground py-10">No exports yet. Generate one above.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Format</TableHead>
                  <TableHead>Filename</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Generated</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((ex: ExportRecord) => {
                  const meta = formatMeta[ex.format] || { icon: <FileText className="h-4 w-4" />, label: ex.format };
                  const config = ex.config as Record<string, unknown> || {};
                  const sizeBytes = (config.size_bytes as number) || 0;
                  const sizeStr = sizeBytes > 1024 * 1024
                    ? `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`
                    : sizeBytes > 1024
                      ? `${(sizeBytes / 1024).toFixed(1)} KB`
                      : `${sizeBytes} B`;
                  const filename = (config.filename as string) || `${ex.format} export`;
                  return (
                    <TableRow key={ex.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {meta.icon}
                          <span className="uppercase font-medium">{ex.format}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm">{filename}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{sizeBytes ? sizeStr : "--"}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(ex.generated_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => api.generateExport(projectId!, ex.format)}
                        >
                          <Download className="mr-2 h-3 w-3" /> Re-download
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
