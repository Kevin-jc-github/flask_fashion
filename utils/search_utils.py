import os
import json
import numpy as np
import torch
import clip
from PIL import Image
from google.cloud import storage
from google.oauth2 import service_account

# ====== 🔐 使用 GOOGLE_APPLICATION_CREDENTIALS 指定的 JSON key 文件路径 ======
gcp_key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
gcp_credentials = service_account.Credentials.from_service_account_file(gcp_key_path)

# ====== 🪣 连接 GCS 并下载文件 ======
client = storage.Client(credentials=gcp_credentials)
bucket_name = "clip-flickr-images-jcz"
bucket = client.bucket(bucket_name)

def download_blob(blob_name, destination_file):
    blob = bucket.blob(blob_name)
    blob.download_to_filename(destination_file)

# ====== 📥 下载 clip_features 中的 .npy 和 .txt 文件 ======
download_blob("clip_features/image_features.npy", "/tmp/image_features.npy")
download_blob("clip_features/image_paths.txt", "/tmp/image_paths.txt")

# ====== 📦 加载 CLIP 模型 ======
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# ====== 🔗 加载图像向量和路径 ======
image_features = np.load("/tmp/image_features.npy", mmap_mode="r")
with open("/tmp/image_paths.txt") as f:
    image_paths = f.read().splitlines()
image_features = torch.from_numpy(image_features).float().to(device)

# ====== 🔍 文本搜索函数 ======
def search_by_text(query, top_k=50):
    text_input = clip.tokenize([query]).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_input)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    similarities = (image_features @ text_features.T).squeeze(1)
    best_indices = similarities.topk(top_k).indices
    return [image_paths[i] for i in best_indices]

# ====== 🖼️ 图像搜索函数 ======
def search_by_image(image_path, top_k=50):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_query_features = model.encode_image(image)
        image_query_features /= image_query_features.norm(dim=-1, keepdim=True)
    similarities = (image_features @ image_query_features.T).squeeze(1)
    best_indices = similarities.topk(top_k).indices
    return [image_paths[i] for i in best_indices]
