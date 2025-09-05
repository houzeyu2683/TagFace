# '''
# path = f'./version/{version}/validation.txt'
# os.makedirs(os.path.dirname(path), exist_ok=True)
# with open(path, "w") as paper:
#     iteration = validation
#     for item in iteration:
#         paper.write(f"{item}\n")
#         continue
#     _ = iteration
#     pass
# _ = paper


# '''

# Following above code, write the function:
# def writeText(content: str, path: str) -> bool:
#    ....
#    return(True)

import os

def writeText(content: str, path: str) -> bool:
    # 建立目錄，如果不存在的話
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as paper:
        paper.write(content)
        pass
    _ = paper
    return(True)
