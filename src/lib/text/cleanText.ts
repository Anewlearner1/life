import { joinLines, splitLines } from "./splitLines";

export interface CleanTextOptions {
  /** 移除每行行首與行尾的空白(含全形空白) */
  trimLines: boolean;
  /** 移除空白行(整行只有空白,含全形空白,也視為空白行) */
  removeBlankLines: boolean;
  /** 將行內連續的半形空格/tab 合併為單一半形空格 */
  collapseSpaces: boolean;
}

export const defaultCleanTextOptions: CleanTextOptions = {
  trimLines: true,
  removeBlankLines: true,
  collapseSpaces: true,
};

export interface CleanTextResult {
  output: string;
  originalCount: number;
  resultCount: number;
}

/**
 * 合併連續空白:只處理半形空格與 tab,不碰全形空白與換行。
 * 行首縮排(第一個非空白字元之前)原樣保留;
 * 只合併行內其後的連續空白。整行皆為空白的行也視為縮排,不改動。
 */
export function collapseInlineSpaces(line: string): string {
  const indent = /^[ \t]*/.exec(line)![0];
  const rest = line.slice(indent.length);
  return indent + rest.replace(/[ \t]{2,}/g, " ");
}

/**
 * 依選項清理文字。處理順序:合併空格 → 去除行首尾空白 → 移除空白行。
 * 輸出以 LF 連接,不含結尾換行。
 */
export function cleanText(
  text: string,
  options: Partial<CleanTextOptions> = {},
): CleanTextResult {
  const { trimLines, removeBlankLines, collapseSpaces } = {
    ...defaultCleanTextOptions,
    ...options,
  };
  const original = splitLines(text);
  let lines = original;

  if (collapseSpaces) lines = lines.map(collapseInlineSpaces);
  if (trimLines) lines = lines.map((l) => l.trim());
  if (removeBlankLines) lines = lines.filter((l) => l.trim() !== "");

  return {
    output: joinLines(lines),
    originalCount: original.length,
    resultCount: lines.length,
  };
}
