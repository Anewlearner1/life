import type { Metadata } from "next";
import Link from "next/link";
import styles from "./home.module.css";

export const metadata: Metadata = {
  title: { absolute: "ToolBox 文字工具箱:免費線上文字去重複與清理" },
  description: "免費、無需登入的繁體中文文字工具:文字去重複、文字清理器。所有處理都在你的瀏覽器本機完成。",
};

const tools = [
  { href: "/remove-duplicate-lines", title: "文字去重複", desc: "移除重複的行,保留首次出現順序,可選擇是否區分大小寫、忽略首尾空白。" },
  { href: "/text-cleaner", title: "文字清理器", desc: "移除行首尾空白、空白行,並合併連續空格,結果即時顯示。" },
];

export default function Home() {
  return (
    <main>
      <section>
        <h1>ToolBox 文字工具箱</h1>
        <p className="lead">免費、無需登入的繁體中文線上文字工具。你輸入的文字只會在自己的瀏覽器中處理,不會傳送到伺服器。</p>
      </section>
      <section aria-labelledby="tools-heading">
        <h2 id="tools-heading">選擇工具</h2>
        <ul className={styles.grid}>
          {tools.map((t) => (
            <li key={t.href}>
              <Link href={t.href} className={styles.card}>
                <span className={styles.title}>{t.title}</span>
                <span className={styles.desc}>{t.desc}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
      <section aria-labelledby="why-heading">
        <h2 id="why-heading">為什麼使用本站</h2>
        <ul className="prose">
          <li>文字僅在本機瀏覽器處理,不上傳、不儲存。</li>
          <li>免費使用,不需註冊或登入。</li>
          <li>支援電腦與手機。</li>
        </ul>
      </section>
    </main>
  );
}
