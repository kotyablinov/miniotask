import os
import boto3
from botocore.exceptions import NoCredentialsError

# Конфигурация MinIO
MINIO_ENDPOINT = "localhost:9000"
ACCESS_KEY = "SsbOjc5QK2MsGOdO36Is"
SECRET_KEY = "SdvNeRacpPliQOma2iwWt3XnkQCsAvY8azzZNXc8"
BUCKET_NAME = "images"
LOCAL_FOLDER = "./images"

# Инициализация клиента MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

def upload_images_to_minio(folder, bucket_name):
    # Создание bucket, если его еще нет
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' создан.")

    # Загрузка файлов из папки
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                try:
                    s3_client.upload_file(file_path, bucket_name, file)
                    print(f"Файл {file} успешно загружен в {bucket_name}.")
                except NoCredentialsError:
                    print("Ошибка: Проверьте учетные данные для MinIO.")
                except Exception as e:
                    print(f"Ошибка при загрузке файла {file}: {e}")

if __name__ == "__main__":
    upload_images_to_minio(LOCAL_FOLDER, BUCKET_NAME)
