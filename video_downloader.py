#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

def download_and_convert_video(url, output_dir="downloads"):
    """
    Download video using yt-dlp and convert to 25 fps with 16000Hz audio
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get video info first to extract title for filename
    info_cmd = [
        "yt-dlp",
        "--get-filename",
        "-o", "%(title)s.%(ext)s",
        url
    ]
    
    try:
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        original_filename = result.stdout.strip()
        base_name = Path(original_filename).stem
        temp_filename = f"{base_name}_temp.%(ext)s"
        final_filename = f"{base_name}_25fps_16khz.mp4"
        
        print(f"Downloading: {original_filename}")
        
        # Download video with yt-dlp
        download_cmd = [
            "yt-dlp",
            "-o", str(output_path / temp_filename),
            "--format", "best[height<=1080]",
            url
        ]
        
        subprocess.run(download_cmd, check=True)
        
        # Find the downloaded file
        temp_files = list(output_path.glob(f"{base_name}_temp.*"))
        if not temp_files:
            raise FileNotFoundError("Downloaded file not found")
        
        temp_file = temp_files[0]
        final_path = output_path / final_filename
        
        print(f"Converting to 25fps and 16kHz audio...")
        
        # Convert with ffmpeg
        convert_cmd = [
            "ffmpeg",
            "-i", str(temp_file),
            "-r", "25",  # Set frame rate to 25 fps
            "-ar", "16000",  # Set audio sample rate to 16kHz
            "-c:v", "libx264",  # Video codec
            "-c:a", "aac",  # Audio codec
            "-y",  # Overwrite output file
            str(final_path)
        ]
        
        subprocess.run(convert_cmd, check=True)
        
        # Remove temporary file
        temp_file.unlink()
        
        print(f"Video saved as: {final_path}")
        return str(final_path)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Download and convert video with yt-dlp")
    parser.add_argument("url", help="Video URL to download")
    parser.add_argument("-o", "--output", default="downloads", help="Output directory (default: downloads)")
    
    args = parser.parse_args()
    
    # Check if required tools are available
    tools = ["yt-dlp", "ffmpeg"]
    missing_tools = []
    
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"Error: Missing required tools: {', '.join(missing_tools)}")
        print("Please install them:")
        for tool in missing_tools:
            if tool == "yt-dlp":
                print(f"  pip install {tool}")
            else:
                print(f"  sudo apt install {tool}")  # Linux
        sys.exit(1)
    
    result = download_and_convert_video(args.url, args.output)
    if result:
        print(f"Success! Video available at: {result}")
    else:
        print("Failed to download and convert video")
        sys.exit(1)

if __name__ == "__main__":
    main()