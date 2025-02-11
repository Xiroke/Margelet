import type { Metadata } from "next";
import { Roboto } from "next/font/google";
import "./globals.css";

const roboto = Roboto({
  weight: ["400", "500", "700"],
  subsets: ["cyrillic", "latin"],
  variable: "--font-roboto",
});

export const metadata: Metadata = {
  title: "R",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body
        className={`${roboto.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
