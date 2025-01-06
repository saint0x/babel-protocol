"""
Content Analysis Algorithm for Babel Protocol

This algorithm implements sophisticated content analysis capabilities to understand, categorize,
and evaluate content quality while maintaining the platform's commitment to free expression
and community-driven truth determination.

Core Philosophy:
- Content understanding over content control
- Context-aware analysis
- Evidence-based quality assessment
- Narrative pattern recognition
- Community perspective integration
"""

from typing import Dict, List, Optional, Any, Union
import json
import nltk
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import PunktSentenceTokenizer, TreebankWordTokenizer
from pydantic import BaseModel
from transformers import pipeline

from .base import BabelAlgorithm

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

class ContentMetadata(BaseModel):
    """Content metadata model"""
    content_id: str
    text: str
    metadata: Dict[str, Any]
    analysis: Dict[str, Any]
    context_references: List[str]
    evidence_count: int

class ContentAnalysis(BabelAlgorithm):
    """Content Analysis implementation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize NLP components
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.sentence_tokenizer = PunktSentenceTokenizer()
        self.word_tokenizer = TreebankWordTokenizer()
        
        # Initialize transformers
        self.zero_shot = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn"
        )
        
        # Topic categories for classification
        self.topic_categories = [
            "technology", "science", "politics", "economics",
            "culture", "health", "environment", "education",
            "society", "philosophy"
        ]
        
        # Evidence quality markers
        self.evidence_markers = [
            "according to", "research shows", "study finds",
            "evidence suggests", "data indicates", "experts say",
            "analysis reveals", "investigation shows"
        ]

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        required_fields = {'content_id', 'text'}
        return all(field in data for field in required_fields)

    def process(self, data: Dict[str, Any]) -> ContentMetadata:
        """Process content and return analysis results"""
        # Check cache first
        cache_key = f"analysis:{data['content_id']}"
        cached_result = self.get_cache(cache_key)
        if cached_result:
            return ContentMetadata.parse_raw(cached_result)

        # Initialize metadata
        metadata = ContentMetadata(
            content_id=data['content_id'],
            text=data['text'],
            metadata=data.get('metadata', {}),
            analysis={},
            context_references=[],
            evidence_count=0
        )

        # Perform analysis
        try:
            # Basic text analysis
            text_properties = self._analyze_text_properties(data['text'])
            metadata.analysis['text_properties'] = text_properties

            # Semantic analysis
            semantics = self._analyze_semantics(data['text'])
            metadata.analysis['semantics'] = semantics

            # Topic classification
            topics = self._classify_topics(data['text'])
            metadata.analysis['topics'] = topics

            # Evidence analysis
            evidence = self._analyze_evidence_markers(data['text'])
            metadata.analysis['evidence'] = evidence
            metadata.evidence_count = evidence['count']

            # Context references
            context = self._extract_context_references(data['text'])
            metadata.context_references = context['references']
            metadata.analysis['context'] = context

            # Generate summary
            if len(data['text']) > 100:  # Only summarize longer texts
                summary = self._generate_summary(data['text'])
                metadata.analysis['summary'] = summary

        except Exception as e:
            self.log_error(e, {'content_id': data['content_id']})
            raise

        # Cache results
        self.set_cache(cache_key, metadata.json())
        
        return metadata

    def _analyze_text_properties(self, text: str) -> Dict[str, Any]:
        """Analyze basic text properties"""
        sentences = self.sentence_tokenizer.tokenize(text)
        words = self.word_tokenizer.tokenize(text.lower())
        
        return {
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': len(words) / max(1, len(sentences)),
            'unique_words': len(set(words)),
            'vocabulary_richness': len(set(words)) / max(1, len(words))
        }

    def _analyze_semantics(self, text: str) -> Dict[str, Any]:
        """Analyze semantic properties of text"""
        # Sentiment analysis
        sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Complexity analysis
        complexity_score = self._calculate_complexity(text)
        
        # Entity extraction
        try:
            entities = self._extract_entities(text)
        except Exception as e:
            self.log_warning(f"Entity extraction failed: {str(e)}")
            entities = []
        
        return {
            'sentiment': sentiment_scores,
            'complexity_score': complexity_score,
            'entities': entities
        }

    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        # Tokenize text
        words = self.word_tokenizer.tokenize(text.lower())
        sentences = self.sentence_tokenizer.tokenize(text)
        
        # Calculate metrics
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        unique_ratio = len(set(words)) / len(words) if words else 0
        
        # Combine metrics into complexity score
        complexity = (
            0.3 * avg_word_length +
            0.4 * avg_sentence_length +
            0.3 * unique_ratio
        )
        
        return min(1.0, complexity / 10.0)  # Normalize to 0-1 range

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        words = self.word_tokenizer.tokenize(text)
        pos_tags = nltk.pos_tag(words)
        chunks = nltk.ne_chunk(pos_tags)
        
        entities = []
        for chunk in chunks:
            if hasattr(chunk, 'label'):
                entity = {
                    'text': ' '.join(c[0] for c in chunk),
                    'type': chunk.label(),
                    'confidence': 0.8  # Placeholder confidence score
                }
                entities.append(entity)
        
        return entities

    def _classify_topics(self, text: str) -> Dict[str, float]:
        """Classify text into predefined topics"""
        # Use zero-shot classification for topics
        result = self.zero_shot(
            text,
            candidate_labels=self.topic_categories,
            multi_label=True
        )
        
        # Convert to dictionary format
        topics = dict(zip(result['labels'], result['scores']))
        
        return topics

    def _analyze_evidence_markers(self, text: str) -> Dict[str, Any]:
        """Analyze evidence and citation patterns"""
        text_lower = text.lower()
        evidence_count = sum(1 for marker in self.evidence_markers if marker in text_lower)
        
        # Calculate evidence strength score
        words = self.word_tokenizer.tokenize(text_lower)
        word_count = len(words)
        strength_score = min(1.0, evidence_count / (word_count / 100))  # Normalize by text length
        
        return {
            'count': evidence_count,
            'strength_score': strength_score,
            'markers_found': [m for m in self.evidence_markers if m in text_lower]
        }

    def _extract_context_references(self, text: str) -> Dict[str, Any]:
        """Extract context references and citations"""
        # Simple pattern matching for now
        words = self.word_tokenizer.tokenize(text.lower())
        sentences = self.sentence_tokenizer.tokenize(text)
        
        references = []
        for sentence in sentences:
            if any(marker in sentence.lower() for marker in self.evidence_markers):
                references.append(sentence)
        
        return {
            'references': references,
            'reference_count': len(references)
        }

    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate text summary"""
        # Use BART for summarization
        summary = self.summarizer(
            text,
            max_length=130,
            min_length=30,
            do_sample=False
        )[0]['summary_text']
        
        return {
            'summary_text': summary,
            'length': len(self.word_tokenizer.tokenize(summary))
        } 