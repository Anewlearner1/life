import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "關於本站",
  description: "ToolBox 文字工具箱是免費、無需登入的繁體中文線上文字工具,所有處理都在瀏覽器本機完成。",
};

export default function Page() {
  return (
    <main>
      <h1>關於本站</h1>
      <div className="prose">
        <section aria-labelledby="what">
          <h2 id="what">ToolBox 文字工具箱</h2>
          <p>ToolBox 提供簡單好用的繁體中文線上文字工具,目前版本(v0.1)包含:</p>
          <ul>
            <li><Link href="/remove-duplicate-lines">文字去重複</Link>:移除重複行並保留首次出現順序。</li>
            <li><Link href="/text-cleaner">文字清理器</Link>:整理多餘空白與空白行。</li>
          </ul>
        </section>
        <section aria-labelledby="principles">
          <h2 id="principles">我們的原則</h2>
          <ul>
            <li>免費使用,不需登入。</li>
            <li>文字只在你的瀏覽器處理,詳見<Link href="/privacy">隱私政策</Link>。</li>
            <li>介面簡潔,電腦與手機都好操作。</li>
          </ul>
        </section>
      </div>
    </main>
  );
}
