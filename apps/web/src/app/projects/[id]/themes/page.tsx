"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Lightbulb, TrendingUp } from "lucide-react";

interface Theme {
  id: string;
  name: string;
  description: string;
  codeCount: number;
  evidenceCount: number;
  confidence: number;
}

export default function ThemesPage() {
  const [themes] = useState<Theme[]>([
    { id: "1", name: "Trust Building", description: "How eHMI builds trust between pedestrians and AVs", codeCount: 4, evidenceCount: 24, confidence: 0.91 },
    { id: "2", name: "Safety Perception", description: "Factors influencing perceived safety", codeCount: 3, evidenceCount: 18, confidence: 0.87 },
    { id: "3", name: "Intention Communication", description: "Clarity of AV intent signaling", codeCount: 3, evidenceCount: 15, confidence: 0.82 },
  ]);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Themes</h1>

      <div className="grid gap-4">
        {themes.map((t) => (
          <Card key={t.id}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-yellow-500" />
                  <CardTitle className="text-lg">{t.name}</CardTitle>
                </div>
                <Badge variant="secondary">{Math.round(t.confidence * 100)}% confidence</Badge>
              </div>
              <CardDescription>{t.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{t.codeCount} codes</span>
                <span>{t.evidenceCount} evidence</span>
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span>Confidence</span>
                  <span className="font-medium">{t.confidence}</span>
                </div>
                <Progress value={t.confidence * 100} max={100} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
