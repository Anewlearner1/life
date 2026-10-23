import { describe, expect, it } from "vitest";
import { removeDuplicateLines } from "./removeDuplicateLines";

describe("removeDuplicateLines", () => {
  it("保留首次出現順序並統計", () => {
    const r = removeDuplicateLines("b\na\nb\nc\na");
    expect(r.output).toBe("b\na\nc");
    expect([r.originalCount, r.resultCount, r.removedCount]).toEqual([5, 3, 2]);
  });

  it("預設區分大小寫", () => {
    expect(removeDuplicateLines("Apple\napple").output).toBe("Apple\napple");
  });

  it("不區分大小寫時保留首次原文", () => {
    expect(removeDuplicateLines("Apple\napple\nAPPLE", { caseSensitive: false }).output).toBe("Apple");
  });

  it("預設不忽略首尾空白", () => {
    expect(removeDuplicateLines("a\n a\na ").resultCount).toBe(3);
  });

  it("忽略首尾空白時保留首次出現的原文(含縮排)", () => {
    const r = removeDuplicateLines("  a\na\na  ", { ignoreEdgeWhitespace: true });
    expect(r.output).toBe("  a");
    expect(r.removedCount).toBe(2);
  });

  it("全形空白與 tab 也視為首尾空白", () => {
    const r = removeDuplicateLines("你好\n　你好　\n\t你好", { ignoreEdgeWhitespace: true });
    expect(r.output).toBe("你好");
  });

  it("中文、數字、標點", () => {
    const r = removeDuplicateLines("你好\n世界\n你好\n123\n123\n,。\n,。");
    expect(r.output).toBe("你好\n世界\n123\n,。");
  });

  it("全形與半形標點不同", () => {
    expect(removeDuplicateLines("a,b\na，b").resultCount).toBe(2);
  });

  it("CRLF 與 LF 混用視為相同", () => {
    const r = removeDuplicateLines("a\r\nb\r\na\nb\r\n");
    expect(r.output).toBe("a\nb");
    expect(r.originalCount).toBe(4);
  });

  it("空輸入為 0 行", () => {
    expect(removeDuplicateLines("")).toEqual({ output: "", originalCount: 0, resultCount: 0, removedCount: 0 });
  });

  it("結尾單一換行不多算一行", () => {
    const r = removeDuplicateLines("a\nb\n");
    expect(r.originalCount).toBe(2);
    expect(r.output).toBe("a\nb");
  });

  it("結尾多個換行,多出的算空白行", () => {
    const r = removeDuplicateLines("a\n\n\n");
    expect(r.originalCount).toBe(3);
    expect(r.output).toBe("a\n");
  });

  it("重複的空白行只保留第一個;空白行與全空白行不同", () => {
    expect(removeDuplicateLines("a\n\nb\n\n  \n  ").output).toBe("a\n\nb\n  ");
    expect(removeDuplicateLines("a\n\n  \n　", { ignoreEdgeWhitespace: true }).output).toBe("a\n");
  });

  it("只有換行的輸入視為一個空白行", () => {
    expect(removeDuplicateLines("\n").originalCount).toBe(1);
  });
});
