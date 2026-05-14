"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Select } from "@/components/ui/select";
import { Plus, Loader2, ArrowRight } from "lucide-react";
import type { Project } from "@/types";

const statusColor: Record<Project["status"], string> = {
  draft: "bg-yellow-100 text-yellow-800",
  active: "bg-green-100 text-green-800",
  completed: "bg-blue-100 text-blue-800",
  archived: "bg-gray-100 text-gray-800",
};

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const { setToast } = useAppStore();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<Project["status"]>("draft");

  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: api.listProjects,
  });

  const create = useMutation({
    mutationFn: api.createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setToast({ message: "Project created", type: "success" });
      setOpen(false);
      setName("");
      setDescription("");
    },
    onError: (e: Error) => setToast({ message: e.message, type: "error" }),
  });

  return (
    <div className="min-h-screen bg-background">
      <header className="flex h-16 items-center justify-between border-b px-6">
        <h1 className="text-xl font-bold">Projects</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />New Project</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Project</DialogTitle>
              <DialogDescription>Start a new workshop analysis project.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Project name" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Short description" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Status</label>
                <Select value={status} onChange={(e) => setStatus(e.target.value as Project["status"])}>
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button
                disabled={!name || create.isPending}
                onClick={() => create.mutate({ name, description, status })}
              >
                {create.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </header>

      <main className="p-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
        ) : !projects?.length ? (
          <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <p className="text-lg font-medium">No projects yet</p>
            <p className="text-sm">Create your first workshop project to get started.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <Card key={p.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{p.name}</CardTitle>
                    <Badge className={statusColor[p.status]}>{p.status}</Badge>
                  </div>
                  <CardDescription className="line-clamp-2">{p.description || "No description"}</CardDescription>
                </CardHeader>
                <CardContent className="pb-3">
                  <div className="text-xs text-muted-foreground">
                    Updated {new Date(p.updated_at).toLocaleDateString()}
                  </div>
                </CardContent>
                <CardFooter>
                  <Link href={`/projects/${p.id}/dashboard`}>
                    <Button variant="secondary" className="w-full">
                      Open <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
