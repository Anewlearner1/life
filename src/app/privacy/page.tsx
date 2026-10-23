import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "隱私政策",
  description: "ToolBox 文字工具箱的隱私政策:你輸入的文字僅在瀏覽器本機處理,不會上傳或儲存。",
};

export default function Page() {
  return (
    <main>
      <h1>隱私政策</h1>
      <div className="prose">
        <section aria-labelledby="local">
          <h2 id="local">文字僅在本機處理</h2>
          <p>本站所有工具(文字去重複、文字清理器)的運算都在你的瀏覽器中執行。你輸入、貼上的文字不會傳送到本站或任何第三方伺服器。</p>
        </section>
        <section aria-labelledby="no-store">
          <h2 id="no-store">不儲存、不追蹤</h2>
          <ul>
            <li>不需要註冊或登入,也沒有資料庫。</li>
            <li>不會儲存你的輸入內容;重新整理或關閉頁面後內容即消失。</li>
            <li>本站目前未使用分析追蹤或廣告。</li>
          </ul>
        </section>
        <section aria-labelledby="clipboard">
          <h2 id="clipboard">剪貼簿</h2>
          <p>只有在你按下「複製結果」時,才會將處理後的結果寫入你裝置的剪貼簿。</p>
        </section>
        <section aria-labelledby="changes">
          <h2 id="changes">政策變更</h2>
          <p>若日後功能有所調整,本頁會同步更新說明。</p>
        </section>
      </div>
    </main>
  );
}
