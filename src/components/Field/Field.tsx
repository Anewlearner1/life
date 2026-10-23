import { useId } from "react";
import styles from "./Field.module.css";

interface FieldProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  ref?: React.Ref<HTMLTextAreaElement>;
}

/** 附標籤的多行文字框。 */
export default function Field({ label, ref, className, ...rest }: FieldProps) {
  const id = useId();
  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>{label}</label>
      <textarea id={id} ref={ref} className={`${styles.textarea} ${className ?? ""}`} spellCheck={false} {...rest} />
    </div>
  );
}
