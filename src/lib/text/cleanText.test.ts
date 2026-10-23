import { describe, expect, it } from "vitest";
import { cleanText } from "./cleanText";

const none = { trimLines: false, removeBlankLines: false, collapseSpaces: false };

describe("cleanText", () => {
  it("全部關閉時內容不變(僅換行正規化)", () => {
    expect(cleanText("  a  b \r\n\r\n c", none).output).toBe("  a  b \n\n c");
  });

  it("移除行首尾空白,含 tab 與全形空白", () => {
    const r = cleanText("  a  \n\t b\t\n　中文　", { ...none, trimLines: true });
    expect(r.output).toBe("a\nb\n中文");
  });

  it("trim 不動行內空白", () => {
    expect(cleanText(" a  b ", { ...none, trimLines: true }).output).toBe("a  b");
  });

  it("移除空白行,含只有空白/全形空白的行", () => {
    const r = cleanText("a\n\n \n　\nb\n\t\nc", { ...none, removeBlankLines: true });
    expect(r.output).toBe("a\nb\nc");
    expect([r.originalCount, r.resultCount]).toEqual([7, 3]);
  });

  it("移除空白行時不 trim 保留有效行的縮排", () => {
    expect(cleanText("  a\n\n  b", { ...none, removeBlankLines: true }).output).toBe("  a\n  b");
  });

  it("合併連續空格與 tab 為單一空格", () => {
    expect(cleanText("a   b\t\tc \t d", { ...none, collapseSpaces: true }).output).toBe("a b c d");
  });

  it("合併空格不破壞行首縮排", () => {
    expect(cleanText("    a    b\n\t\tc  d", { ...none, collapseSpaces: true }).output).toBe("    a b\n\t\tc d");
  });

  it("合併空格不動全形空白與換行", () => {
    expect(cleanText("a　　b\n\nc", { ...none, collapseSpaces: true }).output).toBe("a　　b\n\nc");
  });

  it("單一空格不變,行尾多個空白合併為一個", () => {
    expect(cleanText("a b  ", { ...none, collapseSpaces: true }).output).toBe("a b ");
  });

  it("三個選項同時啟用", () => {
    const r = cleanText("  hello   world  \r\n\r\n   \r\n\t你好   世界\t\r\n", {});
    expect(r.output).toBe("hello world\n你好 世界");
  });

  it("中文與標點不被誤刪", () => {
    expect(cleanText("你好,  世界!\n123  456。", {}).output).toBe("你好, 世界!\n123 456。");
  });

  it("空輸入", () => {
    expect(cleanText("")).toEqual({ output: "", originalCount: 0, resultCount: 0 });
  });

  it("全空白行輸入且啟用全部選項,結果為空", () => {
    const r = cleanText("   \n　\n\t\n");
    expect(r.output).toBe("");
    expect(r.originalCount).toBe(3);
    expect(r.resultCount).toBe(0);
  });

  it("結尾單一換行不多算一行", () => {
    const r = cleanText("a\nb\n", none);
    expect(r.originalCount).toBe(2);
    expect(r.output).toBe("a\nb");
  });
});
