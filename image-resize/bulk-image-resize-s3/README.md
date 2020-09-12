# Bulk image optimization of images present in a S3 bucket

## Usecase: Where this can be used?
Assume there is a S3 bucket which has only images on it. They are images in some format and are not optimized for size and we need to bring down the sizes of images so that images can be served on websites. The script `bulk_img_conversion.py` will convert and optimize such images. The following actions are taken:
- JPGs are optimized and uploaded as JPGs
- PNGs are converted to JPGs first, then optimized, then converted to back to PNGs and uploaded.
- For every image WebP format is also generated and uploaded.

**Please note there is no provision of resizing the images in these script.**

## Process

### Generate a list of all objects first.

```
> export AWS_KEY_ID=<aws_access_key_id>
> export AWS_ACCESS_KEY=<aws_secret_access_key>
> export SOURCE_BUCKET=<bucket name>
> export KEY_PREFIX=<prefix to filter the objects. leave blank or do not export of you don't want filter>
> python s3_key_collection.py
```

The above code will generate a file `s3objects_imgs.txt` with all objects in S3.
Now this file can be used by next script for image conversion.

### Start Conversion
```
> export AWS_KEY_ID=<aws_access_key_id>
> export AWS_ACCESS_KEY=<aws_secret_access_key>
> export SOURCE_BUCKET=<bucket name>
> export TARGET_BUCKET=<bucket name>
> python bulk_img_conversion.py
```

**If you want to run the script again don't forget to remove `s3objects_imgs.txt` file.**

For best speed run this script on an EC2 instance.

## Requirements
```
Pillow==7.2.0
boto3==1.14.28
```
