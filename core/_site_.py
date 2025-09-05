import yt_dlp
import pandas
import os
import multiprocessing
import subprocess
import glob
import foundation

class Site:

    def __init__(self, storage: str) -> None:
        self.storage = storage
        return

    def searchPlaylist(self, link: str) -> bool:
        option = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(option) as session:
            response = session.extract_info(link, download=False)
            information = response['entries']
            title = [item['title'] for item in information]
            name = [item['id'] for item in information]
            source = [item['url'] for item in information]
            pass
        table = pandas.DataFrame({
            "name": name, 
            'title': title, 
            'source': source
        })
        playlist = table.dropna().reset_index(drop=True)
        self.playlist = playlist
        return(True)

    def getArchive(self) -> list:
        archive = self.playlist['source'].tolist()
        return(archive)

    def savePlaylist(self) -> bool:
        path = foundation.getPath(
            [self.storage, 'video', 'playlist.csv'], create=True
        )
        self.playlist.to_csv(path, index=False)
        return(True)
    
    def saveVideo(self, source: str) -> bool:
        if('watch' in source):
            name = source.split("?v=").pop().split("&")[0]
            pass
        elif('shorts' in source):
            name = os.path.basename(source)
            pass
        pattern = foundation.getPath(
            [self.storage, 'video', name], create=True
        )
        option = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': f"{pattern}.%(ext)s",
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'verbose': False,
            'noprogress': True,
            'postprocessor_args': ['-nostats', '-loglevel', '0'],
            
        }
        command = yt_dlp.YoutubeDL(option)
        try:
            command.download(source)
            pass
        except:
            command.close()
            return(True)
        command.close()
        return(True)

    def downloadVideo(self, source: str) -> bool:
        self.saveVideo(source)
        return(True)

    pass
    