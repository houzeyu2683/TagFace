import os
import glob
import subprocess

def convert_mkv_to_mp4(input_dir, overwrite=False):
    """
    將資料夾內所有 .mkv 轉換成 .mp4 (H.264 + AAC)
    
    Args:
        input_dir (str): 要搜尋的資料夾路徑
        overwrite (bool): 是否覆蓋已存在的 mp4 檔案
    """
    mkv_files = glob.glob(os.path.join(input_dir, "**", "*.mkv"), recursive=True)

    if not mkv_files:
        print("❌ 沒有找到任何 .mkv 檔案")
        return

    print(f"🔍 找到 {len(mkv_files)} 個 MKV 檔，開始轉換...")

    for mkv in mkv_files:
        mp4 = os.path.splitext(mkv)[0] + ".mp4"

        if os.path.exists(mp4) and not overwrite:
            print(f"⚠️ 已存在，略過: {mp4}")
            continue

        command = [
            "ffmpeg",
            "-i", mkv,
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-y", mp4
        ]

        print(f"🎬 轉換中: {mkv} → {mp4}")
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("✅ 全部轉換完成！")

# 使用範例
if __name__ == "__main__":
    convert_mkv_to_mp4("download/PL9mUJWHev0Kkzf4n0sL79Azle8X_r-ZB4/#face", overwrite=False)
    convert_mkv_to_mp4("download/PL9mUJWHev0Klo61lR1HwHxSvngSnhKAQg/#face", overwrite=False)
    convert_mkv_to_mp4("download/PLkP0kGDs5Otdm84ZBZcDTAlit6bYMoyTV/#face", overwrite=False)
    convert_mkv_to_mp4("download/PLp7hnLHxd1KFmDKEV3AMpCrNW21Nz9AVT/#face", overwrite=False)
    convert_mkv_to_mp4("download/PLp7hnLHxd1KHpyw5U3kCEVpUiST-01rtO/#face", overwrite=False)
    convert_mkv_to_mp4("download/PLXMYSc0NrSxo9OOw28wpiigFjpZgQgGVF/#face", overwrite=False)
    # convert_mkv_to_mp4("download//#face", overwrite=False)
    # convert_mkv_to_mp4("download//#face", overwrite=False)
