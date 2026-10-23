import Link from "next/link";
import styles from "./Header.module.css";

const links = [
  { href: "/remove-duplicate-lines", label: "文字去重複" },
  { href: "/text-cleaner", label: "文字清理器" },
  { href: "/privacy", label: "隱私政策" },
  { href: "/about", label: "關於本站" },
];

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link href="/" className={styles.brand}>ToolBox 文字工具箱</Link>
        <nav aria-label="主選單">
          <ul className={styles.nav}>
            {links.map((l) => (
              <li key={l.href}><Link href={l.href} className={styles.link}>{l.label}</Link></li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}
