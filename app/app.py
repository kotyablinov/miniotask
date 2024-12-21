from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

minio_config = {}
try:
    minio_config['ENDPOINT'] = os.environ['MINIO_ENDPOINT']
except KeyError:
    raise RuntimeError("Требуемая переменная среды 'MINIO_ENDPOINT' не установлена.")
try:
    minio_config['ACCESS_KEY'] = os.environ['MINIO_ACCESS_KEY']
except KeyError:
    raise RuntimeError("Требуемая переменная среды 'MINIO_ACCESS_KEY' не установлена.")
try:
    minio_config['SECRET_KEY'] = os.environ['MINIO_SECRET_KEY']
except KeyError:
    raise RuntimeError("Требуемая переменная среды 'MINIO_SECRET_KEY' не установлена.")
try:
    minio_config['BUCKET_NAME'] = os.environ['MINIO_BUCKET_NAME']
except KeyError:
    raise RuntimeError("Требуемая переменная среды 'MINIO_BUCKET_NAME' не установлена.")

# Инициализация клиента MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=f"http://{minio_config['ENDPOINT']}",
    aws_access_key_id=minio_config['ACCESS_KEY'],
    aws_secret_access_key=minio_config['SECRET_KEY'],
)


class UploadFileForm(FlaskForm):
    file = FileField("Файл", validators=[InputRequired()])
    submit = SubmitField("Послать")


@app.route('/', methods=['GET', "POST"])
@app.route('/home', methods=['GET', "POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data  # First grab the file
        bucket_name = minio_config['BUCKET_NAME']
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except:
            s3_client.create_bucket(Bucket=bucket_name)
            app.logger.info(f"Bucket '{bucket_name}' создан.")

        file_name = secure_filename(file.filename)
        try:
            s3_client.upload_fileobj(file, bucket_name, file_name)
        except NoCredentialsError:
            return "Ошибка: Проверьте учетные данные для MinIO."
        except Exception as e:
            return f"Ошибка при загрузке файла {file}: {e}"
        return f"Файл {file} успешно загружен в {bucket_name}."
    return render_template('index.html', form=form)


if __name__ == "__main__":
    host = os.environ.get('APP_HOST_NAME', "0.0.0.0")
    port = int(os.environ.get('APP_PORT', 5000))
    app.run(host=host, port=port)
