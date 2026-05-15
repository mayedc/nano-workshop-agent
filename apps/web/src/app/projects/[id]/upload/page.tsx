"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Loader2, UploadCloud, File, CheckCircle, AlertCircle, Trash2 } from "lucide-react";
import { useCallback, useState } from "react";

const roleLabels: Record<string, string> = {
  raw_notes: "Raw Notes",
  transcripts: "Transcripts",
  questionnaire: "Questionnaire",
  images: "Images",
  audio: "Audio",
  video: "Video",
  models: "3D Models",
  tables: "Tables",
};

export default function UploadPage() {
  const { id } = useParams() as { id: string };
  const queryClient = useQueryClient();
  const { setToast } = useAppStore();
  const [uploads, setUploads] = useState<Record<string, number>>({});

  const { data: assets, isLoading } = useQuery({
    queryKey: ["assets", id],
    queryFn: () => api.listAssets(id),
  });

  const upload = useMutation({
    mutationFn: async ({ file, role }: { file: File; role: string }) => {
      const form = new FormData();
      form.append("file", file);
      form.append("semantic_role", role);
      return api.uploadAsset(id, form);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets", id] });
      setToast({ message: "Upload complete", type: "success" });
    },
    onError: (e: Error) => setToast({ message: e.message, type: "error" }),
  });

  const deleteAsset = useMutation({
    mutationFn: (assetId: string) => api.deleteAsset(assetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets", id] });
      setToast({ message: "Asset deleted", type: "success" });
    },
    onError: (e: Error) => setToast({ message: e.message, type: "error" }),
  });

  const handleDrop = useCallback(
    (e: React.DragEvent, role: string) => {
      e.preventDefault();
      const files = Array.from(e.dataTransfer.files);
      files.forEach((file) => {
        setUploads((prev) => ({ ...prev, [file.name]: 50 }));
        upload.mutate({ file, role });
      });
    },
    [upload]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, role: string) => {
    const files = Array.from(e.target.files || []);
    files.forEach((file) => {
      setUploads((prev) => ({ ...prev, [file.name]: 50 }));
      upload.mutate({ file, role });
    });
  };

  const processingBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="mr-1 h-3 w-3" />Completed</Badge>;
      case "failed":
        return <Badge className="bg-red-100 text-red-800"><AlertCircle className="mr-1 h-3 w-3" />Failed</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800"><Loader2 className="mr-1 h-3 w-3 animate-spin" />Processing</Badge>;
      default:
        return <Badge variant="outline">Pending</Badge>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Upload Materials</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(roleLabels).map(([role, label]) => (
          <Card
            key={role}
            className="border-dashed hover:border-solid hover:bg-accent/50 transition-colors"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e, role)}
          >
            <CardHeader>
              <CardTitle className="text-sm font-medium">{label}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <label className="flex cursor-pointer flex-col items-center justify-center rounded-md border border-dashed py-6 text-muted-foreground hover:text-foreground">
                <UploadCloud className="mb-2 h-6 w-6" />
                <span className="text-xs">Drop files or click to upload</span>
                <input type="file" multiple className="hidden" onChange={(e) => handleFileSelect(e, role)} />
              </label>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Uploaded Assets</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <div className="flex justify-center py-6"><Loader2 className="h-6 w-6 animate-spin" /></div>
          ) : !assets?.length ? (
            <p className="text-sm text-muted-foreground">No assets uploaded yet.</p>
          ) : (
            assets.map((a) => (
              <div key={a.id} className="flex items-center justify-between rounded-md border p-3">
                <div className="flex items-center gap-3">
                  <File className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{a.filename}</p>
                    <p className="text-xs text-muted-foreground">{a.semantic_role || a.asset_type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {uploads[a.filename] !== undefined && uploads[a.filename] < 100 && (
                    <Progress value={uploads[a.filename]} max={100} className="w-24" />
                  )}
                  {processingBadge(a.processing_status)}
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={deleteAsset.isPending}
                    onClick={() => { if (confirm(`Delete "${a.filename}"?`)) deleteAsset.mutate(a.id); }}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
