import os
from minio import Minio
from minio.error import S3Error

MINIO_API = "10.2.1.65:9003"
MINIO_ACCESS_KEY = "admin_dev"
MINIO_SECRET_KEY = "pass_dev"
MINIO_SECURE = False  # Adjust if using HTTPS

minio_client = Minio(
    MINIO_API,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def ensure_bucket(bucket_name=str):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

def get_object(bucket_name: str, object_name: str) -> bytes:
    try:
        response = minio_client.get_object(bucket_name, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    except S3Error as e:
        raise Exception(f"Error getting object from MinIO: {str(e)}")

def put_object(bucket_name: str, object_name: str, file_path: str, content_type="text/csv"):
    try:
        ensure_bucket(bucket_name)
        minio_client.fput_object(bucket_name, object_name, file_path, content_type=content_type)
    except S3Error as e:
        raise Exception(f"Error putting object to MinIO: {str(e)}")

