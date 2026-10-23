import { joinLines, splitLines } from "./splitLines";

export interface RemoveDuplicateOptions {
  /** 是否區分大小寫(預設 true) */
  caseSensitive: boolean;
  /** 比較時忽略行首尾空白(含全形空白);輸出保留首次出現那一行的原文 */
  ignoreEdgeWhitespace: boolean;
}

export const defaultRemoveDuplicateOptions: RemoveDuplicateOptions = {
  caseSensitive: true,
  ignoreEdgeWhitespace: false,
};

export interface RemoveDuplicateResult {
  output: string;
  originalCount: number;
  resultCount: number;
  removedCount: number;
}

/**
 * 移除重複行,保留首次出現的順序。
 * 空白行視為一般的行:重複的空白行只保留第一個。
 */
export function removeDuplicateLines(
  text: string,
  options: Partial<RemoveDuplicateOptions> = {},
): RemoveDuplicateResult {
  const { caseSensitive, ignoreEdgeWhitespace } = {
    ...defaultRemoveDuplicateOptions,
    ...options,
  };
  const lines = splitLines(text);
  const seen = new Set<string>();
  const kept: string[] = [];

  for (const line of lines) {
    let key = ignoreEdgeWhitespace ? line.trim() : line;
    if (!caseSensitive) key = key.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    kept.push(line);
  }

  return {
    output: joinLines(kept),
    originalCount: lines.length,
    resultCount: kept.length,
    removedCount: lines.length - kept.length,
  };
}
