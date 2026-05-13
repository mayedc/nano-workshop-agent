import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nano Workshop Agent",
  description: "Agentic AI platform for academic workshop data analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
