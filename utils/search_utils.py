import faiss
import torch
import clip
import numpy as np
from PIL import Image
from google.cloud import storage
from io import BytesIO
import os

# ================= 配置 =================
BUCKET_NAME = "clip-flickr-images-jcz"
FEATURE_FILE_GCS = "clip_features/image_features.npy"
PATH_FILE_GCS = "clip_features/image_paths.txt"
TOP_K = 50

# GCP 凭证
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/gcp_key.json"

# 设备和模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# ================= 工具函数 =================

def download_from_gcs(gcs_path, local_path):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.download_to_filename(local_path)

def load_features_and_paths():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # 直接从 GCS 读取 .npy 特征文件为 bytes
    feature_blob = bucket.blob(FEATURE_FILE_GCS)
    feature_bytes = feature_blob.download_as_bytes()
    features = np.load(BytesIO(feature_bytes)).astype("float32")

    # 直接读取 image_paths.txt 内容为字符串
    path_blob = bucket.blob(PATH_FILE_GCS)
    path_bytes = path_blob.download_as_bytes()
    image_paths = path_bytes.decode("utf-8").splitlines()

    return features, image_paths

# ================= 模块级初始化 =================
features, image_paths = load_features_and_paths()
faiss.normalize_L2(features)
faiss_index = faiss.IndexFlatIP(features.shape[1])
faiss_index.add(features)

# ================= 查询函数 =================

def search_by_text(text, top_k=TOP_K):
    text_input = clip.tokenize([text]).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_input)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    text_np = text_features.cpu().numpy().astype("float32")

    D, I = faiss_index.search(text_np, top_k)
    return [image_paths[i] for i in I[0]]

def search_by_image(file, top_k=TOP_K):
    image = Image.open(file).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input)
    image_features /= image_features.norm(dim=-1, keepdim=True)
    image_np = image_features.cpu().numpy().astype("float32")

    D, I = faiss_index.search(image_np, top_k)
    return [image_paths[i] for i in I[0]]
