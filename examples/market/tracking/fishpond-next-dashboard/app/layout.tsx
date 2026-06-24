import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "统一鱼塘看板",
  description: "近期新高与主题鱼塘统一跟踪"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
