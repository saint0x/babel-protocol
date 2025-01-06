"""
Algorithm Package Initialization

This module initializes the algorithm package and ensures all dependencies are properly set up.
It also provides convenient imports for the main components.
"""

import logging
from pathlib import Path

import nltk
import torch
from transformers import pipeline

from .interface import algorithm_interface
from .main import app as algorithm_app
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_nlp():
    """Initialize NLP components"""
    try:
        # Download required NLTK data
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('vader_lexicon')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        logger.info("NLTK data downloaded successfully")
    except Exception as e:
        logger.error(f"Failed to download NLTK data: {e}")
        raise

def initialize_ml_models():
    """Initialize machine learning models"""
    try:
        # Ensure models directory exists
        models_dir = Path(__file__).parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Initialize transformers pipelines
        _ = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        _ = pipeline("summarization", model="facebook/bart-large-cnn")
        
        logger.info("ML models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ML models: {e}")
        raise

def initialize():
    """Initialize all algorithm components"""
    try:
        # Initialize NLP components
        initialize_nlp()
        
        # Initialize ML models
        initialize_ml_models()
        
        # Log successful initialization
        logger.info("Algorithm package initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize algorithm package: {e}")
        raise

# Initialize package on import
initialize()

# Export main components
__all__ = ['algorithm_interface', 'algorithm_app', 'settings'] 