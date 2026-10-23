import type { Metadata } from "next";
import RemoveDuplicateLinesTool from "@/components/tools/RemoveDuplicateLinesTool";

export const metadata: Metadata = {
  title: "文字去重複",
  description: "免費線上移除重複行,保留首次出現順序,可選擇區分大小寫與忽略行首尾空白。文字僅在瀏覽器本機處理。",
};

export default function Page() {
  return (
    <main>
      <h1>文字去重複</h1>
      <p className="lead">貼上多行文字,自動移除重複的行並保留首次出現的順序。文字不會上傳,全部在你的瀏覽器中處理。</p>
      <section aria-label="文字去重複工具">
        <RemoveDuplicateLinesTool />
      </section>
    </main>
  );
}
