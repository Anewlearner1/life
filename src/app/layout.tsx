import type { Metadata, Viewport } from "next";
import Header from "@/components/Header/Header";
import Footer from "@/components/Footer/Footer";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "ToolBox 文字工具箱", template: "%s | ToolBox 文字工具箱" },
  description: "免費的繁體中文線上文字工具:文字去重複、文字清理器。所有處理都在你的瀏覽器本機完成,不上傳文字。",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-Hant">
      <body>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
