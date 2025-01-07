"""
Feedback Loop Optimization Algorithm

This module implements feedback-based optimization for content recommendations.
It analyzes user engagement patterns and adjusts recommendation weights accordingly.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel

from .base import BaseAlgorithm, AlgorithmResponse, AlgorithmMetrics

class FeedbackData(BaseModel):
    """Feedback data model"""
    feedback_id: str
    algorithm_id: str
    feedback_type: str
    feedback_data: Dict[str, Any]
    timestamp: Optional[float] = None

class OptimizationResult(BaseModel):
    """Optimization result model"""
    user_id: str
    algorithm_id: str
    optimizations: Dict[str, float]
    confidence: float
    timestamp: float

class FeedbackLoopOptimizer(BaseAlgorithm):
    """Feedback loop optimization implementation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback_history: Dict[str, List[FeedbackData]] = {}
        self.optimization_weights = {
            'engagement_score': 0.4,
            'read_time': 0.3,
            'scroll_depth': 0.3
        }
        
        # Learning rate for weight adjustments
        self.learning_rate = 0.1
        
        # Minimum confidence threshold
        self.min_confidence = 0.6
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        if 'feedback_id' in data:
            required_fields = {'feedback_id', 'algorithm_id', 'feedback_type', 'feedback_data'}
        else:
            required_fields = {'user_id', 'feedback_history'}
        return all(field in data for field in required_fields)
    
    def record_user_feedback(self, feedback_id: str, algorithm_id: str, 
                           feedback_type: str, feedback_data: Dict[str, Any]) -> None:
        """Record user feedback for optimization"""
        feedback = FeedbackData(
            feedback_id=feedback_id,
            algorithm_id=algorithm_id,
            feedback_type=feedback_type,
            feedback_data=feedback_data,
            timestamp=time.time()
        )
        
        user_id = feedback_data.get('user_id', 'default')
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = []
        self.feedback_history[user_id].append(feedback)
    
    def process(self, data: Dict[str, Any]) -> AlgorithmResponse:
        """Process feedback data and optimize recommendations"""
        if 'feedback_id' in data:
            # Record new feedback
            self.record_user_feedback(
                data['feedback_id'],
                data['algorithm_id'],
                data['feedback_type'],
                data['feedback_data']
            )
            return AlgorithmResponse(
                algorithm_id='feedback_optimization_v1',
                timestamp=time.time(),
                results=[{'status': 'feedback_recorded'}],
                metrics=self.get_metrics().dict()
            )
        
        # Optimize based on feedback history
        user_id = data['user_id']
        feedback_history = data['feedback_history']
        
        # Calculate optimization weights
        optimizations = self._calculate_optimizations(user_id, feedback_history)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(feedback_history)
        
        result = OptimizationResult(
            user_id=user_id,
            algorithm_id='feedback_optimization_v1',
            optimizations=optimizations,
            confidence=confidence,
            timestamp=time.time()
        )
        
        return AlgorithmResponse(
            algorithm_id='feedback_optimization_v1',
            timestamp=time.time(),
            results=[result.dict()],
            metrics=self.get_metrics().dict()
        )
    
    def _calculate_optimizations(self, user_id: str, feedback_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate optimization weights based on feedback history"""
        if not feedback_history:
            return self.optimization_weights.copy()
        
        # Initialize weight adjustments
        weight_adjustments = {k: 0.0 for k in self.optimization_weights}
        total_feedback = len(feedback_history)
        
        for feedback in feedback_history:
            metrics = feedback.get('metrics', {})
            
            # Calculate engagement impact
            if 'engagement_score' in metrics:
                weight_adjustments['engagement_score'] += (
                    metrics['engagement_score'] - 0.5
                ) * self.learning_rate
            
            # Calculate read time impact
            if 'read_time' in metrics:
                normalized_read_time = min(metrics['read_time'] / 300, 1.0)  # Normalize to 5 minutes
                weight_adjustments['read_time'] += (
                    normalized_read_time - 0.5
                ) * self.learning_rate
            
            # Calculate scroll depth impact
            if 'scroll_depth' in metrics:
                weight_adjustments['scroll_depth'] += (
                    metrics['scroll_depth'] - 0.5
                ) * self.learning_rate
        
        # Apply adjustments and normalize
        optimized_weights = {}
        for key in self.optimization_weights:
            optimized_weights[key] = max(0.1, min(0.8, 
                self.optimization_weights[key] + weight_adjustments[key] / total_feedback
            ))
        
        # Normalize to sum to 1
        total_weight = sum(optimized_weights.values())
        return {k: v/total_weight for k, v in optimized_weights.items()}
    
    def _calculate_confidence(self, feedback_history: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for optimizations"""
        if not feedback_history:
            return self.min_confidence
        
        # Factors affecting confidence:
        # 1. Number of feedback points
        # 2. Consistency of feedback
        # 3. Recency of feedback
        
        num_feedback = len(feedback_history)
        confidence_base = min(0.8, 0.4 + 0.1 * num_feedback)  # Increases with more feedback
        
        # Calculate consistency
        if num_feedback > 1:
            engagement_scores = [
                f.get('metrics', {}).get('engagement_score', 0.5) 
                for f in feedback_history
            ]
            variance = sum((s - sum(engagement_scores)/num_feedback)**2 
                         for s in engagement_scores) / num_feedback
            consistency_factor = max(0.5, 1.0 - variance)
        else:
            consistency_factor = 0.7
        
        # Calculate recency
        current_time = time.time()
        avg_age = sum(
            current_time - f.get('metrics', {}).get('timestamp', current_time)
            for f in feedback_history
        ) / num_feedback
        recency_factor = max(0.5, min(1.0, 7*24*3600 / max(1, avg_age)))  # Decay over a week
        
        confidence = confidence_base * consistency_factor * recency_factor
        return max(self.min_confidence, min(0.95, confidence))  # Bound between min and 0.95 