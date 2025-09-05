import datasets
import foundation
import os

token = ''
repository = ''

# 下載資料集
dataset = datasets.load_dataset(
    repository, 
    token=token,
    cache_dir=foundation.getPath(['cache'], create=True)
)
# 儲存資料集到本地
local_path = foundation.getPath(['version', 'pulled'], create=True)
dataset.save_to_disk(local_path)

print(f"Dataset downloaded to: {local_path}")

x = dataset['data'][1]['video']
for i in x:
    print(i.shape)
    continue


# 單元測試: 檢查資料集第一個項目
if(len(dataset) > 0):
    sample = dataset[0]
    print("Dataset sample:", sample)
    print("Dataset keys:", sample.keys() if hasattr(sample, 'keys') else "No keys available")
else:
    print("Dataset is empty")
    pass

# 顯示資料集資訊
print(f"Dataset info: {dataset}")
print(f"Dataset features: {dataset.column_names if hasattr(dataset, 'column_names') else 'No column names'}")

pass