"""
Content Recommendation Algorithm

This module implements personalized content recommendations based on user preferences,
content features, and engagement patterns.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel

from .base import BaseAlgorithm, AlgorithmResponse

class RecommendationScore(BaseModel):
    """Recommendation score model"""
    content_id: str
    score: float
    relevance_score: float
    engagement_score: float
    authenticity_score: float
    temporal_score: float

class ContentRecommendationSystem(BaseAlgorithm):
    """Content recommendation system implementation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_store: Dict[str, Dict[str, Any]] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Recommendation weights
        self.weights = {
            'relevance': 0.4,
            'engagement': 0.3,
            'authenticity': 0.2,
            'temporal': 0.1
        }
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        if 'content_id' in data:  # Adding content
            required_fields = {'content_id', 'text', 'timestamp'}
        else:  # Getting recommendations
            required_fields = {'user_id', 'user_profile'}
        return all(field in data for field in required_fields)
    
    def add_content(self, content_id: str, text: str, timestamp: float,
                   authenticity_score: float, metadata: Dict[str, Any]) -> None:
        """Add or update content in the recommendation system"""
        self.content_store[content_id] = {
            'text': text,
            'timestamp': timestamp,
            'authenticity_score': authenticity_score,
            'metadata': metadata
        }
    
    def process(self, data: Dict[str, Any]) -> AlgorithmResponse:
        """Process user profile and return personalized recommendations"""
        try:
            mode = data.get('mode', 'personalized')
            
            if mode == 'similar_content':
                if 'content_id' not in data:
                    raise ValueError("content_id required for similar_content mode")
                    
                # Add content to store if not exists
                if 'text' in data:
                    self.add_content(
                        data['content_id'],
                        data['text'],
                        data.get('timestamp', time.time()),
                        data.get('authenticity_score', 0.5),
                        data.get('metadata', {})
                    )
                
                # Find similar content
                recommendations = self._find_similar_content(data['content_id'])
            else:  # personalized mode
                if 'user_id' not in data or 'user_profile' not in data:
                    raise ValueError("user_id and user_profile required for personalized mode")
                
                # Update user profile
                self.user_profiles[data['user_id']] = data['user_profile']
                
                # Generate personalized recommendations
                recommendations = self._generate_recommendations(data['user_id'])
            
            return AlgorithmResponse(
                algorithm_id='content_recommendation_v1',
                timestamp=time.time(),
                results=recommendations,
                metrics=self.get_metrics().dict()
            )
        except Exception as e:
            return AlgorithmResponse(
                algorithm_id='content_recommendation_v1',
                timestamp=time.time(),
                results=[{
                    'error': str(e),
                    'content_id': data.get('content_id', 'unknown')
                }],
                metrics=self.get_metrics().dict()
            )
    
    def _generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized recommendations for user"""
        if not self.content_store:
            return []
        
        user_profile = self.user_profiles.get(user_id, {})
        current_time = time.time()
        scores = []
        
        for content_id, content in self.content_store.items():
            # Calculate relevance score
            relevance_score = self._calculate_relevance(
                content['text'],
                content['metadata'],
                user_profile.get('interests', []),
                user_profile.get('expertise_areas', [])
            )
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement(
                content_id,
                user_profile.get('engagement_patterns', {})
            )
            
            # Get authenticity score
            authenticity_score = content['authenticity_score']
            
            # Calculate temporal score
            temporal_score = self._calculate_temporal_score(
                content['timestamp'],
                current_time
            )
            
            # Calculate final score
            final_score = (
                self.weights['relevance'] * relevance_score +
                self.weights['engagement'] * engagement_score +
                self.weights['authenticity'] * authenticity_score +
                self.weights['temporal'] * temporal_score
            )
            
            scores.append(RecommendationScore(
                content_id=content_id,
                score=final_score,
                relevance_score=relevance_score,
                engagement_score=engagement_score,
                authenticity_score=authenticity_score,
                temporal_score=temporal_score
            ))
        
        # Sort by score and return top recommendations
        scores.sort(key=lambda x: x.score, reverse=True)
        return [score.dict() for score in scores[:10]]  # Return top 10
    
    def _calculate_relevance(self, text: str, metadata: Dict[str, Any],
                           interests: List[str], expertise_areas: List[str]) -> float:
        """Calculate content relevance based on user interests and expertise"""
        if not interests and not expertise_areas:
            return 0.5  # Default score
        
        try:
            # Preprocess text content
            processed_text = text.lower() if isinstance(text, str) else ""
            processed_metadata = str(metadata).lower()
            
            # Calculate interest match
            interest_match = sum(
                1 for interest in interests
                if interest.lower() in processed_text or
                interest.lower() in processed_metadata
            ) / max(1, len(interests))
            
            # Calculate expertise match
            expertise_match = sum(
                1 for area in expertise_areas
                if area.lower() in processed_text or
                area.lower() in processed_metadata
            ) / max(1, len(expertise_areas))
            
            # Combine scores with weights
            return 0.7 * interest_match + 0.3 * expertise_match
        except (AttributeError, TypeError):
            return 0.5  # Default score if text processing fails
    
    def _calculate_engagement(self, content_id: str, engagement_patterns: Dict[str, Any]) -> float:
        """Calculate predicted engagement score based on user patterns"""
        if not engagement_patterns:
            return 0.5  # Default score
        
        # Get content complexity
        content = self.content_store[content_id]
        content_complexity = content['metadata'].get('complexity_level', 0.5)
        
        # Calculate time-of-day match
        current_hour = datetime.now().hour
        active_hours = engagement_patterns.get('active_hours', [])
        time_match = 1.0 if current_hour in active_hours else 0.5
        
        # Calculate complexity match
        user_complexity_preference = engagement_patterns.get('preferred_complexity', 0.5)
        complexity_match = 1.0 - abs(content_complexity - user_complexity_preference)
        
        # Combine factors
        return 0.6 * complexity_match + 0.4 * time_match
    
    def _calculate_temporal_score(self, content_timestamp: float, current_time: float) -> float:
        """Calculate temporal relevance score"""
        age_hours = (current_time - content_timestamp) / 3600
        
        if age_hours < 24:  # Last 24 hours
            return 1.0
        elif age_hours < 72:  # 1-3 days
            return 0.8
        elif age_hours < 168:  # 3-7 days
            return 0.6
        elif age_hours < 720:  # 7-30 days
            return 0.4
        else:
            return 0.2  # Older than 30 days 
    
    def _find_similar_content(self, content_id: str) -> List[Dict[str, Any]]:
        """Find content similar to the given content_id"""
        if content_id not in self.content_store:
            return []
        
        target_content = self.content_store[content_id]
        scores = []
        
        for other_id, other_content in self.content_store.items():
            if other_id == content_id:
                continue
            
            # Calculate text similarity if text exists
            text_similarity = 0.0
            if isinstance(target_content.get('text', ''), str) and isinstance(other_content.get('text', ''), str):
                text_similarity = self._calculate_text_similarity(
                    target_content['text'],
                    other_content['text']
                )
            
            # Calculate metadata similarity
            metadata_similarity = self._calculate_metadata_similarity(
                target_content.get('metadata', {}),
                other_content.get('metadata', {})
            )
            
            # Calculate final similarity score
            similarity_score = 0.7 * text_similarity + 0.3 * metadata_similarity
            
            scores.append({
                'content_id': other_id,
                'score': similarity_score,
                'similarity_score': similarity_score
            })
        
        # Sort by similarity score
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:10]  # Return top 10 similar items
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        # Convert to sets of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_metadata_similarity(self, metadata1: Dict[str, Any], metadata2: Dict[str, Any]) -> float:
        """Calculate similarity between content metadata"""
        # Extract comparable fields
        fields1 = {str(k): str(v) for k, v in metadata1.items()}
        fields2 = {str(k): str(v) for k, v in metadata2.items()}
        
        # Calculate field overlap
        common_keys = set(fields1.keys()).intersection(fields2.keys())
        if not common_keys:
            return 0.0
        
        # Calculate similarity for each common field
        similarities = []
        for key in common_keys:
            if fields1[key] == fields2[key]:
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return sum(similarities) / len(similarities) 