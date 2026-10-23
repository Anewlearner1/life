/**
 * 將文字切成行。規則(所有文字工具共用):
 * 1. CRLF、單獨的 CR 一律視為換行,統一成 LF。
 * 2. 空字串視為 0 行。
 * 3. 輸入結尾「單一」換行視為終止符號,不會多算一個空白行;
 *    結尾若有多個換行,多出的部分才算空白行("a\n\n" => ["a", ""])。
 */
export function splitLines(text: string): string[] {
  const normalized = text.replace(/\r\n?/g, "\n");
  if (normalized === "") return [];
  const body = normalized.endsWith("\n") ? normalized.slice(0, -1) : normalized;
  return body.split("\n");
}

/** 以 LF 接回各行;輸出不含結尾換行,行為固定一致。 */
export function joinLines(lines: string[]): string {
  return lines.join("\n");
}
