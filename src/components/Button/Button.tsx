import styles from "./Button.module.css";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export default function Button({ variant = "secondary", className, type = "button", ...rest }: ButtonProps) {
  const cls = [styles.button, variant === "primary" ? styles.primary : "", className ?? ""].filter(Boolean).join(" ");
  return <button type={type} className={cls} {...rest} />;
}
