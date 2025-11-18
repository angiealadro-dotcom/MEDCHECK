#!/bin/bash
# Build script for Cloudflare Pages

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/css static/js static/img

echo "✅ Build completed successfully"
