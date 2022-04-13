
# https://tech.asimio.net/2015/09/27/A-static-blog-hosted-at-Amazon-S3-built-with-Jekyll-and-Jenkins.html#publishing-jekyll-generated-static-site-to-aws-s3

docker run --net=host -e DB_TYPE=mysql -e DB_HOST=`hostname` -e DB_PORT=3306 -e DB_NAME=geofacts_db_001 \
 -e DB_USER=vfcreator -e DB_PASSWD=8cwrr123# \
 -e DB_SCHEMAS=public -e JDBC_DRIVER_PATH=/opt/asimio/schemaspy/jdbc -v ~/Downloads/schemaspy:/opt/asimio/schemaspy asimio/schemaspy:latest
