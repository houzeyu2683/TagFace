import skimage.metrics
import moviepy
import PIL.Image
import numpy
import multiprocessing
import torch
import os
import skimage
import json
import numpy
import face_alignment
import torchvision.ops
import itertools
import pandas
import re
import subprocess
import tqdm

def getRegion(box: list, size: tuple) -> tuple:
    box = numpy.stack(box)
    origin = (
        min(box[:,0]), # 最左邊 x 座標
        min(box[:,1]), # 最上邊 y 座標
        max(box[:,2]), # 最右邊 x 座標
        max(box[:,3]) # 最下邊 y 座標
    )
    delta = [
        (origin[2] - origin[0]) * 0.1, # 寬度增量
        (origin[3] - origin[1]) * 0.1 # 高度增量
    ]
    width, height = size
    region = (
        max(origin[0]-delta[0], 0),
        max(origin[1]-delta[1], 0),
        min(origin[2]+delta[0], width),
        min(origin[3]+delta[1], height)
    )
    region = tuple(map(int, region))    
    return(region)

def getContinuity(sequence: list, shot: tuple) -> bool:
    score = torchvision.ops.box_iou(
        torch.tensor(sequence[-1][2])[None],
        torch.tensor(shot[2])[None]
    )
    score = score.item()
    threshold = 0.6
    if(score<threshold): return(False)
    score = skimage.metrics.structural_similarity(
        numpy.array(sequence[-1][1]).mean(axis=2),
        numpy.array(shot[1]).mean(axis=2),
        data_range=255.0
    )
    score = round(numpy.array(score).item(), 3)
    threshold = 0.8
    if(score<threshold): return(False)
    return(True)

class State:

    def __init__(self, total: int, trajectory: dict, episode: dict) -> None:
        self.total = total
        self.trajectory = trajectory
        self.episode = episode
        return
    
    def addTrajectory(self, detection: list) -> bool:
        count = self.total
        for index, frame, box, score, landmark, likelihood in detection:
            item = (index, frame, box, score, landmark, likelihood)
            element = {count: [item]}
            self.trajectory.update(element)
            count += 1
            continue
        self.total = count
        return(True)

    def dumpTrajectory(self, key: list) -> bool:
        for index in key:
            element = {index: self.trajectory.pop(index)}
            self.episode.update(element)
            continue
        _ = key
        return(True)

    def updateTrajectory(self, detection: list) -> bool:
        memory = []
        for key, sequence in self.trajectory.items():
            batch = []
            for digit, shot in enumerate(detection, 0):
                continuity = getContinuity(sequence, shot)
                item = (key, digit, continuity)
                batch += [item]
                continue
            memory += batch
            continue
        memory = pandas.DataFrame(
            memory,
            columns=['key', 'digit', 'continuity']
        )
        if(True):
            key = list(map(int, memory['key'].unique()))
            digit = list(map(int, memory['digit'].unique()))
            pass
        positive = memory[memory['continuity']==True]
        selection = positive.duplicated(subset=['key', 'digit'], keep=False)
        summary = positive[selection==False].reset_index(drop=True)
        if(summary.empty):
            self.dumpTrajectory(key)
            self.addTrajectory([detection[index] for index in digit])
            return(True)
        for _, item in summary.iterrows():
            self.trajectory[item['key']] += [detection[item['digit']]]
            key.remove(item['key'])
            digit.remove(item['digit'])
            continue
        self.dumpTrajectory(key)
        self.addTrajectory([detection[index] for index in digit])
        return(True)

    def getEpisode(self) -> dict:
        episode = self.episode
        return(episode)

    pass

class Action:

    def __init__(self, folder: str) -> None:
        self.folder = folder
        return

    def readVideo(self, path: str) -> bool:
        video = moviepy.VideoFileClip(path)
        assert (video.fps == 25) and (video.duration >= 1)
        interval = (0, int(video.duration))
        video = video.subclipped(*interval)
        assert isinstance(video, moviepy.VideoFileClip)
        self.video = video
        return(True)

    def getLength(self) -> int:
        length = self.video.duration
        return(length)

    def getSize(self) -> tuple:
        size = self.video.size
        return(size)

    def getRate(self) -> int:
        rate = self.video.fps
        return(rate)

    def loadModel(self) -> bool:
        existence = hasattr(self, 'model')
        if(existence):
            return(True)
        model = face_alignment.FaceAlignment(
            face_alignment.LandmarksType.TWO_D, 
            device='cuda'
        )
        self.model = model
        return(True)

    def makeDetection(self, index: int, frame: numpy.ndarray) -> bool:
        # 在單一影格中進行人臉偵測
        response = self.model.get_landmarks(
            frame, 
            return_bboxes=True, 
            return_landmark_score=True
        )
        detection = []
        if(None in response):
            self.detection = detection
            return(True)
        for landmark, likelihood, prediction in zip(*response):
            # 檢查特徵點的置信度，過濾低品質的偵測結果
            # count = numpy.array(sum(likelihood<0.7)).item() # 低於闾值的特徵點數量
            # if(count>0): continue  # 如果有低品質特徵點則跳過
            # 提取邊界框座標和置信度
            box = numpy.array(prediction[:-1]).astype(int).tolist()
            score = round(numpy.array(prediction[-1]).item(), 3)
            # probability = round(float(prediction[-1]), 3)
            # if(probability<0.8): continue  # 置信度低於 0.8 則跳過
            # 建立 Shot 物件並加入偵測結果
            # shot = Shot(frame, box, landmark)
            detection += [(index, frame, box, score, landmark, likelihood)]
            continue
        # print(len(detection))
        self.detection = detection
        return(True)

    def analyzeState(self, step: int) -> bool:
        rate = self.getRate()
        length = self.getLength()
        unit = 1/rate
        total = int(length*rate)
        state = State(total=0, trajectory={}, episode={})
        # step = 10
        progress = tqdm.tqdm(
            enumerate(self.video.iter_frames(), start=0),
            total=total
        )
        for index, frame in progress:
            # print(f'[{second:.3f}, {second+unit:.3f})', end='r')
            second = index / rate  # 當前時間點
            progress.set_description_str(
                f'Analyze [{second:.3f}, {second+unit:.3f}) timestep'
            )
            if(index!=0 and index%step!=0): continue
            assert numpy.sum(self.video.get_frame(second)!=frame)==0
            self.makeDetection(index, frame)
            if(state.trajectory=={} and self.detection==[]): 
                continue
            if(state.trajectory=={} and self.detection!=[]):
                state.addTrajectory(self.detection)
                # print(state.trajectory)
                continue
            if(state.trajectory!={} and self.detection==[]):
                key = list(state.trajectory.keys())
                state.dumpTrajectory(key)
                continue
            state.updateTrajectory(self.detection)
            continue
        key = list(state.trajectory.keys())
        state.dumpTrajectory(key)
        self.state = state
        return(True)

    def makeSegment(self) -> bool:
        episode = self.state.getEpisode()
        size = self.getSize()
        rate = self.getRate()
        segment = {}
        for index in episode:
            trajectory = episode[index]
            if(len(trajectory)==1): continue
            timestep = list(map(lambda item: item[0] / rate, trajectory))
            interval = (timestep[0], timestep[-1])
            if((interval[-1] - interval[0])<1): continue
            box = list(map(lambda item: item[2], trajectory))
            delta = numpy.mean(numpy.stack(box).std(axis=0))
            if(numpy.array(delta).tolist()<1): continue
            region = getRegion(box, size)
            segment[index] = (interval, region)
            continue
        self.segment = segment
        return(True)

    def saveSegment(self) -> bool:
        # checkpoint = re.sub(r"\.[^.]*$", "", self.path)
        name = os.path.splitext(os.path.basename(self.video.filename))[0]
        checkpoint = os.path.join(self.folder, name)
        os.makedirs(checkpoint, exist_ok=True)
        # path = os.path.join(folder, 'result.json')
        with open(os.path.join(checkpoint, 'segment.json'), 'w') as paper:
            json.dump(self.segment, paper)
            pass
        _ = paper
        os.makedirs(os.path.join(checkpoint, 'segment'), exist_ok=True)
        segment = self.segment
        for index, (interval, region) in segment.items():
            path = os.path.join(checkpoint, 'segment', f'{index}.mp4')
            # segment = self.video.subclipped(*interval)
            # assert isinstance(segment, moviepy.VideoFileClip)
            # segment = segment.cropped(*region)
            # segment.write_videofile(
            #     path, codec="libx264", audio_codec="aac", logger=None
            # )
            width = region[2]-region[0]
            height = region[3]-region[1]
            box = f"crop={width}:{height}:{region[0]}:{region[1]}"
            command = [
                "ffmpeg",
                "-i", self.video.filename,
                "-ss", f'{interval[0]}',
                "-to", f'{interval[1]}',
                "-filter:v", box,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-movflags", "+faststart",
                "-y", path
            ]
            subprocess.run(command, check=True)
            continue
        _ = segment
        return(True)

    def runCommand(self, path: str) -> bool:
        self.loadModel()
        self.readVideo(path)
        self.analyzeState(step=25)
        self.makeSegment()
        self.saveSegment()
        return(True)

    pass

class Engine:

    def __init__(self, folder: str) -> None:
        self.folder = folder
        return
    
    def processBatch(self, channel: str, core: int) -> bool:
        loop = [os.path.join(channel, item) for item in os.listdir(channel)]
        action = Action(self.folder)
        with multiprocessing.Pool(processes=core) as pool:
            pool.map(action.runCommand, loop)
            pass
        _ = pool
        return(True)

    pass

engine = Engine(folder='./episode/PLvrTMNP6Iw6oo-DuBrUZiCRHzBrsFWLU3')
engine.processBatch(channel='./download/PLvrTMNP6Iw6oo-DuBrUZiCRHzBrsFWLU3/video', core=2)
