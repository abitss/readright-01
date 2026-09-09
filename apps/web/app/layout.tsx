import type { Metadata } from "next";
import "@readright/design-system/tokens.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReadRight",
  description: "Learning Intelligence Infrastructure for foundational learning.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
