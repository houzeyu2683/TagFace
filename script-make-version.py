import glob
import os
import sklearn.model_selection
import foundation
import pandas
import shutil

storage = 'rocket'
version = '20250906'
involvement = [
    'PL9mUJWHev0KkbsPtDReSYo-b1e_IIx_L8',
    'PL9mUJWHev0Kkzf4n0sL79Azle8X_r-ZB4',
    'PL9mUJWHev0Klo61lR1HwHxSvngSnhKAQg',
    'PLf5hP3QpCpY5VYN0AJQrELWxgUJUIV3yw',
    'PLkP0kGDs5Otdm84ZBZcDTAlit6bYMoyTV',
    'PLp7hnLHxd1KFmDKEV3AMpCrNW21Nz9AVT',
    'PLp7hnLHxd1KHpyw5U3kCEVpUiST-01rtO',
    'PLxdm6JxBd9NOWyyawr_VGErauc-fWjrkw',
    'PLXMYSc0NrSxo9OOw28wpiigFjpZgQgGVF',
]
folder = './download/*/#face/*/*.mp4'
iteration = glob.glob(folder)
collection = []
for path in iteration:
    lock = any(channel in path for channel in involvement)
    if(not lock): 
        continue
    collection += [path]
    continue
_ = iteration
pass
chunk = 1000
index = 0
batch = -1
root = os.path.join(storage, version)
iteration = collection
for source in iteration:
    if(index%chunk==0): batch += 1
    # source
    node = [
        root,
        'video',
        f'{batch}',
        os.path.basename(os.path.dirname(source)),
        os.path.basename(source)
    ]
    path = foundation.getPath(node, create=True)
    shutil.copy(source, path)
    index += 1
    continue
_ = iteration
iteration = glob.glob(f'video/**/*.mp4', root_dir=root, recursive=True)
data, lock = sklearn.model_selection.train_test_split(
    iteration, test_size=0.4, random_state=0
)
validation, test = sklearn.model_selection.train_test_split(
    lock, test_size=0.5, random_state=0
)
# foundation.getPath(create=True)
# data = pandas.DataFrame({"video": data})
# data.to_csv(
#     foundation.getPath([root, f'data.csv'], create=True),
#     index=False
# )
foundation.writeText(
    '\n'.join(data),
    foundation.getPath([root, f'data.txt'], create=True),
)
# validation = pandas.DataFrame({"video": validation})
# validation.to_csv(
#     foundation.getPath([root, f'validation.csv'], create=True), 
#     index=False
# )
foundation.writeText(
    '\n'.join(validation),
    foundation.getPath([root, f'validation.txt'], create=True)
)
# test = pandas.DataFrame({"video": test})
# test.to_csv(
#     foundation.getPath([root, f'test.csv'], create=True), 
#     index=False
# )
foundation.writeText(
    '\n'.join(test),
    foundation.getPath([root, f'test.txt'], create=True)
)
