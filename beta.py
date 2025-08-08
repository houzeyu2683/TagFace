import yt_dlp
import pandas
import os
import shutil
import multiprocessing

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

    def downloadFile(self, link: str) -> bool:
        path = os.path.join(self.folder, '%(id)s.%(ext)s')
        option = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': path,
            'merge_output_format': 'mp4',
            'postprocessor_args': {
                'ffmpeg': [
                    '-r', '25', 
                    '-ar', '16000',
                    '-crf', '23'
                ]
            },
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'verbose': False,
        }
        with yt_dlp.YoutubeDL(option) as command:
            command.download(link)
            pass
        command.close()
        return(True)

    def saveCatalog(self) -> bool:
        checkpoint = os.path.join(self.folder)
        _ = shutil.rmtree(checkpoint, ignore_errors=True)
        os.makedirs(checkpoint, exist_ok=True)
        path = os.path.join(checkpoint, 'catalog.csv')
        if('table'):
            self.catalog.to_csv(path, index=False)
            pass
        loop = self.catalog['link'].tolist()
        with multiprocessing.Pool(processes=4) as pool:
            pool.map(self.downloadFile, loop)
            pass
        pool.close()
        return(True)

    pass

link = 'https://www.youtube.com/playlist?list=PL9mUJWHev0KmqJCmdyWNfihoRY6zHTcAn'
folder = './checkpoint'
video = Video(link, folder)
video.searchCatalog(query=None)
video.saveCatalog()
