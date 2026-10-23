import type { Metadata } from "next";
import TextCleanerTool from "@/components/tools/TextCleanerTool";

export const metadata: Metadata = {
  title: "文字清理器",
  description: "免費線上文字清理:移除行首尾空白、移除空白行、合併連續空格,即時顯示結果。文字僅在瀏覽器本機處理。",
};

export default function Page() {
  return (
    <main>
      <h1>文字清理器</h1>
      <p className="lead">勾選需要的選項,即時整理多餘的空白與空白行。文字不會上傳,全部在你的瀏覽器中處理。</p>
      <section aria-label="文字清理器工具">
        <TextCleanerTool />
      </section>
    </main>
  );
}
