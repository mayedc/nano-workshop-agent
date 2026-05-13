"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Box, Plus, Wand2 } from "lucide-react";

interface Concept {
  id: string;
  name: string;
  description: string;
  prompt: string;
  status: "draft" | "generated" | "reviewed";
}

export default function PrototypesPage() {
  const [concepts, setConcepts] = useState<Concept[]>([
    { id: "1", name: "Front LED Bar", description: "Horizontal LED strip indicating intent", prompt: "A sleek front LED bar on an AV showing green for go, red for stop", status: "generated" },
    { id: "2", name: "Roof Display", description: "Overhead display visible from all angles", prompt: "A roof-mounted eHMI display with directional arrows", status: "draft" },
  ]);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const addConcept = () => {
    if (!name) return;
    setConcepts((prev) => [...prev, { id: String(Date.now()), name, description, prompt: "", status: "draft" }]);
    setOpen(false);
    setName("");
    setDescription("");
  };

  const generate = (id: string) => {
    setConcepts((prev) => prev.map((c) => c.id === id ? { ...c, status: "generated" as const, prompt: `Generated image for ${c.name}` } : c));
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Prototypes</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Concept</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>New Design Concept</DialogTitle></DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Concept name" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe the concept" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={addConcept}>Save</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {concepts.map((c) => (
          <Card key={c.id}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Box className="h-4 w-4 text-muted-foreground" />
                  <CardTitle className="text-base">{c.name}</CardTitle>
                </div>
                <Badge variant={c.status === "generated" ? "default" : "outline"}>{c.status}</Badge>
              </div>
              <CardDescription>{c.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {c.prompt && <div className="rounded-md bg-muted p-3 text-xs text-muted-foreground">{c.prompt}</div>}
              {c.status === "draft" && (
                <Button variant="outline" className="w-full" onClick={() => generate(c.id)}>
                  <Wand2 className="mr-2 h-4 w-4" /> Generate
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
