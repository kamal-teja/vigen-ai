# S3 Deployment Script for Vigen Frontend (PowerShell)

# Configuration
$BUCKET_NAME = "vigen-ai"
$CLOUDFRONT_DISTRIBUTION_ID = "ESVG7ABJYQ8CK" # Optional

Write-Host "🚀 Building production bundle..." -ForegroundColor Yellow
npm run build:prod

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host "📦 Uploading to S3..." -ForegroundColor Yellow
    
    # Upload files to S3
    aws s3 sync dist/ s3://$BUCKET_NAME/ --delete --cache-control "public, max-age=31536000" --exclude "*.html"
    aws s3 sync dist/ s3://$BUCKET_NAME/ --delete --cache-control "public, max-age=0, must-revalidate" --include "*.html"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Upload successful!" -ForegroundColor Green
        
        # Invalidate CloudFront cache (optional)
        if ($CLOUDFRONT_DISTRIBUTION_ID -ne "your-cloudfront-distribution-id") {
            Write-Host "🔄 Invalidating CloudFront cache..." -ForegroundColor Yellow
            aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
        }
        
        Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Upload failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}