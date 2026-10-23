import Link from "next/link";
import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <p>ToolBox 文字工具箱:免費、無需登入,文字僅在你的瀏覽器本機處理。</p>
        <p>
          <Link href="/privacy">隱私政策</Link> · <Link href="/about">關於本站</Link>
        </p>
      </div>
    </footer>
  );
}
