"""
Recommendation Algorithm for Babel Protocol

This algorithm implements content recommendation capabilities that balance
relevance, engagement, authenticity, and temporal factors while promoting
healthy content discovery and community interaction.
"""

from typing import Dict, List, Optional, Any
import time
from datetime import datetime
from pydantic import BaseModel
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from .base import BabelAlgorithm

class ContentRecommendation(BaseModel):
    """Content recommendation model"""
    content_id: str
    score: float
    relevance_score: float
    engagement_score: float
    authenticity_score: float
    temporal_score: float

class ContentRecommendationSystem(BabelAlgorithm):
    """Content Recommendation implementation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize NLP components
        self.word_tokenizer = TreebankWordTokenizer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Content store
        self.content_store: Dict[str, Dict[str, Any]] = {}
        
        # User interaction history
        self.user_history: Dict[str, List[str]] = {}
        
        # Content engagement metrics
        self.engagement_metrics: Dict[str, Dict[str, float]] = {}
    
    def add_content(
        self,
        content_id: str,
        text: str,
        timestamp: float,
        authenticity_score: float
    ) -> None:
        """Add content to recommendation system"""
        # Process text
        tokens = self.word_tokenizer.tokenize(text.lower())
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]
        
        # Store content
        self.content_store[content_id] = {
            'text': text,
            'tokens': tokens,
            'timestamp': timestamp,
            'authenticity_score': authenticity_score,
            'engagement_score': self.engagement_metrics.get(
                content_id, {'score': 0.5}
            ).get('score', 0.5)
        }
    
    def update_engagement(
        self,
        content_id: str,
        user_id: str,
        engagement_type: str,
        engagement_value: float
    ) -> None:
        """Update content engagement metrics"""
        if content_id not in self.engagement_metrics:
            self.engagement_metrics[content_id] = {
                'score': 0.5,
                'interactions': 0
            }
        
        # Update metrics
        metrics = self.engagement_metrics[content_id]
        metrics['interactions'] += 1
        
        # Weight new engagement value
        alpha = 1 / (1 + metrics['interactions'])  # Decay factor
        metrics['score'] = (
            (1 - alpha) * metrics['score'] +
            alpha * engagement_value
        )
        
        # Update content store
        if content_id in self.content_store:
            self.content_store[content_id]['engagement_score'] = metrics['score']
        
        # Update user history
        if user_id not in self.user_history:
            self.user_history[user_id] = []
        self.user_history[user_id].append(content_id)
    
    def process(self, data: Dict[str, Any]) -> List[ContentRecommendation]:
        """Generate recommendations for user"""
        user_id = data['user_id']
        
        # Check cache
        cache_key = f"recommendations:{user_id}"
        cached_result = self.get_cache(cache_key)
        if cached_result:
            return [ContentRecommendation.parse_raw(item) for item in cached_result]
        
        recommendations = []
        current_time = time.time()
        
        for content_id, content in self.content_store.items():
            # Calculate scores
            temporal_score = self._calculate_temporal_score(
                content['timestamp'],
                current_time
            )
            
            relevance_score = 0.8  # Placeholder - would use actual relevance calculation
            
            recommendation = ContentRecommendation(
                content_id=content_id,
                score=self._calculate_final_score(
                    relevance_score,
                    content['engagement_score'],
                    content['authenticity_score'],
                    temporal_score
                ),
                relevance_score=relevance_score,
                engagement_score=content['engagement_score'],
                authenticity_score=content['authenticity_score'],
                temporal_score=temporal_score
            )
            recommendations.append(recommendation)
        
        # Sort by score
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        # Cache results
        self.set_cache(cache_key, [r.json() for r in recommendations])
        
        return recommendations[:10]  # Return top 10
    
    def _calculate_temporal_score(
        self,
        content_timestamp: float,
        current_time: float
    ) -> float:
        """Calculate temporal relevance score"""
        age_hours = (current_time - content_timestamp) / 3600
        return max(0.0, 1.0 - (age_hours / 72))  # Decay over 72 hours
    
    def _calculate_final_score(
        self,
        relevance: float,
        engagement: float,
        authenticity: float,
        temporal: float
    ) -> float:
        """Calculate final recommendation score"""
        weights = {
            'relevance': 0.3,
            'engagement': 0.2,
            'authenticity': 0.4,
            'temporal': 0.1
        }
        
        return sum([
            relevance * weights['relevance'],
            engagement * weights['engagement'],
            authenticity * weights['authenticity'],
            temporal * weights['temporal']
        ]) 