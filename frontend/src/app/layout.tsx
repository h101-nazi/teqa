import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Teqa - AI Business Intelligence for Egyptian SMBs",
  description:
    "Get daily AI-powered business insights delivered to your WhatsApp. No dashboards, no spreadsheets — just actionable intelligence.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" dir="ltr">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
