#!/bin/bash

set -e

echo "🚀 Starting Google Cloud deployment..."

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID environment variable is not set"
    exit 1
fi

if [ -z "$GCP_REGION" ]; then
    echo "❌ Error: GCP_REGION environment variable is not set"
    exit 1
fi

if [ -z "$GCP_SERVICE_NAME" ]; then
    echo "❌ Error: GCP_SERVICE_NAME environment variable is not set"
    exit 1
fi

echo "📦 Building Docker image..."
docker build -t gcr.io/${GCP_PROJECT_ID}/${GCP_SERVICE_NAME}:latest .

echo "🔐 Authenticating with Google Cloud..."
gcloud auth configure-docker --quiet

echo "📤 Pushing image to Google Container Registry..."
docker push gcr.io/${GCP_PROJECT_ID}/${GCP_SERVICE_NAME}:latest

echo "🚢 Deploying to Cloud Run..."
gcloud run deploy ${GCP_SERVICE_NAME} \
    --image gcr.io/${GCP_PROJECT_ID}/${GCP_SERVICE_NAME}:latest \
    --platform managed \
    --region ${GCP_REGION} \
    --allow-unauthenticated \
    --set-env-vars "$(cat .env | grep -v '^#' | grep -v '^$' | tr '\n' ',' | sed 's/,$//')" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10

echo "🔄 Running database migrations..."
gcloud run jobs create migrate-${GCP_SERVICE_NAME} \
    --image gcr.io/${GCP_PROJECT_ID}/${GCP_SERVICE_NAME}:latest \
    --region ${GCP_REGION} \
    --command alembic \
    --args upgrade,head \
    --set-env-vars "$(cat .env | grep -v '^#' | grep -v '^$' | tr '\n' ',' | sed 's/,$//')" \
    || echo "Migration job already exists, updating..."
gcloud run jobs update migrate-${GCP_SERVICE_NAME} \
    --image gcr.io/${GCP_PROJECT_ID}/${GCP_SERVICE_NAME}:latest \
    --region ${GCP_REGION}

gcloud run jobs execute migrate-${GCP_SERVICE_NAME} --region ${GCP_REGION}

echo "✅ Deployment complete!"
echo "🌐 Service URL:"
gcloud run services describe ${GCP_SERVICE_NAME} --region ${GCP_REGION} --format 'value(status.url)'

