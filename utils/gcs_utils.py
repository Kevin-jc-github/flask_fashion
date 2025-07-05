from google.cloud import storage
import json
from google.oauth2 import service_account
import os

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/gcp_key.json"

# 从环境变量加载 json 内容
gcp_key_content = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
gcp_credentials = service_account.Credentials.from_service_account_info(json.loads(gcp_key_content))


def download(bucket_name, blob_name, local_folder='flask/static/images_cache'):
    """
    下载 GCS bucket 中的图片文件到本地 static/images_cache/ 文件夹。

    :param bucket_name: GCS bucket 名称
    :param blob_name: GCS 中的文件路径（即 blob 名）
    :param local_folder: 本地保存目录（默认 static/images_cache）
    :return: 本地文件的相对路径（可直接用于 Flask 渲染）
    """
    # 初始化客户端
    client = storage.Client(credentials=gcp_credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # 创建目标目录（如果不存在）
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # 提取文件名
    filename = os.path.basename(blob_name)

    # 本地完整路径
    local_path = os.path.join(local_folder, filename)

    # 下载文件
    blob.download_to_filename(local_path)

    print(f"✅ 下载完成: {blob_name} -> {local_path}")
    return os.path.join(local_folder, filename)

