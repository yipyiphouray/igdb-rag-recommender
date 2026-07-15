import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "IGDB Game Discovery",
  description: "A cyberpunk game discovery website powered by IGDB analytics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <SiteHeader />
        <main className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-5 py-8 sm:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
