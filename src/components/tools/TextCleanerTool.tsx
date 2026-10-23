"use client";

import { useMemo, useRef, useState } from "react";
import Button from "@/components/Button/Button";
import Checkbox from "@/components/Checkbox/Checkbox";
import CopyButton from "@/components/CopyButton/CopyButton";
import Field from "@/components/Field/Field";
import Stat from "@/components/Stat/Stat";
import { cleanText, defaultCleanTextOptions, type CleanTextOptions } from "@/lib/text/cleanText";
import styles from "@/components/ToolLayout/ToolLayout.module.css";

export default function TextCleanerTool() {
  const [input, setInput] = useState("");
  const [opts, setOpts] = useState<CleanTextOptions>(defaultCleanTextOptions);
  const outRef = useRef<HTMLTextAreaElement>(null);

  const result = useMemo(() => cleanText(input, opts), [input, opts]);
  const isEmpty = input.trim() === "";
  const set = (key: keyof CleanTextOptions) => (v: boolean) => setOpts((o) => ({ ...o, [key]: v }));

  return (
    <div>
      <fieldset className={styles.options}>
        <legend>選項</legend>
        <Checkbox label="移除行首尾空白" hint="含半形空格、tab 與全形空白。"
          checked={opts.trimLines} onChange={set("trimLines")} />
        <Checkbox label="移除空白行" hint="整行只有空白(含全形空白)也視為空白行。"
          checked={opts.removeBlankLines} onChange={set("removeBlankLines")} />
        <Checkbox label="合併連續空格"
          hint="只將行內連續的半形空格與 tab 合併為單一空格;不處理全形空白與換行。行首縮排會保留(若同時啟用「移除行首尾空白」則會被移除)。"
          checked={opts.collapseSpaces} onChange={set("collapseSpaces")} />
      </fieldset>

      <div className={styles.panes}>
        <Field label="輸入文字" value={input} onChange={(e) => setInput(e.target.value)}
          placeholder="在此貼上或輸入要清理的文字" />
        <Field label="清理結果" ref={outRef} readOnly value={isEmpty ? "" : result.output}
          placeholder="結果會即時顯示在這裡" />
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
        </dl>
      )}
      <p className="hint">
        說明:換行統一以 LF 處理(CRLF 亦可);輸入結尾的單一換行不算一行,輸出也不含結尾換行。處理順序:合併空格、移除行首尾空白、移除空白行。
      </p>
    </div>
  );
}
