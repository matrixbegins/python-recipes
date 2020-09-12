import boto3, json, csv, os


def collectKeys(objects):
    print("\n\nprocessing next batch====================")
    last_key = ""
    file1 = open("s3objects_imgs.txt","a+")

    keyList = []
    for obj in objects:
        # print(obj.get('Key'))

        keyList.append(obj.get('Key') + "\n")
        # we have to return last key to caller
        last_key = obj.get('Key')

    file1.writelines(keyList)
    file1.close()
    return last_key


aws_key_id = os.getenv('AWS_KEY_ID', 'KK' )
aws_access_key = os.getenv('AWS_ACCESS_KEY', 'ACC' )

source_bucket = os.getenv('SOURCE_BUCKET', 'mybuckets')

key_prefix = os.getenv('KEY_PREFIX', '')

s3 = boto3.client('s3', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_access_key )

pagesize = 50

last_key = ""

resultSize = 100

while resultSize >= pagesize:
    bucket_content = s3.list_objects(Bucket=source_bucket, Prefix=key_prefix, MaxKeys=pagesize, Marker=last_key)
    last_key = collectKeys(bucket_content['Contents'])
    print(" ------- last_key of the batch---------------: ", last_key)
    resultSize = len(bucket_content['Contents'])
    # resultSize = 40


print("completed---- resultSize: ", resultSize)

