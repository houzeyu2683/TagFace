import huggingface_hub
import datasets
import pandas
import os
import foundation
import glob
import tqdm

token = ''
repository = ''
root = 'rocket'
version = 'R2'
client = huggingface_hub.HfApi(token=token)
reference = client.list_repo_refs(
    repository, repo_type='dataset', token=token
)
branch = reference.branches[0].name

client.upload_large_folder(
    folder_path=foundation.getPath([root, version], False),
    repo_id=repository,
    repo_type="dataset",
    # token=token
)
data = pandas.read_table(
    foundation.getPath([root, version, 'data.txt'], False), header=None
)
data = data.rename(columns={0:'video'})
host = 'https://huggingface.co/datasets'
getLink = lambda item: f"{host}/{repository}/resolve/{branch}/{item}"
data['video'] = data['video'].map(getLink)
data = datasets.Dataset.from_pandas(data)
data = data.cast_column("video", datasets.Video())

validation = pandas.read_table(
    foundation.getPath([root, version, 'validation.txt'], False), header=None
)
validation = validation.rename(columns={0:'video'})
host = 'https://huggingface.co/datasets'
getLink = lambda item: f"{host}/{repository}/resolve/{branch}/{item}"
validation['video'] = validation['video'].map(getLink)
validation = datasets.Dataset.from_pandas(validation)
validation = validation.cast_column("video", datasets.Video())
test = pandas.read_table(
    foundation.getPath([root, version, 'test.txt'], False), header=None
)
test = test.rename(columns={0:'video'})
host = 'https://huggingface.co/datasets'
getLink = lambda item: f"{host}/{repository}/resolve/{branch}/{item}"
test['video'] = test['video'].map(getLink)
test = datasets.Dataset.from_pandas(test)
test = test.cast_column("video", datasets.Video())
navigation = {
    'data': data,
    'validation': validation,
    'test': test
}
session = datasets.DatasetDict(navigation)
session.push_to_hub(repository, token=token)



# data = foundation.getPath([root, version, 'data.txt'], False)
# client.upload_file(
#     path_or_fileobj=data,
#     path_in_repo=f'data.txt',
#     repo_id=repository,
#     repo_type="dataset",
#     token=token
# )
# validation = foundation.getPath([root, version, 'validation.txt'], False)
# client.upload_file(
#     path_or_fileobj=validation,
#     path_in_repo=f'validation.csv',
#     repo_id=repository,
#     repo_type="dataset",
#     token=token
# )
# test = foundation.getPath([root, version, 'test.txt'], False)
# client.upload_file(
#     path_or_fileobj=test,
#     path_in_repo=f'test.txt',
#     repo_id=repository,
#     repo_type="dataset",
#     token=token
# )
# for batch in os.listdir(os.path.join(root, version, 'video')):
#     source = foundation.getPath(
#         [root, version, 'video', f"{batch}"], False
#     )
#     target = foundation.getPath(
#         ['video', f"{batch}"], False
#     )
#     client.upload_large_folder(
#         folder_path=source,
#         # path_in_repo=target,
#         repo_id=repository,
#         repo_type="dataset",
#         # token=token
#     )
#     continue