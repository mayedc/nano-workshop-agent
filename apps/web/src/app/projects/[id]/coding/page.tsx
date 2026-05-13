"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tag, Plus, Trash2 } from "lucide-react";

interface CodeItem {
  id: string;
  name: string;
  description: string;
  evidenceCount: number;
}

export default function CodingPage() {
  const { id } = useParams() as { id: string };
  const [codes, setCodes] = useState<CodeItem[]>([
    { id: "1", name: "Trust", description: "References to trust in automation", evidenceCount: 12 },
    { id: "2", name: "Safety", description: "Perceived safety concerns", evidenceCount: 8 },
    { id: "3", name: "Visibility", description: "Need for clear signals", evidenceCount: 5 },
  ]);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const addCode = () => {
    if (!name) return;
    setCodes((prev) => [...prev, { id: String(Date.now()), name, description, evidenceCount: 0 }]);
    setOpen(false);
    setName("");
    setDescription("");
  };

  const removeCode = (cid: string) => setCodes((prev) => prev.filter((c) => c.id !== cid));

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Coding</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Code</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>New Code</DialogTitle></DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Code name" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What does this code capture?" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={addCode}>Save</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {codes.map((c) => (
          <Card key={c.id}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Tag className="h-4 w-4 text-muted-foreground" />
                  <CardTitle className="text-base">{c.name}</CardTitle>
                </div>
                <button onClick={() => removeCode(c.id)} className="rounded p-1 hover:bg-destructive/10">
                  <Trash2 className="h-4 w-4 text-destructive" />
                </button>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground">{c.description}</p>
              <Badge variant="secondary">{c.evidenceCount} evidence</Badge>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
