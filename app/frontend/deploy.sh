#!/bin/bash

# S3 Deployment Script for Vigen Frontend
# Make sure to configure AWS CLI first: aws configure

# Configuration
BUCKET_NAME="your-s3-bucket-name"
CLOUDFRONT_DISTRIBUTION_ID="your-cloudfront-distribution-id" # Optional

echo "🚀 Building production bundle..."
npm run build:prod

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📦 Uploading to S3..."
    
    # Upload files to S3
    aws s3 sync dist/ s3://$BUCKET_NAME/ --delete --cache-control "public, max-age=31536000" --exclude "*.html"
    aws s3 sync dist/ s3://$BUCKET_NAME/ --delete --cache-control "public, max-age=0, must-revalidate" --include "*.html"
    
    if [ $? -eq 0 ]; then
        echo "✅ Upload successful!"
        
        # Invalidate CloudFront cache (optional)
        if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
            echo "🔄 Invalidating CloudFront cache..."
            aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
        fi
        
        echo "🎉 Deployment completed successfully!"
    else
        echo "❌ Upload failed!"
        exit 1
    fi
else
    echo "❌ Build failed!"
    exit 1
fi