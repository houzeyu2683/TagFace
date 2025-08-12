import core
import os
import multiprocessing
folder = ''
checkpoint = './checkpoint'


loop = [os.path.join(folder, item) for item in os.listdir(folder)]

def startJob(path: str) -> bool:
    agent = core.Agent(path)
    name = os.path.basename(path).split('.')[0]
    checkpoint = os.path.join('./checkpoint', name)
    agent.searchFace(checkpoint)
    return(True)

pool = multiprocessing.Pool(processes=4)
pool.map(startJob, loop)

