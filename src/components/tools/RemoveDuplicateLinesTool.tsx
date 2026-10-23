"use client";

import { useMemo, useRef, useState } from "react";
import Button from "@/components/Button/Button";
import Checkbox from "@/components/Checkbox/Checkbox";
import CopyButton from "@/components/CopyButton/CopyButton";
import Field from "@/components/Field/Field";
import Stat from "@/components/Stat/Stat";
import { removeDuplicateLines } from "@/lib/text/removeDuplicateLines";
import styles from "@/components/ToolLayout/ToolLayout.module.css";

export default function RemoveDuplicateLinesTool() {
  const [input, setInput] = useState("");
  const [caseSensitive, setCaseSensitive] = useState(true);
  const [ignoreEdgeWhitespace, setIgnoreEdgeWhitespace] = useState(false);
  const outRef = useRef<HTMLTextAreaElement>(null);

  const result = useMemo(
    () => removeDuplicateLines(input, { caseSensitive, ignoreEdgeWhitespace }),
    [input, caseSensitive, ignoreEdgeWhitespace],
  );
  const isEmpty = input.trim() === "";

  return (
    <div>
      <fieldset className={styles.options}>
        <legend>選項</legend>
        <Checkbox label="區分大小寫" hint="預設開啟。關閉後 Apple 與 apple 視為相同,保留先出現的那行。"
          checked={caseSensitive} onChange={setCaseSensitive} />
        <Checkbox label="忽略行首尾空白差異" hint="比較時忽略行首尾空白(含全形空白與 tab),輸出保留首次出現那一行的原文。"
          checked={ignoreEdgeWhitespace} onChange={setIgnoreEdgeWhitespace} />
      </fieldset>

      <div className={styles.panes}>
        <Field label="輸入文字(每行一筆)" value={input} onChange={(e) => setInput(e.target.value)}
          placeholder="在此貼上或輸入多行文字" />
        <Field label="結果" ref={outRef} readOnly value={isEmpty ? "" : result.output}
          placeholder="結果會顯示在這裡" />
      </div>

      <div className={styles.actions}>
        <CopyButton text={isEmpty ? "" : result.output} onCopyFailed={() => outRef.current?.select()} />
        <Button onClick={() => setInput("")} disabled={input === ""}>清空</Button>
      </div>

      {isEmpty ? (
        <p className={styles.empty} role="status">請輸入文字</p>
      ) : (
        <dl className={styles.stats} aria-label="統計">
          <Stat label="原始行數" value={result.originalCount} />
          <Stat label="結果行數" value={result.resultCount} />
          <Stat label="移除數量" value={result.removedCount} />
        </dl>
      )}
      <p className="hint">
        說明:換行統一以 LF 處理(CRLF 亦可);輸入結尾的單一換行不算一行,輸出也不含結尾換行。空白行視為一般的行,重複的空白行只保留第一個。
      </p>
    </div>
  );
}
