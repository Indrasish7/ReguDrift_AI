import type { Metadata } from "next";
import { Hanken_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const hankenGrotesk = Hanken_Grotesk({
  subsets: ["latin"],
  variable: "--font-hanken-grotesk",
  weight: ["300", "400", "600", "700", "800"],
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "ReguDrift AI | CISO Command Center",
  description: "Enterprise Asynchronous AI Compliance and Relational Persistence Carrier",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${hankenGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable} font-body-md bg-background text-on-background min-h-screen flex overflow-hidden`}
      >
        {children}
      </body>
    </html>
  );
}
