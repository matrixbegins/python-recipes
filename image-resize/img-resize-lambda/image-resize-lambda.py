import os, pathlib, sys, boto3

from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO


sizes = [ {"width": 140, "height": 140 },
        { "width": 1040, "height": 490 }]


def get_s3_object(client, src_bucket, key):
    print("getting S3 object:: ", key)
    return client.get_object(Bucket=src_bucket, Key=key)['Body'].read()

def put_s3_object(client, target_bucket, target_key, payload):
    expdate = datetime.now() + timedelta(days=15)
    return client.put_object(
            Body=payload,
            Bucket=target_bucket,
            Key=target_key,
            ContentType="image",
            CacheControl="public, max-age=31536000",
            Expires=expdate
        )


def create_webp(file_byte_string, size):
    img = Image.open(BytesIO(file_byte_string)).convert('RGB')
    payload = BytesIO()
    img.thumbnail( tuple(size.values()), Image.ANTIALIAS )
    img.save( payload, format="webp",optimize=True )
    payload.seek(0)

    return payload


def create_jpeg(file_byte_string, size):
    img = Image.open(BytesIO(file_byte_string)).convert('RGB')
    payload = BytesIO()
    img.thumbnail( tuple(size.values()), Image.ANTIALIAS )
    img.save( payload, format="jpeg",optimize=True, quality=80)
    payload.seek(0)

    return payload


def get_target_key(size, objectKey, target_ext):
    objectPath, file = os.path.split(objectKey)
    filename, _ = os.path.splitext(file)

    ext_mapping = {
        'webp': '.webp',
        'png': '.jpg',
        'gif': '.gif'
    }

    target_fileName = filename + ext_mapping.get(target_ext, '.jpg')

    # prepare the target key
    if objectPath == "":
        targetKey = "{}x{}/{}".format(size["width"], size["height"], target_fileName )
    else:
        targetKey = "{}/{}x{}/{}".format(objectPath, size["width"], size["height"], target_fileName )

    return targetKey



def resize_handler(event, context):
    if "Records" not in event:
        raise Exception("not a proper AWS S3 event")

    sourceBucket = event["Records"][0]["s3"]["bucket"]["name"]
    targetBucket = os.getenv("TARGET_BUCKET", "target_bucket")
    objectKey =  event["Records"][0]["s3"]["object"]["key"]


    print("sourceBucket:: ", sourceBucket)
    print("targetBucket:: ", targetBucket)
    print("objectKey:: ", objectKey)

    objectPath, file = os.path.split(objectKey)
    filename, extension = os.path.splitext(file)

    if filename is None or filename == "":
        print("invalid file name extracted: ", filename)
        return False

    if extension is None or extension == "":
        print("invalid file extension ", extension)
        return False

    supported_types = [ ".jpg", ".jpeg", ".png", ".gif" ]
    if extension not in supported_types:
        raise Exception("Document type not supported {} ".format(extension) )


    aws_key_id = os.getenv('AWS_KEY_ID', 'KK' )
    aws_access_key = os.getenv('AWS_ACCESS_KEY', 'ACC' )

    # init s3 client
    client = boto3.client('s3', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_access_key)
    file_byte_string = get_s3_object(client, sourceBucket, objectKey)

    for size in sizes:
        # check for image cropping
        print("processing size:: ", size)

        # creating webP and JPEG files
        webpImg = create_webp(file_byte_string, size)
        jpegImg = create_jpeg(file_byte_string, size)

        # now upload webp
        webp_target_key = get_target_key(size, objectKey, 'webp')
        print( "uploading size {} to path: {}".format(size, webp_target_key) )

        response = put_s3_object(client, targetBucket, webp_target_key, webpImg)
        print("upload results:: ", response)
        webpImg.close()

        # now upload jpg
        jpg_target_key = get_target_key(size, objectKey, 'jpg')
        print( "uploading size {} to path: {}".format(size, jpg_target_key) )

        response = put_s3_object(client, targetBucket, jpg_target_key, jpegImg)
        print("upload results:: ", response)
        jpegImg.close()



if __name__ == '__main__':
    event = {
        "Records": [
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-2",
            "eventTime": "2019-09-03T19:37:27.192Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
            "principalId": "AWS:PO5IXQXHT3IKHL2"
            },
            "requestParameters": {
            "sourceIPAddress": "225.255.255.255"
            },
            "responseElements": {
            "x-amz-request-id": "D5F771F645",
            "x-amz-id-2": "vlR7Pnbdvsca782biko5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emHGYXOo6QBU0Wo="
            },
            "s3": {
            "s3SchemaVersion": "1.0",
            "configurationId": "828aa6fc-f7b5-44456-8584-487c791949c1",
            "bucket": {
                "name": "source_bucket",
                "ownerIdentity": {
                "principalId": "A3I5XTGTPAI3E"
                },
                "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
            },
            "object": {
                "key": "path1/path2/fileName.jpeg",
                "size": 1305107,
                "eTag": "b21b84db07b05b1e6b33684dc11b",
                "sequencer": "0C0F6FED209E1"
            }
            }
        }
        ]
    }
    resize_handler(event, {})
