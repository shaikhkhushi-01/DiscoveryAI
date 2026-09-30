import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DiscoveryAI",
  description: "AI for Scientific Discovery and Knowledge Gap Detection",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
