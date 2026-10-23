import styles from "./Stat.module.css";

export default function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className={styles.stat}>
      <dt className={styles.label}>{label}</dt>
      <dd className={styles.value}>{value}</dd>
    </div>
  );
}
