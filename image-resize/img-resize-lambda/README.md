## A lambda to resize and optimize images on S3 upload

An AWS lambda function to resize images as soon as they are uploaded on a S3 bucket.

### What's happening?:
This is a source bucket and target bucket scenario. The application will upload the image on source bucket and a lambda will intercept this upload event. It'll download the Object, resize, optimize and save to target bucket.

Lambda downloads the Object received in the bucket. Then the image is opened and converted to JPG. Lambda resizes the image in two sizes and uploads a JPG and WebP for the given file on the target bucket. **Please note the PNGs are also converted to JPGs and only JPGs are uploaded.**


### Attaching S3 bucket event to lambda
- Create a bucket, e.g. source
- Go to S3 bucket source > Properties
- Under Advance Settings find Events:
![S3 Event Setings](/image-resize/img-resize-lambda/images/s3-event-create-2.png)

- Click on Add notification
![S3 event add notification](/image-resize/img-resize-lambda/images/s3-event-add-notif.png)

- Enter name of the notification for your reference. Then choose `PUT` Events.
- Leave prefixes and suffixes blank if you don't know what they do.
- Under Option Send To, select lambda function
- In last Dropdown select your lambda function (`test-function` in image)
![S3 event add notification](/image-resize/img-resize-lambda/images/s3-event-add-notif-details.png)

### Running the script

The script can be run independently of AWS lambda.
Open file `image-resize-lambda.py` go line number: `153`
```
"name": "source_bucket",
```
Change the bucket name here.
Then change following to the desired file at line number: `160`
```
 "key": "path1/path2/pexels-photo-210012.jpeg",
```

**Make sure the file exists on S3 source bucket.**

Now run:
```
> python image-resize-lambda.py
```

