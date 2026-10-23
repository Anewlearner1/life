"use client";

import { useEffect, useRef, useState } from "react";
import Button from "@/components/Button/Button";
import { copyText } from "@/lib/clipboard";
import styles from "./CopyButton.module.css";

interface CopyButtonProps {
  text: string;
  disabled?: boolean;
  /** 複製失敗時呼叫,可用來選取結果文字框,方便使用者手動複製 */
  onCopyFailed?: () => void;
}

type Status = "idle" | "copied" | "failed";

export default function CopyButton({ text, disabled, onCopyFailed }: CopyButtonProps) {
  const [status, setStatus] = useState<Status>("idle");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);

  async function handleClick() {
    const ok = await copyText(text);
    if (timer.current) clearTimeout(timer.current);
    if (ok) {
      setStatus("copied");
      timer.current = setTimeout(() => setStatus("idle"), 2000);
    } else {
      setStatus("failed");
      onCopyFailed?.();
    }
  }

  return (
    <span className={styles.wrap}>
      <Button variant="primary" onClick={handleClick} disabled={disabled || text === ""}>
        {status === "copied" ? "已複製" : "複製結果"}
      </Button>
      <span className={status === "failed" ? styles.error : styles.ok} role="status" aria-live="polite">
        {status === "copied" && "已複製到剪貼簿"}
        {status === "failed" && "無法自動複製。結果已選取,請按 Ctrl+C(Mac 為 ⌘+C)手動複製。"}
      </span>
    </span>
  );
}
