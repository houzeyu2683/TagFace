import os

def getPath(node: list, create: bool) -> str:
    path = '/'.join(node)
    if('./'!=path[0:2]): path = os.path.join('./', path)
    if(not create):
        return(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return(path)

# node = ['a', 'b', 'c']
# os.path.dirname('a/b')