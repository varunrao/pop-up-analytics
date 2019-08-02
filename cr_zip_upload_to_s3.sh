#!/usr/bin/env bash
S3_BUCKET=pop-up-analytics-us-east-1

S3_BUCKET_LIST="pop-up-analytics-us-east-1"


for S3_BUCKET in $S3_BUCKET_LIST; do
    # Copy cloudformations
    pushd cloudformation;

    aws s3 cp . s3://$S3_BUCKET/cloudformation/ --content-type 'text/x-yaml' --recursive --profile account4

    popd
done