import { AppShell } from "@/components/layout/AppShell";

export default async function ProjectLayout({ children, params }: { children: React.ReactNode; params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <AppShell projectId={id}>{children}</AppShell>;
}
