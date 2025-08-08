import shutil
import os
import yt_dlp
import datetime
import hashlib
import re
import subprocess
import multiprocessing
import pandas
import pathlib

class Cloud:

    def __init__(self, folder: str) -> None:
        self.folder = folder
        return

    def downloadVideo(self, link: str) -> bool:
        if("shorts" in link):
            name = re.search(r'[^/]+$', link).group()
            pass
        elif("watch" in link):
            name = link.split("?v=").pop().split("&")[0]
            pass
        archive = os.path.join(self.folder, f"{name}.%(ext)s")
        option = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': archive,
            'quiet': True,
            'merge_output_format': 'mkv'
        }
        checkpoint = re.sub(r'\.[^.]*$', '.mp4', archive)
        if(os.path.isfile(checkpoint)==True):
            return(True)
        with yt_dlp.YoutubeDL(option) as session:
            session.download([link])
            pass
        # session.close()
        source = re.sub(r'\.[^.]*$', '.mkv', archive)
        target = re.sub(r'\.[^.]*$', '.mp4', archive)
        command = [
            'ffmpeg',
            '-loglevel', 'error',
            '-i', source,
            '-r', '25',
            '-ar', '16000',
            '-c:v', 'libx264',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '192k',
            target
        ]
        subprocess.run(command, check=True)
        os.remove(source)
        return(True)

    def clearStream(self) -> bool:
        folder = pathlib.Path(self.folder)
        for item in folder.glob('*.mkv'):
            item.unlink()  # 等同於 os.remove()
            continue
        for item in folder.glob('*.part'):
            item.unlink()  # 等同於 os.remove()
            continue
        for item in folder.glob('*.webm'):
            item.unlink()  # 等同於 os.remove()
            continue
        _ = folder
        return(True)

    def downloadCatalog(self, site: str, core: int) -> bool:
        self.clearStream()
        checkpoint = os.path.join(self.folder, 'catalog.csv')
        if(os.path.isfile(checkpoint)==False):
            option = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': True,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(option) as session:
                response = session.extract_info(site, download=False)
                information = response['entries']
                name = [item['id'] for item in information]
                pass
            host = 'https://www.youtube.com/watch?v='
            link = [f'{host}{item}' for item in name]
            catalog = pandas.DataFrame({'link': link})
            os.makedirs(self.folder, exist_ok=True)
            catalog.to_csv(checkpoint, index=False)
            pass
        else:
            catalog = pandas.read_csv(checkpoint)
            pass
        link = catalog['link'].tolist()
        with multiprocessing.Pool(core) as pool:
            pool.map(self.downloadVideo, link)
            pass
        folder = pathlib.Path(self.folder)
        for item in folder.glob('*.mkv'):
            item.unlink()  # 等同於 os.remove()
            continue
        self.clearStream()
        return(True)

    pass

folder = './download'
channel = "https://www.youtube.com/playlist?list=PL9mUJWHev0KmqJCmdyWNfihoRY6zHTcAn"
cloud = Cloud(folder)
# cloud.downloadVideo(link)
core = 4
cloud.downloadCatalog(channel, core)
