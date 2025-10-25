"""
StoryCrafter Vercel Serverless Function
"""

from fastapi import FastAPI
from mangum import Mangum
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app from main
from main import app

# Wrap with Mangum for serverless
handler = Mangum(app, lifespan="off")
