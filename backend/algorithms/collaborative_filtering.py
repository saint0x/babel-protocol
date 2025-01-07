"""
Collaborative Filtering Algorithm for Content Recommendations
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel

from .base import BaseAlgorithm, AlgorithmResponse
from .models.recommendation import RecommendationScore

class UserProfile(BaseModel):
    """User profile for collaborative filtering"""
    interests: List[str]
    expertise_areas: List[str]
    engagement_patterns: Dict[str, Any]

class CollaborativeFilter(BaseAlgorithm):
    """Collaborative filtering implementation combining user similarity and content features"""
    
    def __init__(self):
        super().__init__()
        self.user_vectors = {}  # Store user feature vectors
        self.content_vectors = {}  # Store content feature vectors
        self.user_content_matrix = {}  # Store user-content interactions
        
    def _create_user_vector(self, user_profile: Dict[str, Any]) -> np.ndarray:
        """Create a feature vector for a user based on their profile"""
        # Extract features from user profile
        interests = set(user_profile.get('interests', []))
        expertise = set(user_profile.get('expertise_areas', []))
        engagement = user_profile.get('engagement_patterns', {})
        
        # Create feature vector components
        interest_vec = np.array([
            len(interests & {'blockchain', 'crypto', 'defi'}),  # Tech focus
            len(interests & {'philosophy', 'ethics', 'society'}),  # Philosophy focus
            len(interests & {'trading', 'market', 'analysis'}),  # Trading focus
            len(interests & {'security', 'privacy', 'cryptography'}),  # Security focus
            len(interests & {'community', 'governance', 'education'})  # Community focus
        ])
        
        expertise_vec = np.array([
            len(expertise & {'programming', 'development', 'engineering'}),
            len(expertise & {'research', 'academic', 'mathematics'}),
            len(expertise & {'trading', 'economics', 'finance'}),
            len(expertise & {'security', 'auditing', 'cryptography'}),
            len(expertise & {'community', 'moderation', 'writing'})
        ])
        
        engagement_vec = np.array([
            engagement.get('reading_depth', 0.5),
            engagement.get('comment_frequency', 0.5),
            engagement.get('content_creation', 0.5),
            engagement.get('preferred_complexity', 0.5)
        ])
        
        # Combine all features
        return np.concatenate([
            interest_vec / max(1, np.sum(interest_vec)),
            expertise_vec / max(1, np.sum(expertise_vec)),
            engagement_vec
        ])
    
    def _create_content_vector(self, content: Dict[str, Any]) -> np.ndarray:
        """Create a feature vector for content based on its properties"""
        tags = set(content.get('tags', []))
        
        # Create feature vector components
        topic_vec = np.array([
            len(tags & {'blockchain', 'crypto', 'defi'}),
            len(tags & {'philosophy', 'ethics', 'society'}),
            len(tags & {'trading', 'market', 'analysis'}),
            len(tags & {'security', 'privacy', 'cryptography'}),
            len(tags & {'community', 'governance', 'education'})
        ])
        
        property_vec = np.array([
            content.get('complexity_level', 0.5),
            1.0 if content.get('flags', []) else 0.0,  # Flagged content
            len(content.get('expected_audience', [])) / 5.0  # Audience breadth
        ])
        
        # Combine features
        return np.concatenate([
            topic_vec / max(1, np.sum(topic_vec)),
            property_vec
        ])
    
    def add_user(self, user_id: str, user_profile: Dict[str, Any]):
        """Add or update a user in the collaborative system"""
        self.user_vectors[user_id] = self._create_user_vector(user_profile)
        if user_id not in self.user_content_matrix:
            self.user_content_matrix[user_id] = {}
    
    def add_content(self, content_id: str, content: Dict[str, Any]):
        """Add or update content in the collaborative system"""
        self.content_vectors[content_id] = self._create_content_vector(content)
    
    def record_interaction(self, user_id: str, content_id: str, interaction_strength: float):
        """Record an interaction between a user and content"""
        if user_id not in self.user_content_matrix:
            self.user_content_matrix[user_id] = {}
        self.user_content_matrix[user_id][content_id] = interaction_strength
    
    def get_recommendations(self, user_id: str, user_profile: Dict[str, Any], top_k: int = 5) -> List[RecommendationScore]:
        """Get collaborative filtering recommendations for a user"""
        # Ensure user vector exists
        if user_id not in self.user_vectors:
            self.add_user(user_id, user_profile)
        
        user_vec = self.user_vectors[user_id]
        
        # Calculate recommendations
        scores = []
        for content_id, content_vec in self.content_vectors.items():
            # Calculate direct user-content similarity
            direct_score = cosine_similarity(
                user_vec.reshape(1, -1),
                content_vec.reshape(1, -1)
            )[0][0]
            
            # Find similar users who interacted with this content
            similar_user_scores = []
            for other_id, other_vec in self.user_vectors.items():
                if other_id != user_id:
                    user_sim = cosine_similarity(
                        user_vec.reshape(1, -1),
                        other_vec.reshape(1, -1)
                    )[0][0]
                    
                    if content_id in self.user_content_matrix.get(other_id, {}):
                        interaction = self.user_content_matrix[other_id][content_id]
                        similar_user_scores.append(user_sim * interaction)
            
            # Combine scores
            collaborative_score = np.mean(similar_user_scores) if similar_user_scores else 0.5
            final_score = 0.7 * direct_score + 0.3 * collaborative_score
            
            scores.append(RecommendationScore(
                content_id=content_id,
                score=float(final_score),
                relevance_score=float(direct_score),
                collaborative_score=float(collaborative_score),
                timestamp=datetime.now().timestamp()
            ))
        
        # Sort and return top-k recommendations
        scores.sort(key=lambda x: x.score, reverse=True)
        return scores[:top_k]
    
    def process(self, request: Dict[str, Any]) -> AlgorithmResponse:
        """Process a recommendation request"""
        user_id = request.get('user_id')
        user_profile = request.get('user_profile', {})
        
        if not user_id:
            raise ValueError("user_id is required")
        
        recommendations = self.get_recommendations(user_id, user_profile)
        
        return AlgorithmResponse(
            algorithm_id='collaborative_filtering_v1',
            timestamp=datetime.now().timestamp(),
            results=recommendations
        ) 