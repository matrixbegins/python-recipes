import boto3, os
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta

aws_key_id = os.getenv('AWS_KEY_ID', 'KK' )
aws_access_key = os.getenv('AWS_ACCESS_KEY', 'ACC' )


def optimize_image(key, s3client):

    # check file format.
    filename, extension = os.path.splitext(key)
    if extension.lower() == ".webp":
        return

    # download image.
    source_bucket = os.getenv("SOURCE_BUCKET", "source")
    target_bucket = os.getenv("TARGET_BUCKET", "target")
    file_byte_string = download_object(key, source_bucket, s3client)

    # create/open image
    img = Image.open(BytesIO(file_byte_string)).convert('RGB')

    # create webp image
    webpImg = jpg_to_webp(img)

    # for PNG we need to convert it into JPG  then optimize and finally back to PNG
    if extension.lower() == ".png":
        jpgImg = Image.open(png_to_jpg(img))
        # back to png
        pngImg = png_to_jpg(jpgImg)

        # upload png to s3
        upload_object(key, target_bucket, pngImg, s3client)

    # upload optimized webp to s3
    upload_object(filename + '.webp', target_bucket, webpImg, s3client)


def download_object(key, src_bucket, s3client):
    print("getting S3 object:: ", key)
    return s3client.get_object(Bucket=src_bucket, Key=key)['Body'].read()


def upload_object(key, target_bucket, payload, s3client):
    expdate = datetime.now() + timedelta(days=15)
    return s3client.put_object(
            Body=payload,
            Bucket=target_bucket,
            Key=key,
            ContentType="image",
            CacheControl="public, max-age=31536000",
            Expires=expdate
        )


def jpg_to_webp(img):
    payload = BytesIO()

    img.save( payload, format="webp",optimize=True )
    payload.seek(0)

    return payload


def png_to_jpg(img):
    payload = BytesIO()

    img.save( payload, format="jpeg",optimize=True, quality=80)
    payload.seek(0)

    return payload


def jpg_to_png(img):
    payload = BytesIO()

    img.save( payload, format="png",optimize=True )
    payload.seek(0)

    return payload


def processImages(keys_file):
    # init boto3
    s3 = boto3.client('s3', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_access_key )


    with open(keys_file) as fp:
        for line in fp:
            print("processing image:: ", line.strip())
            optimize_image(line.strip(), s3)


print("completed.....")


if __name__ == '__main__':
    processImages("s3objects_imgs.txt")
