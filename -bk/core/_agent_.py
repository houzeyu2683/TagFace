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
    # 評估指標類別，用於計算預測結果與真實值之間的相似度分數

    def __init__(self, method: str) -> None:
        # 初始化評估方法，支援 'IoU' 和 'Similarity' 兩種方式
        self.method = method
        return

    def getScore(
        self,
        prediction: numpy.ndarray, 
        truth: numpy.ndarray
    ) -> float:
        # 根據設定的方法計算預測結果與真實值的分數
        if(self.method=='IoU'):
            # 使用 IoU (Intersection over Union) 計算邊界框重疊率
            score = torchvision.ops.box_iou(
                torch.tensor(prediction)[None],
                torch.tensor(truth)[None]
            )
            score = score.item()
            pass
        elif(self.method=='Similarity'):
            # 使用結構相似性指標 (SSIM) 計算圖像相似度
            score = skimage.metrics.structural_similarity(
                prediction,
                truth,
                data_range=255.0
            )
            score = numpy.array(score).item()
            pass
        # 將分數四捨五入至三位小數
        score = round(score, 3)
        return(score)

    pass

class Shot:
    # 儲存單一影格中偵測到的人臉資訊，包含影格、邊界框和特徵點

    def __init__(
        self, 
        frame: numpy.ndarray,
        box: numpy.ndarray,
        landmark: numpy.ndarray
    ) -> None:
        # 初始化人臉截圖物件
        # frame: 完整的影格圖像
        # box: 人臉邊界框座標 [x1, y1, x2, y2]
        # landmark: 人臉特徵點座標
        self.frame = frame
        self.box = box
        self.landmark = landmark
        return

    def getArea(self, size: tuple, color: bool) -> numpy.ndarray:
        # 從影格中擷取人臉區域並調整大小
        # size: 目標尺寸 (width, height)
        # color: 是否保留彩色，False 則轉為灰階
        image = PIL.Image.fromarray(self.frame)
        image = image.crop(self.box)  # 根據邊界框裁切人臉區域
        if(not color): image = image.convert("L")  # 轉換為灰階
        image = image.resize(size)  # 調整至指定尺寸
        area = numpy.array(image)
        return(area)

    def getSize(self) -> tuple:
        # 取得影格的尺寸
        height, width, _ = self.frame.shape
        size = (height, width)
        return(size)

    pass

class Trajectory:
    # 追蹤同一人臉在連續影格中的軌跡變化

    def __init__(self, size: tuple, fragment: list, timestep: list) -> None:
        # 初始化軌跡物件
        # size: 影片尺寸 (height, width)
        # fragment: 儲存 Shot 物件的列表
        # timestep: 對應每個 Shot 的時間點
        self.size = size
        self.fragment = fragment
        self.timestep = timestep
        return

    def getContinuity(self, shot: Shot) -> bool:
        # 判斷新的 Shot 是否能與當前軌跡連續
        memory = self.fragment[-1]  # 取得軌跡中的最後一個 Shot
        assert isinstance(memory, Shot)
        # 首先檢查邊界框的 IoU 重疊率
        score = Metric('IoU').getScore(memory.box, shot.box)
        if(score<0.8): return(False)  # IoU 低於 0.8 則不連續
        # 再檢查人臉區域的結構相似性
        size = (64, 64)
        truth = memory.getArea(size, color=False)
        prediction = shot.getArea(size, color=False)
        score = Metric('Similarity').getScore(prediction, truth)
        if(score<0.8): return(False)  # 相似度低於 0.8 則不連續
        return(True)

    def increaseFragment(self, shot: Shot) -> bool:
        # 將新的 Shot 加入軌跡片段中
        self.fragment = self.fragment + [shot]
        return(True)

    def increaseTimestep(self, second: float) -> bool:
        # 將對應的時間點加入時間列表中
        self.timestep = self.timestep + [second]
        return(True)

    def getRegion(self) -> numpy.ndarray:
        # 計算整個軌跡的包圍區域，用於裁切影片
        # 集中所有片段中的邊界框座標
        box = []
        for shot in self.fragment:
            assert isinstance(shot, Shot)
            box += [shot.box]
            continue
        # 將所有邊界框堆疊成矩陣
        box = numpy.stack(box)
        # 計算所有邊界框的包圍範圍
        origin = (
            box[:,0].min(), # 最左邊 x 座標
            box[:,1].min(), # 最上邊 y 座標
            box[:,2].max(), # 最右邊 x 座標
            box[:,3].max() # 最下邊 y 座標
        )
        # 為包圍範圍增加 10% 的緩衝區域
        delta = [
            (origin[2] - origin[0]) * 0.1, # 寬度增量
            (origin[3] - origin[1]) * 0.1 # 高度增量
        ]
        height, width = self.size
        # 確保包圍範圍不超出影片邊界
        region = (
            max(origin[0]-delta[0], 0),
            max(origin[1]-delta[1], 0),
            min(origin[2]+delta[0], width),
            min(origin[3]+delta[1], height)
        )        
        return(region)

    pass

class Agent:
    # 主要的處理代理，負責影片處理、人臉偵測和軌跡分析

    def __init__(self, path: str) -> None:
        # 初始化處理代理
        # path: 要處理的影片檔案路徑
        self.path = path
        return

    def makeDetection(self, frame: numpy.ndarray) -> bool:
        # 在單一影格中進行人臉偵測
        response = self.model.get_landmarks(
            frame, 
            return_bboxes=True, 
            return_landmark_score=True
        )
        detection = []
        for landmark, likelihood, prediction in zip(*response):
            # 檢查特徵點的置信度，過濾低品質的偵測結果
            count = numpy.array(sum(likelihood<0.7)).item() # 低於闾值的特徵點數量
            if(count>0): continue  # 如果有低品質特徵點則跳過
            # 提取邊界框座標和置信度
            box = numpy.array(prediction[:-1]).astype(int)
            probability = round(float(prediction[-1]), 3)
            if(probability<0.8): continue  # 置信度低於 0.8 則跳過
            # 建立 Shot 物件並加入偵測結果
            shot = Shot(frame, box, landmark)
            detection += [shot]
            continue
        self.detection = detection
        return(True)

    def readVideo(self) -> bool:
        # 讀取影片檔案並驗證格式
        video = moviepy.VideoFileClip(self.path)
        # 確保影片格式符合要求：fps=25，時長至少 1 秒
        assert (video.fps == 25) and (video.duration >= 1)
        self.video = video
        return(True)

    def captureSequence(self) -> bool:
        # 逐格分析影片並建立人臉軌跡序列
        delta = 1 / self.video.fps  # 每格之間的時間間隔
        sequence = {}  # 儲存完整的軌跡序列
        for index, frame in enumerate(self.video.iter_frames(), start=0):
            second = index / self.video.fps  # 當前時間點
            unit = round(second + delta, 3)  # 下一格的時間點
            print(f'Analyze [{second}, {unit}) Interval', end='\r')
            self.makeDetection(frame)  # 在當前影格中偵測人臉
            # 情況1: 有待處理軌跡但當前無偵測結果 - 結束所有軌跡
            if(self.queue!=[] and self.detection==[]): 
                # 所有的 queue 都打包成一個完整的片段
                for trajectory in self.queue:
                    item = {self.total: trajectory}
                    sequence.update(item)
                    self.total += 1
                    continue
                _, _ = index, frame
                self.queue = []  # 清空佇列
                continue
            # 情況2: 有待處理軌跡且有新偵測結果 - 嘗試匹配和合併
            if(self.queue!=[] and self.detection!=[]):
                # 查詢可以合併的 trajectory 跟 shot
                rule = []  # 儲存可以匹配的配對
                # 建立所有軌跡與偵測結果的配對組合
                grid = list(
                    itertools.product(
                        range(len(self.queue)), 
                        range(len(self.detection))
                    )
                )
                # 檢查每個配對是否具有連續性
                for cell in grid:
                    trajectory = self.queue[cell[0]]
                    shot = self.detection[cell[1]]
                    assert isinstance(trajectory, Trajectory)
                    assert isinstance(shot, Shot)
                    continuity = trajectory.getContinuity(shot)
                    if(continuity): rule += [cell]  # 記錄可匹配的配對
                    continue
                rule = numpy.array(rule)
                summary = numpy.unique(rule, axis=0)  # 去除重複的匹配
                if(summary.size==0): summary = numpy.array([(-1, -1)])  # 無匹配時的預設值
                # 合併匹配的 trajectory 跟 shot
                for cell in summary:
                    if(cell[0]==-1 and cell[1]==-1): continue
                    trajectory = self.queue[cell[0]]
                    shot = self.detection[cell[1]]
                    assert isinstance(trajectory, Trajectory)
                    assert isinstance(shot, Shot)
                    trajectory.increaseFragment(shot)  # 將 shot 加入軌跡
                    trajectory.increaseTimestep(second)  # 記錄時間點
                    continue
                # 處理未匹配的 trajectory - 結束並儲存
                acceptance = []  # 保留繼續追蹤的軌跡
                for anchor, trajectory in enumerate(self.queue):
                    if(anchor in summary[:, 0]): 
                        acceptance += [trajectory]  # 已匹配的軌跡繼續追蹤
                        continue
                    # 未匹配的軌跡結束並儲存
                    item = {self.total: trajectory}
                    sequence.update(item)
                    self.total += 1
                    continue
                self.queue = acceptance
                # 處理未匹配的 shot - 建立新軌跡
                for anchor, shot in enumerate(self.detection):
                    assert isinstance(shot, Shot)
                    if(anchor in summary[:, 1]): continue  # 已匹配的 shot 跳過
                    # 為未匹配的 shot 建立新軌跡
                    trajectory = Trajectory(
                        size=shot.getSize(), 
                        fragment=[shot], 
                        timestep=[second]
                    )
                    self.queue += [trajectory]
                    continue
                _, _ = anchor, frame
                continue
            # 情況3: 無待處理軌跡但有新偵測結果 - 建立新軌跡
            if(self.queue==[] and self.detection!=[]):
                for anchor, shot in enumerate(self.detection):
                    assert isinstance(shot, Shot)
                    # 為每個偵測到的人臉建立新軌跡
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
        self.sequence = sequence  # 儲存完整的軌跡序列
        return(True)

    def filterSequence(self) -> bool:
        # 過濾軌跡序列，保留符合條件的軌跡
        # 未來可擴展：挑出嘴巴有在動的或是聲音與臉部匹配的
        sequence = {}
        for index in self.sequence:
            trajectory = self.sequence[index]
            assert isinstance(trajectory, Trajectory)
            # 過濾條件1: 軌跡持續時間至少 1 秒
            second = trajectory.timestep[-1] - trajectory.timestep[0]
            if(second<=1): continue
            # 過濾條件2: 人臉區域尺寸至少 128x128 像素
            region = trajectory.getRegion()
            width = (region[2] - region[0])
            height = (region[3] - region[1])
            if(width<128 or height<128): continue
            # 符合條件的軌跡保留下來
            sequence.update({index: trajectory})
            continue
        self.sequence = sequence
        return(True)

    def saveSequence(self, checkpoint: str) -> bool:
        # 將過濾後的軌跡序列儲存為獨立的影片檔案
        for index in self.sequence:
            # 建立輸出檔案路徑
            path = os.path.join(checkpoint, f'{index}.mp4')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            trajectory = self.sequence[index]
            assert isinstance(trajectory, Trajectory)
            # 取得軌跡的空間和時間範圍
            region = trajectory.getRegion()  # 空間範圍（裁切區域）
            interval = trajectory.timestep[0], trajectory.timestep[-1]  # 時間範圍
            # 從原始影片中擷取對應的時間片段
            segment = self.video.subclipped(*interval)
            assert isinstance(segment, moviepy.VideoFileClip)
            # 裁切至人臉區域
            segment = segment.cropped(*region)
            # 輸出為 MP4 檔案
            segment.write_videofile(
                path, codec="libx264", audio_codec="aac", logger=None
            )
            continue
        return(True)

    def searchFace(self, checkpoint: str) -> bool:
        # 執行完整的影片處理流程
        self.readVideo()        # 讀取影片檔案
        self.captureSequence()  # 分析影格並建立軌跡
        self.filterSequence()   # 過濾軌跡序列
        self.saveSequence(checkpoint)  # 儲存結果
        return(True)

    # 類別變數
    total = 0  # 軌跡總數計數器
    queue = []  # 待處理的軌跡佇列
    # 人臉偵測模型，使用 CUDA 加速
    model = face_alignment.FaceAlignment(
        face_alignment.LandmarksType.TWO_D, 
        device='cuda'
    )    
    pass

