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
import glob
import PIL.Image
import foundation

def getContinuity(sequence: list, shot: tuple) -> bool:
    score = torchvision.ops.box_iou(
        torch.tensor(sequence[-1][2])[None],
        torch.tensor(shot[2])[None]
    ).item()
    # score = score.item()
    threshold = 0.6
    if(score<threshold):
        return(False)
    _ = threshold
    distance = face_recognition.face_distance([sequence[-1][1]], shot[1])[0]
    threshold = 0.5
    if(distance>threshold):
        return(False)
    _ = threshold
    return(True)

class Transition:

    def __init__(self) -> None:
        return
    
    def initiateCount(self) -> bool:
        self.count = 0
        return(True)

    def initiateState(self) -> bool:
        self.state = {}
        return(True)

    def initiateAlignment(self) -> bool:
        self.alignment = {}
        return(True)

    def updateCount(self) -> bool:
        self.count += 1
        return(True)

    def updateState(self, element: tuple) -> bool:
        # existence = self.state.get(key, False)
        # if(not existence):
        self.state.update({self.count: [element]})
            # self.count += 1
            # return(True)
        # self.state[key] += [element]
        return(True)
    
    def updateAlignment(self, key: int) -> bool:
        sequence = self.state.pop(key)
        self.alignment.update({key: sequence})
        return(True)

    pass

class Knife:

    def __init__(self, storage: str) -> None:
        self.storage = storage
        return

    def loadModel(self) -> bool:
        self.model = face_alignment.FaceAlignment(
            face_alignment.LandmarksType.TWO_D, 
            device='cuda'
        )
        return(True)

    def makeDetection(self, timestep: float, frame: numpy.ndarray) -> bool:
        detection = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            response = self.model.get_landmarks(
                frame, 
                return_bboxes=True, 
                return_landmark_score=True
            )
            pass
        empty = None in response
        if(empty):
            self.detection = detection
            return(True)
        width, height, _ = frame.shape
        for _, (landmark, likelihood, prediction) in enumerate(zip(*response), 0):
            assert isinstance(landmark, numpy.ndarray)
            assert isinstance(likelihood, numpy.ndarray)
            assert isinstance(prediction, numpy.ndarray)
            box = prediction[:-1].astype(int).tolist()
            box = [
                max(box[0] - int((box[2] - box[0]) * 0.1), 0),
                max(box[1] - int((box[3] - box[1]) * 0.1), 0),
                min(box[2] + int((box[2] - box[0]) * 0.1), height),
                min(box[3] + int((box[3] - box[1]) * 0.1), width)
            ]
            score = round(float(prediction[-1]), 3)
            target = face_recognition.face_encodings(
                numpy.ascontiguousarray(
                    frame[box[1]:box[3], box[0]:box[2], :]
                )
            )
            if(len(target)!=1): continue
            target = target.pop()
            inference = (timestep, target, box, score, landmark, likelihood)
            detection += [inference]
            continue
        self.detection = detection
        return(True)

    def getArchive(self, folder: str) -> list:
        iteration = []
        for path in glob.glob(folder, recursive=True):
            part = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
            # path = os.path.join(folder, name)
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

    def makeTransition(self, step: int) -> bool:
        # if(not self.quiet): print(f'Analyze Video: [{self.video.filename}] File')
        total = self.getRate(audio=False)*(self.getDuration()-1)
        index = 0
        for timestep, frame in self.video.iter_frames(with_times=True):
            progress = round(100*(index/total), 2)
            message = f'[{progress}%]: Analyze `{self.video.filename}` Video.'
            print(message)
            if(index==0):
                transition = Transition()
                transition.initiateCount()
                transition.initiateState()
                transition.initiateAlignment()
                pass
            if(index%step!=0): 
                index += 1
                if(index>=total): break
                continue
            timestep = float(timestep)
            self.makeDetection(timestep, frame)
            if(transition.state=={} and self.detection==[]):
                index += 1
                if(index>=total): break
                continue
            elif(transition.state=={} and self.detection!=[]):
                iteration = self.detection
                for element in self.detection:
                    transition.updateState(element)
                    transition.updateCount()
                    continue
                _ = iteration
                index += 1
                if(index>=total): break
                continue
            elif(transition.state!={} and self.detection==[]):
                iteration = list(transition.state.keys())
                for key in iteration:
                    transition.updateAlignment(key)
                    continue
                _ = iteration
                index += 1
                if(index>=total): break
                continue
            condition = (transition.state!={} and self.detection!=[])
            assert condition
            state = transition.state
            detection = {
                key: value for key, value in enumerate(self.detection, 0)
            }
            opportunity = []
            iteration = list(itertools.product(state, detection))
            for branch, leaf in iteration:
                continuity = getContinuity(state[branch], detection[leaf])
                if(continuity==False): continue
                opportunity += [(branch, leaf)]
                continue
            _ = iteration
            if(True):
                count = (
                    collections.Counter(value for value, _ in opportunity), 
                    collections.Counter(value for _, value in opportunity)
                )
                connection = []
                iteration = opportunity
                for branch, leaf in iteration:
                    success = count[0][branch]==1 and count[1][leaf]==1
                    if(not success): continue
                    connection += [(branch, leaf)]
                    continue
                _ = iteration
                truncation = []
                iteration = state
                for branch in iteration:
                    lock = [value for value, _ in connection]
                    if(branch in lock): continue
                    truncation += [branch]
                    continue
                _ = iteration
                expansion = []
                iteration = detection
                for leaf in iteration:
                    lock = [value for _, value in connection]
                    if(leaf in lock): continue
                    expansion += [leaf]
                    continue
                _ = iteration
                pass
            iteration = connection
            for branch, leaf in iteration:
                transition.state[branch] += [detection[leaf]]
                continue
            _ = iteration
            iteration = truncation
            for key in iteration:
                transition.updateAlignment(key)
                continue
            _ = iteration
            iteration = expansion
            for leaf in iteration:
                element = detection[leaf]
                transition.updateState(element)
                transition.updateCount()
                continue
            _ = iteration
            index += 1
            if(index>=total): break
            continue
        progress = round(100*(total/total), 2)
        message = f'[{progress}%]: Finish `{self.video.filename}` Video.'
        print(message)
        if(transition.state!={}):
            iteration = list(transition.state.keys())
            for key in iteration:
                transition.updateAlignment(key)
                continue
            _ = iteration
            pass
        self.transition = transition
        return(True)

    def makeTrajectory(self) -> bool:
        trajectory = []
        iteration = self.transition.alignment
        for index in iteration:
            sequence = self.transition.alignment[index]
            scale = 100
            head = (math.ceil(sequence[0][0]*scale) / scale) + 1
            tail = (math.floor(sequence[-1][0]*scale) / scale) - 1
            interval = (head, tail)
            if(tail-head<2): continue
            region = list(map(lambda item: item[2], sequence))
            region = numpy.stack(region)
            delta = numpy.mean(region.std(axis=0))
            if(delta<3): continue
            box = (
                min(region[:,0]), # 最左邊 x 座標
                min(region[:,1]), # 最上邊 y 座標
                max(region[:,2]), # 最右邊 x 座標
                max(region[:,3]) # 最下邊 y 座標
            )
            box = tuple(map(int, box))
            trajectory += [(interval, box, delta)]
            continue
        _ = iteration
        self.trajectory = trajectory
        return(True)

    def saveTrajectory(self) -> bool:
        name, _ = os.path.splitext(
            self.video.filename.split('/')[-1]
        )
        trajectory = pandas.DataFrame(self.trajectory)
        if(trajectory.empty==False):
            path = foundation.getPath(
                [self.storage, f'{name}.csv'], create=True
            )
            trajectory.columns = ['interval', 'region', 'delta']
            trajectory.to_csv(path, index=False)
            pass
        iteration = self.trajectory
        for index, element in enumerate(iteration):
            suffix = '.mp4'
            path = foundation.getPath(
                [self.storage, name, f'{name}_{index}{suffix}'], create=True
            )
            interval, box, _ = element
            width, height = box[2] - box[0], box[3] - box[1]
            command = [
                "ffmpeg", 
                "-i", self.video.filename,
                "-ss", str(interval[0]),      # 起始時間
                "-to", str(interval[1]),        # 結束時間
                "-vf", f"crop={width}:{height}:{box[0]}:{box[1]},fps=25",  # 裁切人臉區域
                "-c:v", "libx264", 
                "-crf", "18", 
                "-preset", "fast",
                '-c:a', 'aac', '-b:a', '192k', #"-c:a", "flac", 
                '-y', path #os.path.join(folder, f'{name}_{index}{suffix}')
            ]
            _ = subprocess.run(command, capture_output=True, text=True)
            continue
        _ = iteration
        return(True)

    def captureFace(self, folder: str, step: int) -> bool:
        self.loadModel()
        archive = self.getArchive(folder)
        total = len(archive)
        iteration = enumerate(archive, 1)
        for index, path in iteration:
            print(f"[{index}|{total}]: Current Progress.")
            self.openVideo(path)
            self.makeTransition(step)
            self.makeTrajectory()
            self.saveTrajectory()
            self.closeVideo()
            continue
        _ = iteration
        return(True)

    pass

channel = '【懂商業 看商周】'
storage = f'./download/{channel}/#face'
folder = f'download/{channel}/#fragment/**/*'
knife = Knife(storage=storage)
knife.captureFace(folder, step=5)
# knife.loadModel()
# archive = knife.getArchive(folder)
# # index = 0
# step = 5
# for path in archive:
#     # if('leGPCnVk-c4_0.mkv' not in path):
#     #     continue
#     knife.loadModel()
#     knife.openVideo(path)
#     knife.makeTransition(step=step)
#     knife.makeTrajectory()
#     knife.saveTrajectory()
#     knife.closeVideo()
#     # gc.collect()
#     continue

# operation = foundation.Operation(core=2)
# operation.activatePipeline(
#     archive, knife.captureFace, [('step', 5)]
# )