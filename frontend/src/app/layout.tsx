import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { AppProviders } from "@/infrastructure/http/providers";
import "./globals.css";

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WEB_MINERA",
  description: "Plataforma digital de trazabilidad y cadena de custodia",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body className={`${geist.variable} antialiased`}>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
