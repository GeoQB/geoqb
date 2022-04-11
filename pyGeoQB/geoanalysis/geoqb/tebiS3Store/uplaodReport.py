import boto3
from io import BytesIO
import os


# Let's use S3
s3 = boto3.resource(
    service_name='s3',
    aws_access_key_id=os.environ.get('aws_access_key_id'),
    aws_secret_access_key=os.environ.get('aws_secret_access_key'),
    endpoint_url= os.environ.get('s3_endpoint_url') )

def listBuckets():
    # Print out bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)

defaultBucketName = "geoqb-reports-mvp-1"

def uploadFile( fn, key, PREFIX="GeoQB-Analysis-Report-", bucket=defaultBucketName ):
    mykey = getMyKey( key )
    data = open( fn, 'rb')
    s3.Bucket( bucket ).put_object(Key=mykey, Body=data)
    print( ">>> TEBI S3 Store: { BUCKET: " + bucket + ", KEY: " + mykey + " }" )
    return( bucket, mykey )

def getMyKey( reportHash, PREFIX="GeoQB-Analysis-Report-" ):
    mykey = f"{PREFIX}{reportHash}.pdf"
    return mykey

def getURL( mykey, bucket=defaultBucketName ):
    PDF_URL = os.environ.get('s3_endpoint_url') + bucket + "/" + mykey + "?AWSAccessKeyId=3Aso9KSsQHrea8Tb&Signature=2HmbPU34Cm%2BLKnr6bkT6oLNH%2BeY%3D&Expires=1646578088"
    return PDF_URL

def readFile(reportHash, PREFIX="GeoQB-Analysis-Report-", bucket=defaultBucketName):
    mykey = getMyKey( reportHash )
    tempFN = './static/pdfs/'+mykey
    print( ">>> TEBI S3 Store Downloader : { KEY: " + mykey + ", FILE: " + tempFN + " }" )
    s3.Bucket( bucket ).download_file( mykey, tempFN )
    print( ">>> TEBI S3 Store Downloader : ----> Ready." )

    return tempFN







#
# We test the upload function ... TEBI is an S3 compatible storage service, where our reports will be hosted.
#
def main():

    print("> TEST UPLAOD to TEBI S3 service ...")
    fn = "./data/out/Layer-Inspection-v1-Location-Wismar (DE).pdf"

    hash = "5509530949889804855123"

    uploadFile( fn, hash, PREFIX="" )
    print("> Done")

    readFile( hash, PREFIX="" )


if __name__ == "__main__":
    main()

