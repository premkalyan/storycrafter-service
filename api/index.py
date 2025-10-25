"""
StoryCrafter Vercel Serverless Function
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app from main
# Vercel expects an 'app' variable for ASGI applications
from main import app

# Vercel will automatically handle the ASGI app
# No need for Mangum wrapper with native Vercel support
