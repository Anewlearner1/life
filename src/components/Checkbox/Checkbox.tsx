import { useId } from "react";
import styles from "./Checkbox.module.css";

interface CheckboxProps {
  label: string;
  hint?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export default function Checkbox({ label, hint, checked, onChange }: CheckboxProps) {
  const id = useId();
  const hintId = `${id}-hint`;
  return (
    <div className={styles.option}>
      <input id={id} type="checkbox" className={styles.input} checked={checked}
        aria-describedby={hint ? hintId : undefined} onChange={(e) => onChange(e.target.checked)} />
      <div className={styles.text}>
        <label htmlFor={id} className={styles.label}>{label}</label>
        {hint && <p id={hintId} className={styles.hint}>{hint}</p>}
      </div>
    </div>
  );
}
