import yt_dlp
import pandas
import os
import shutil
import multiprocessing
import pathlib
import subprocess
import re

class Video:

    def __init__(self, link: str, folder: str) -> None:
        self.link = link
        self.folder = folder
        return

    def searchCatalog(self, query: None|str) -> bool:
        option = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(option) as session:
            response = session.extract_info(self.link, download=False)
            information = response['entries']
            title = [item['title'] for item in information]
            name = [item['id'] for item in information]
            duration = [item['duration'] for item in information]
            pass
        host = 'https://www.youtube.com/watch?v='
        link = [f'{host}{item}' for item in name]
        table = pandas.DataFrame({
            "name": name, 
            'title': title, 
            'duration': duration, 
            'link': link
        })
        table = table.dropna().reset_index(drop=True)
        if(query!=None): 
            table = table.query(query, engine='python')
            table = table.reset_index(drop=True)
            pass
        self.catalog = table
        return(True)

    def dumpSource(self, link: str) -> bool:
        name = link.split("?v=").pop().split("&")[0]
        if(True):
            checkpoint = os.path.join(self.folder, 'video')
            os.makedirs(checkpoint, exist_ok=True)
            target = os.path.join(checkpoint, f"{name}.mp4")
            if(os.path.isfile(target)==True): return(True)
            pass
        pattern = os.path.join(self.folder, name)
        option = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': f"{pattern}.%(ext)s",
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'verbose': False,
        }
        command = yt_dlp.YoutubeDL(option)
        try:
            command.download(link)
            pass
        except:
            command.close()
            return(True)
        command.close()
        if(os.path.isfile(f"{pattern}.mkv")==True):
            path = f"{pattern}.mkv"
            pass
        elif(os.path.isfile(f"{pattern}.mp4")==True):
            path = f"{pattern}.mp4"
            pass
        else:
            return(True)
        command = [
            "ffmpeg",
            "-i", path,  # 輸入檔案
            "-r", "25",        # 設定 FPS
            "-ar", "16000",    # 設定音頻取樣率
            "-crf", "23",      # 設定視訊品質
            target
        ]
        try:
            subprocess.run(command, check=True)
            pass
        except:
            _ = command
            return(True)
        _ = command
        _ = os.remove(path)
        return(True)

    def saveCatalog(self) -> bool:
        os.makedirs(self.folder, exist_ok=True)
        path = os.path.join(self.folder, 'catalog.csv')
        if('table'):
            self.catalog.to_csv(path, index=False)
            pass
        loop = self.catalog['link'].tolist()
        with multiprocessing.Pool(processes=4) as pool:
            pool.map(self.dumpSource, loop)
            pass
        pool.close()
        return(True)

    pass

link = 'https://www.youtube.com/playlist?list=PL9mUJWHev0Klo61lR1HwHxSvngSnhKAQg'
folder = './download/PL9mUJWHev0Klo61lR1HwHxSvngSnhKAQg'
video = Video(link, folder)
video.searchCatalog(query=None)
video.saveCatalog()

