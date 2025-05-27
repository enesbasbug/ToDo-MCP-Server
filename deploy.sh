#!/bin/bash

# Configuration
PROJECT_ID="your-todo-mcp-server"  # CHANGE THIS IF YOU NAMED IT DIFFERENT
SERVICE_NAME="todo-mcp-server"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Todo MCP Server to Google Cloud Run"
echo "================================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ Not authenticated with Google Cloud. Running 'gcloud auth login'..."
    gcloud auth login
fi

# Set the project
echo "📋 Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com

# Configure Docker authentication
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker

# Build the Docker image
echo "🏗️  Building Docker image..."
docker build -t ${IMAGE_NAME} .

# Push to Google Container Registry
echo "📤 Pushing image to GCR..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8050 \
    --memory 512Mi \
    --timeout 3600 \
    --concurrency 1000 \
    --max-instances 10

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo "✅ Deployment complete!"
echo "🌐 Your MCP server is available at: ${SERVICE_URL}/sse"
echo ""
echo "To test your deployment, update your client code to use:"
echo "client = TodoMCPClient('${SERVICE_URL}/sse')"