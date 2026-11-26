# 審核紀錄《終點線》(pain_before_success)

## 用戶需求（2026-11-26）
- 主題：成功之前的痛苦
- 片長 32 秒｜16:9｜總預算 70 點
- 要配樂（沒有指定歌曲）；不要字幕
- 沒有參考片；畫風依上傳的參考影片（`03_design/reference/style_ref.mp4`）
- 用四線程開工

## 環境
- ffmpeg / ffprobe / Python3 / Pillow / numpy / opencv（補裝 opencv-python-headless）OK
- 參考片：856x480、24fps、30.04 秒、BT.709；結尾有部分檔案損毀（可解碼到約 30 秒）
- 參考片切點（scene>0.2）：4.96, 12.0, 12.75, 15.29, 17.17, 18.0, 22.54, 23.83, 26.63, 27.88 秒

## 步驟 1：故事
- v1 初稿：`01_story/story_v1.md`
