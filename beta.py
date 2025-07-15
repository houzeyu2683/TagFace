import skimage.metrics
import moviepy
import PIL.Image
import numpy
import torch
import os
import skimage
import json
import numpy
import face_alignment
import torchvision
import itertools

class Metric:

    def __init__(self, method: str) -> None:
        self.method = method
        return

    def getScore(
        self,
        prediction: numpy.ndarray, 
        truth: numpy.ndarray
    ) -> float:
        if(self.method=='IoU'):
            score = torchvision.ops.box_iou(
                torch.tensor(prediction)[None],
                torch.tensor(truth)[None]
            )
            score = score.item()
            pass
        elif(self.method=='Similarity'):
            score = skimage.metrics.structural_similarity(
                prediction,
                truth,
                data_range=255.0
            )
            score = numpy.array(score).item()
            pass
        score = round(score, 3)
        return(score)

    pass

class Shot:

    def __init__(
        self, 
        frame: numpy.ndarray,
        box: numpy.ndarray,
        landmark: numpy.ndarray
    ) -> None:
        self.frame = frame
        self.box = box
        self.landmark = landmark
        return

    def getArea(self, size: tuple, color: bool) -> numpy.ndarray:
        image = PIL.Image.fromarray(self.frame)
        image = image.crop(self.box)
        if(not color): image = image.convert("L")
        image = image.resize(size)
        area = numpy.array(image)
        return(area)

    def getSize(self) -> tuple:
        height, width, _ = self.frame.shape
        size = (height, width)
        return(size)

    pass

class Trajectory:

    def __init__(self, size: tuple, fragment: list, timestep: list) -> None:
        self.size = size
        self.fragment = fragment
        self.timestep = timestep
        return

    def getContinuity(self, shot: Shot) -> bool:
        memory = self.fragment[-1]
        assert isinstance(memory, Shot)
        score = Metric('IoU').getScore(memory.box, shot.box)
        if(score<0.8): return(False)
        size = (64, 64)
        truth = memory.getArea(size, color=False)
        prediction = shot.getArea(size, color=False)
        score = Metric('Similarity').getScore(prediction, truth)
        if(score<0.8): return(False)
        return(True)

    def increaseFragment(self, shot: Shot) -> bool:
        self.fragment = self.fragment + [shot]
        return(True)

    def increaseTimestep(self, second: float) -> bool:
        self.timestep = self.timestep + [second]
        return(True)

    def getRegion(self) -> numpy.ndarray:
        # 統一所有box的
        # size = None
        box = []
        for shot in self.fragment:
            assert isinstance(shot, Shot)
            # size += [shot.getSize()]
            # if(size==None): size = shot.getSize()
            box += [shot.box]
            continue
        # height, width = size
        box = numpy.stack(box)
        origin = (
            box[:,0].min(), # left width
            box[:,1].min(), # left height
            box[:,2].max(), # right width
            box[:,3].max() # right height
        )
        delta = [
            (origin[2] - origin[0]) * 0.1, # width delta
            (origin[3] - origin[1]) * 0.1 # height delta
        ]
        height, width = self.size
        region = (
            max(origin[0]-delta[0], 0),
            max(origin[1]-delta[1], 0),
            min(origin[2]+delta[0], width),
            min(origin[3]+delta[1], height)
        )        
        return(region)

    pass

class Agent:

    def __init__(self, path: str) -> None:
        self.path = path
        return
    
    def readVideo(self) -> bool:
        video = moviepy.VideoFileClip(self.path)
        assert (video.fps == 25) and (video.duration >= 1)
        self.video = video
        return(True)

    def captureSequence(self) -> bool:
        delta = 1 / self.video.fps
        sequence = {}
        for index, frame in enumerate(agent.video.iter_frames(), start=0):
            second = index / self.video.fps
            print(f'<Message>: Analyze [{second}, {second+delta}) Interval')
            self.makeDetection(frame)
            if(self.queue!=[] and self.detection==[]): 
                # 所有的 queue 都打包成一個完整的片段
                for trajectory in self.queue:
                    item = {self.total: trajectory}
                    sequence.update(item)
                    self.total += 1
                    continue
                _, _ = index, frame
                self.queue==[]
                continue
            if(self.queue!=[] and self.detection!=[]):
                # 查詢可以合併的 trajectory 跟 shot
                rule = []
                grid = list(
                    itertools.product(
                        range(len(self.queue)), 
                        range(len(self.detection))
                    )
                )
                for cell in grid:
                    trajectory = self.queue[cell[0]]
                    shot = self.detection[cell[1]]
                    assert isinstance(trajectory, Trajectory)
                    assert isinstance(shot, Shot)
                    continuity = trajectory.getContinuity(shot)
                    if(continuity): rule += [cell]
                    continue
                rule = numpy.array(rule)
                summary = numpy.unique(rule, axis=0)
                if(summary.size==0): summary = numpy.array([(-1, -1)])
                # 合併批配的 trajectory 跟 shot
                for cell in summary:
                    if(cell[0]==-1 and cell[1]==-1): continue
                    trajectory = self.queue[cell[0]]
                    shot = self.detection[cell[1]]
                    assert isinstance(trajectory, Trajectory)
                    assert isinstance(shot, Shot)
                    trajectory.increaseFragment(shot)
                    trajectory.increaseTimestep(second)
                    continue
                # 未批配的 trajectory 取出存起來
                acceptance = []
                for anchor, trajectory in enumerate(self.queue):
                    if(anchor in summary[:, 0]): 
                        acceptance += [trajectory]
                        continue
                    item = {self.total: trajectory}
                    sequence.update(item)
                    self.total += 1
                    continue
                self.queue = acceptance
                # 未批配的 shot 變成新的 Trajectory 並且新增至 queue
                for anchor, shot in enumerate(self.detection):
                    assert isinstance(shot, Shot)
                    if(anchor in summary[:, 1]): continue
                    trajectory = Trajectory(
                        size=shot.getSize(), 
                        fragment=[shot], 
                        timestep=[second]
                    )
                    self.queue += [trajectory]
                    continue
                _, _ = anchor, frame
                continue
            if(self.queue==[] and self.detection!=[]):
                for anchor, shot in enumerate(self.detection):
                    assert isinstance(shot, Shot)
                    trajectory = Trajectory(
                        size=shot.getSize(), 
                        fragment=[shot], 
                        timestep=[second]
                    )
                    self.queue += [trajectory]
                    continue
                _, _ = index, frame
                continue
            _, _ = anchor, frame
            continue
        self.sequence = sequence
        return(True)

    def filterSequence(self) -> bool:
        # 挑出嘴巴有在動的
        # 或是聲音與臉部批配的
        sequence = {}
        for index in self.sequence:
            trajectory = self.sequence[index]
            assert isinstance(trajectory, Trajectory)
            second = trajectory.timestep[-1] - trajectory.timestep[0]
            if(second<=1): continue
            region = trajectory.getRegion()
            width = (region[2] - region[0])
            height = (region[3] - region[1])
            if(width<128 or height<128): continue
            sequence.update({index: trajectory})
            continue
        self.sequence = sequence
        return(True)

    def saveSequence(self, checkpoint: str) -> bool:
        for index in self.sequence:
            path = os.path.join(checkpoint, f'{index}.mp4')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            trajectory = self.sequence[index]
            assert isinstance(trajectory, Trajectory)
            region = trajectory.getRegion()
            interval = trajectory.timestep[0], trajectory.timestep[-1]
            segment = self.video.subclipped(*interval)
            assert isinstance(segment, moviepy.VideoFileClip)
            segment = segment.cropped(*region)
            segment.write_videofile(
                path, codec="libx264", audio_codec="aac", logger=None
            )
            continue
        return(True)

    def makeDetection(self, frame: numpy.ndarray) -> bool:
        response = self.model.get_landmarks(
            frame, 
            return_bboxes=True, 
            return_landmark_score=True
        )
        detection = []
        for landmark, likelihood, prediction in zip(*response):
            count = numpy.array(sum(likelihood<0.7)).item() # likelihood (landmark)
            if(count>0): continue
            box = numpy.array(prediction[:-1]).astype(int)
            probability = round(float(prediction[-1]), 3)
            if(probability<0.8): continue
            shot = Shot(frame, box, landmark)
            detection += [shot]
            continue
        self.detection = detection
        return(True)

    def launchJob(self, checkpoint: str) -> bool:
        self.readVideo()
        self.captureSequence()
        self.filterSequence()
        self.saveSequence(checkpoint)
        return(True)

    total = 0
    queue = []
    model = face_alignment.FaceAlignment(
        face_alignment.LandmarksType.TWO_D, 
        device='cuda'
    )    
    pass

agent = Agent(path='./video/_V1NYVMWkiE_30sec.mp4')
agent.launchJob(checkpoint='checkpoint')
