import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Blog Studio",
  description: "Write and publish blog posts with AI-powered editing tools",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
