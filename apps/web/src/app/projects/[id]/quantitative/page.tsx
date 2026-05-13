"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";

const likertData = [
  { name: "Trust", mean: 3.8 },
  { name: "Safety", mean: 4.2 },
  { name: "Visibility", mean: 3.5 },
  { name: "Clarity", mean: 4.0 },
  { name: "Timeliness", mean: 3.6 },
];

const radarData = [
  { subject: "Trust", A: 3.8, fullMark: 5 },
  { subject: "Safety", A: 4.2, fullMark: 5 },
  { subject: "Visibility", A: 3.5, fullMark: 5 },
  { subject: "Clarity", A: 4.0, fullMark: 5 },
  { subject: "Timeliness", A: 3.6, fullMark: 5 },
];

const sigTests = [
  { test: "t-test (trust vs baseline)", p_value: 0.03, significant: true },
  { test: "ANOVA (safety groups)", p_value: 0.12, significant: false },
  { test: "Mann-Whitney (visibility)", p_value: 0.01, significant: true },
];

export default function QuantitativePage() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Quantitative Analysis</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Sample Size</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">42</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Cronbach Alpha</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">0.87</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Factors</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">3</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Significant</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">2/3</div></CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Likert Means</CardTitle></CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={likertData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Bar dataKey="mean" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Radar Profile</CardTitle></CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis domain={[0, 5]} />
                <Radar name="Mean" dataKey="A" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.3} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Significance Tests</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Test</TableHead>
                <TableHead>p-value</TableHead>
                <TableHead>Result</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sigTests.map((t, i) => (
                <TableRow key={i}>
                  <TableCell>{t.test}</TableCell>
                  <TableCell>{t.p_value.toFixed(3)}</TableCell>
                  <TableCell>
                    {t.significant ? (
                      <Badge className="bg-green-100 text-green-800">Significant</Badge>
                    ) : (
                      <Badge variant="outline">Not significant</Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
