import os
import insightface
import moviepy
import math
import face_alignment
import numpy
import warnings
import itertools
import torchvision
import torch
import face_recognition
import collections
import subprocess
import tqdm
import math
import pandas
import foundation

class Element:

    def __init__(self) -> None:
        return

    def initiateSequence(self) -> bool:
        self.sequence = []
        return(True)

    def insertValue(self, value: float) -> bool:
        self.sequence += [value]
        return(True)

    def getInterval(self) -> list:
        empty = self.sequence==[]
        if(empty):
            interval = []
            return(interval)
        interval = [
            float(self.sequence[0]),
            float(self.sequence[-1])
        ]
        length = interval[1] - interval[0]
        if(length<2): 
            interval = []
            return(interval)
        scale = 100
        head = math.ceil(interval[0]*scale) / scale
        tail = math.floor(interval[1]*scale) / scale
        interval = [head, tail]
        return(interval)

    def clearSequence(self) -> bool:
        self.sequence = []
        return(True)

    pass

class Hatchet:

    def __init__(self, storage: str) -> None:
        self.storage = storage
        # self.quiet = quiet
        return

    def loadModel(self) -> bool:
        model = insightface.app.FaceAnalysis(name='buffalo_s')
        model.prepare(ctx_id=0, det_size=(320, 320))
        self.model = model
        return(True)

    def makeDetection(self, frame: numpy.ndarray) -> bool:
        self.detection = self.model.get(frame)
        return(True)

    def getArchive(self, folder: str) -> list:
        iteration = []
        for name in os.listdir(folder):
            part = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
            path = os.path.join(folder, name)
            suffix = os.path.splitext(path)[-1]
            if(suffix not in part): continue
            iteration += [path]
            continue
        archive = iteration
        return(archive)
    
    def openVideo(self, path: str) -> bool:
        self.video = moviepy.VideoFileClip(path)
        # video = video.subclipped(0, math.floor(video.duration))
        return(True)
    
    def getRate(self, audio: bool) -> float:
        rate = self.video.audio.fps if(audio) else self.video.fps
        return(rate)

    def getDuration(self) -> float:
        duration = self.video.duration
        return(duration)

    def closeVideo(self) -> bool:
        self.video.close()
        return(True)

    def makeFragment(self, step: int) -> bool:
        fragment = []
        # if(not self.quiet):
        #     print(f'Analyze Video: [{self.video.filename}] File')
        #     pass
        # duration = self.getDuration()
        total = self.getRate(audio=False)*(self.getDuration()-1)
        iteration = self.video.iter_frames(with_times=True)
        index = 0
        for timestep, frame in iteration:
            progress = round(100*(index/total), 2)
            message = f'[{progress}%]: {self.video.filename}'
            print(message)
            if(index==0):
                element = Element()
                element.initiateSequence()
                pass
            if(index%step!=0): 
                index += 1
                if(index>=total): break
                continue
            timestep = float(timestep)
            self.makeDetection(frame)
            if(element.sequence==[] and self.detection==[]):
                index += 1
                if(index>=total): break
                continue
            elif(element.sequence==[] and self.detection!=[]):
                element.insertValue(timestep)
                index += 1
                if(index>=total): break
                continue
            elif(element.sequence!=[] and self.detection==[]):
                interval = element.getInterval()
                element.clearSequence()
                if(interval==[]):
                    index += 1
                    if(index>=total): break
                    continue
                fragment += [interval]
                index += 1
                if(index>=total): break
                continue
            condition = (element.sequence!=[] and self.detection!=[])
            assert condition
            element.insertValue(timestep)
            index += 1
            if(index>=total): break
            continue
        _ = iteration
        interval = element.getInterval()
        if(interval!=[]):
            fragment += [interval]
            pass
        # progress = round(100*(index/total), 2)
        # if(not self.quiet): print(f'Progress: [{progress}%]')
        progress = round(100*(total/total), 2)
        message = f'[{progress}%]: {self.video.filename}'
        print(message)
        self.fragment = fragment
        return(True)

    def saveFragment(self) -> bool:
        name, _ = os.path.splitext(
            self.video.filename.split('/')[-1]
        )
        fragment = pandas.DataFrame(
            self.fragment
        )
        if(fragment.empty==False):
            path = foundation.getPath(
                [self.storage, f"{name}.csv"],
                create=True
            )
            fragment.to_csv(path, index=False)
            pass
        iteration = self.fragment
        for index, interval in enumerate(iteration):
            # os.makedirs(folder, exist_ok=True)
            suffix = '.mkv'
            path = foundation.getPath(
                [self.storage, name, f'{name}_{index}{suffix}'],
                create=True
            )
            command = [
                'ffmpeg', 
                "-ss", str(interval[0]), 
                "-to", str(interval[1]), 
                "-i", self.video.filename, 
                "-c", "copy", 
                '-nostats',           # 不顯示進度統計
                '-loglevel', '24',     # 完全靜默
                '-y', path
            ]
            _ = subprocess.run(command)
            continue
        _ = iteration
        return(True)

    def cutFragment(self, path: str, step: int) -> bool:
        self.loadModel()
        self.openVideo(path)
        self.makeFragment(step)
        self.saveFragment()
        self.closeVideo()
        return(True)

    pass

channel = 'Share-a-short-video-every-day'
storage = f'./download/{channel}/#fragment'
folder = f'./download/{channel}/video'
hatchet = Hatchet(storage)
archive = hatchet.getArchive(folder)
# for path in archive:
#     if(path != './download/Share-a-short-video-every-day/video/7h7tiCh3fRw.webm'): continue
#     hatchet.openVideo(path)
#     hatchet.loadModel()
#     hatchet.makeFragment(step=25)
#     hatchet.saveFragment()
#     hatchet.closeVideo()
#     continue

iteration = archive
operation = foundation.Operation(core=6)
operation.activatePipeline(
    archive, hatchet.cutFragment, {'step': 25}
)