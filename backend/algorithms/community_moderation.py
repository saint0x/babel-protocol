"""
Community Moderation Algorithm

This module implements community-driven content moderation using
sentiment analysis, spam detection, and content quality assessment.
"""

import time
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

from .base import BaseAlgorithm, AlgorithmResponse

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)

class ModerationResult(BaseModel):
    """Moderation result model"""
    content_id: str
    flags: List[str]
    spam_score: float
    quality_score: float
    sentiment_score: float
    action_needed: bool
    timestamp: float

class CommunityModerationSystem(BaseAlgorithm):
    """Community moderation system implementation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # Spam detection patterns
        self.spam_patterns = [
            r'\b(buy|sell|discount|offer|price|deal|free|win|click)\b',
            r'https?://\S+',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b(urgent|limited time|act now|don\'t wait)\b',
            r'[!?]{2,}',
            r'[A-Z]{4,}'
        ]
        
        # Quality assessment factors
        self.quality_factors = {
            'length': 0.3,
            'complexity': 0.2,
            'formatting': 0.2,
            'engagement': 0.3
        }
        
        # Action thresholds
        self.spam_threshold = 0.7
        self.quality_threshold = 0.3
        self.sentiment_threshold = -0.6
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        required_fields = {'content_id', 'text', 'analysis'}
        return all(field in data for field in required_fields)
    
    def process(self, data: Dict[str, Any]) -> AlgorithmResponse:
        """Process content and return moderation results"""
        # Check cache first
        cache_key = f"moderation:{data['content_id']}"
        cached_result = self.get_cache(cache_key)
        if cached_result:
            return AlgorithmResponse.parse_raw(cached_result)
        
        text = data['text']
        analysis = data['analysis']
        metadata = data.get('metadata', {})
        
        # Calculate scores
        spam_score = self.check_spam_score(text)
        quality_score = self._assess_quality(text, analysis, metadata)
        sentiment_score = self._analyze_sentiment(text)
        
        # Determine flags
        flags = self._determine_flags(
            text,
            spam_score,
            quality_score,
            sentiment_score,
            metadata.get('flags', [])
        )
        
        # Determine if action is needed
        action_needed = self._needs_action(
            spam_score,
            quality_score,
            sentiment_score,
            flags
        )
        
        result = ModerationResult(
            content_id=data['content_id'],
            flags=flags,
            spam_score=spam_score,
            quality_score=quality_score,
            sentiment_score=sentiment_score,
            action_needed=action_needed,
            timestamp=time.time()
        )
        
        response = AlgorithmResponse(
            algorithm_id='community_moderation_v1',
            timestamp=time.time(),
            results=[result.dict()],
            metrics=self.get_metrics().dict()
        )
        
        # Cache results
        self.set_cache(cache_key, response.json())
        
        return response
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        # Split on whitespace and punctuation
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in self.stop_words]
    
    def check_spam_score(self, text: str) -> float:
        """Calculate spam probability score"""
        text_lower = text.lower()
        spam_indicators = 0
        total_patterns = len(self.spam_patterns)
        
        # Check against spam patterns
        for pattern in self.spam_patterns:
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                spam_indicators += min(1.0, matches / 3)  # Cap multiple matches
        
        # Additional spam indicators
        words = self._tokenize(text_lower)
        
        # Check for repetitive words
        word_freq = {}
        for word in words:
            if word not in self.stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        max_word_freq = max(word_freq.values()) if word_freq else 0
        if max_word_freq > 3:
            spam_indicators += min(1.0, (max_word_freq - 3) / 5)
        
        # Check for excessive punctuation
        if text.count('!') > 3 or text.count('?') > 3:
            spam_indicators += 0.5
        
        # Normalize score
        return min(1.0, spam_indicators / (total_patterns + 2))
    
    def _assess_quality(self, text: str, analysis: Dict[str, Any],
                       metadata: Dict[str, Any]) -> float:
        """Assess content quality"""
        scores = {}
        
        # Length score
        text_length = len(text.split())
        scores['length'] = min(1.0, text_length / 500)  # Normalize to 500 words
        
        # Complexity score
        complexity = analysis.get('semantics', {}).get('complexity_score', 0.5)
        scores['complexity'] = complexity
        
        # Formatting score
        formatting_score = self._assess_formatting(text)
        scores['formatting'] = formatting_score
        
        # Engagement potential score
        engagement_score = self._assess_engagement_potential(text, analysis)
        scores['engagement'] = engagement_score
        
        # Calculate weighted average
        final_score = sum(
            self.quality_factors[factor] * scores[factor]
            for factor in self.quality_factors
        )
        
        return final_score
    
    def _assess_formatting(self, text: str) -> float:
        """Assess text formatting quality"""
        score = 1.0
        
        # Check for proper capitalization
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if sentences:
            properly_capitalized = sum(
                1 for s in sentences if s[0].isupper()
            ) / len(sentences)
            score *= 0.5 + 0.5 * properly_capitalized
        
        # Check for paragraph breaks
        if len(text) > 200 and text.count('\n\n') == 0:
            score *= 0.8
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if caps_ratio > 0.3:
            score *= 0.7
        
        return score
    
    def _assess_engagement_potential(self, text: str, analysis: Dict[str, Any]) -> float:
        """Assess potential for user engagement"""
        score = 0.0
        
        # Check for questions (encourages discussion)
        question_count = text.count('?')
        score += min(0.3, question_count * 0.1)
        
        # Check for evidence/citations
        evidence_count = analysis.get('evidence', {}).get('count', 0)
        score += min(0.3, evidence_count * 0.1)
        
        # Check for balanced sentiment
        sentiment = analysis.get('semantics', {}).get('sentiment', {})
        if sentiment:
            # Prefer balanced or slightly positive content
            compound = sentiment.get('compound', 0)
            score += 0.4 * (1.0 - abs(compound - 0.2))
        
        return score
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze text sentiment"""
        sentiment = self.sentiment_analyzer.polarity_scores(text)
        return sentiment['compound']
    
    def _determine_flags(self, text: str, spam_score: float,
                        quality_score: float, sentiment_score: float,
                        existing_flags: List[str]) -> List[str]:
        """Determine content flags"""
        flags = list(existing_flags)  # Start with existing flags
        
        # Check spam
        if spam_score > self.spam_threshold:
            flags.append('potential_spam')
        
        # Check quality
        if quality_score < self.quality_threshold:
            flags.append('low_quality')
        
        # Check sentiment
        if sentiment_score < self.sentiment_threshold:
            flags.append('negative_sentiment')
        
        # Check for sensitive content
        sensitive_patterns = [
            r'\b(password|secret|private|confidential)\b',
            r'\b(wallet|key|seed|phrase)\b'
        ]
        for pattern in sensitive_patterns:
            if re.search(pattern, text.lower()):
                flags.append('sensitive_content')
                break
        
        return list(set(flags))  # Remove duplicates
    
    def _needs_action(self, spam_score: float, quality_score: float,
                     sentiment_score: float, flags: List[str]) -> bool:
        """Determine if moderator action is needed"""
        return any([
            spam_score > self.spam_threshold,
            quality_score < self.quality_threshold,
            sentiment_score < self.sentiment_threshold,
            'sensitive_content' in flags,
            len(flags) >= 2  # Multiple flags
        ]) 