"""
Direct Algorithm Test Runner with SQLite Integration
"""
import os
os.environ['BABEL_TEST_MODE'] = '1'  # Set test mode before any imports

import json
import sys
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Set up NLTK data path and download required data silently
import nltk
nltk.data.path = [str(Path.home() / 'nltk_data')]

# Download all required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('vader_lexicon', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from algorithms.content_analysis import ContentAnalysis
from algorithms.recommendation import ContentRecommendationSystem
from algorithms.feedback_loop_optimization import FeedbackLoopOptimizer
from algorithms.community_moderation import CommunityModerationSystem
from algorithms.engagement_analytics import EngagementAnalytics
from algorithms.temporal_considerations import TemporalConsiderations
from algorithms.source_of_truth_consensus import SourceOfTruthConsensus

# Import test database configuration
from algorithms.test.data.db_config import TestDatabaseConfig
from algorithms.test.data.init_db import init_test_db

class TestMetrics:
    """Track performance metrics for tests"""
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'content_analysis': {'success': 0, 'failed': 0, 'time': 0},
            'recommendations': {'success': 0, 'failed': 0, 'time': 0},
            'optimization': {'success': 0, 'failed': 0, 'time': 0},
            'moderation': {'success': 0, 'failed': 0, 'time': 0},
            'engagement': {'success': 0, 'failed': 0, 'time': 0},
            'temporal': {'success': 0, 'failed': 0, 'time': 0},
            'consensus': {'success': 0, 'failed': 0, 'time': 0}
        }
    
    def record_success(self, algorithm: str, execution_time: float):
        self.metrics[algorithm]['success'] += 1
        self.metrics[algorithm]['time'] += execution_time
    
    def record_failure(self, algorithm: str, execution_time: float):
        self.metrics[algorithm]['failed'] += 1
        self.metrics[algorithm]['time'] += execution_time
    
    def get_summary(self) -> Dict[str, Any]:
        total_time = time.time() - self.start_time
        return {
            'total_execution_time': total_time,
            'algorithm_metrics': self.metrics
        }

# Load test data
def load_test_data() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load test users and content from JSON files"""
    data_dir = Path(__file__).parent
    
    with open(data_dir / 'users.json') as f:
        users = json.load(f)
    
    with open(data_dir / 'content.json') as f:
        content = json.load(f)
    
    return users, content

def test_content_analysis(content: Dict[str, Any], metrics: TestMetrics) -> Dict[str, Any]:
    """Test content analysis with various content types"""
    analyzer = ContentAnalysis(db_config=TestDatabaseConfig())
    results = {}
    
    print("\n🔍 Testing Content Analysis:")
    
    for content_id, content_data in content.items():
        start_time = time.time()
        try:
            result = analyzer.process({
                'content_id': content_data['content_id'],
                'text': content_data['text'],
                'metadata': {
                    'title': content_data['title'],
                    'tags': content_data['tags'],
                    'complexity_level': content_data.get('complexity_level', 0.5)
                }
            })
            
            print(f"  ✅ Analyzed {content_data['title']}")
            results[content_id] = result.results[0]
            metrics.record_success('content_analysis', time.time() - start_time)
            
        except Exception as e:
            print(f"  ❌ Failed to analyze {content_data['title']}: {str(e)}")
            metrics.record_failure('content_analysis', time.time() - start_time)
            raise
    
    return results

def test_recommendations(users_data: Dict[str, Any], content_results: Dict[str, Any], metrics: TestMetrics) -> Dict[str, Any]:
    """Test recommendation system with various user profiles and content types"""
    recommender = ContentRecommendationSystem(db_config=TestDatabaseConfig())
    results = {}
    
    print("\n🎯 Testing Recommendations:")
    
    # Add content to recommendation system
    for content_id, content in content_results.items():
        recommender.add_content(
            content_id=content['content_id'],
            text=content['text'],
            timestamp=datetime.now().timestamp(),
            authenticity_score=content['analysis'].get('evidence', {}).get('strength_score', 0.5),
            metadata={
                'complexity_level': content.get('complexity_level', 0.5),
                'tags': content.get('tags', [])
            }
        )
    
    # Get recommendations for each user
    for user_id, user in users_data.items():
        start_time = time.time()
        try:
            # Get personalized recommendations
            recommendations = recommender.process({
                'user_id': user['user_id'],
                'user_profile': {
                    'interests': user['interests'],
                    'expertise_areas': user['expertise_areas'],
                    'engagement_patterns': user['engagement_patterns']
                }
            })
            
            print(f"  ✅ Generated recommendations for {user['name']}")
            results[user['user_id']] = recommendations.results  # Use user_id from user data
            metrics.record_success('recommendations', time.time() - start_time)
            
        except Exception as e:
            print(f"  ❌ Failed to generate recommendations for {user['name']}: {str(e)}")
            metrics.record_failure('recommendations', time.time() - start_time)
            raise
    
    return results

def test_feedback_optimization(users_data: Dict[str, Any], recommendations: Dict[str, Any], metrics: TestMetrics) -> Dict[str, Any]:
    """Test feedback loop optimization with various engagement patterns"""
    optimizer = FeedbackLoopOptimizer(db_config=TestDatabaseConfig())
    results = {}
    
    print("\n💭 Testing Feedback Optimization:")
    
    # Simulate different types of feedback
    feedback_patterns = [
        {'engagement_score': 0.9, 'read_time': 300, 'scroll_depth': 1.0},  # Highly engaged
        {'engagement_score': 0.5, 'read_time': 120, 'scroll_depth': 0.7},  # Moderately engaged
        {'engagement_score': 0.2, 'read_time': 30, 'scroll_depth': 0.3}    # Poorly engaged
    ]
    
    for user_id, user_data in users_data.items():
        start_time = time.time()
        try:
            user_recs = recommendations[user_data['user_id']]  # Use user_id from user data
            user_feedback = []
            
            # Generate feedback for each recommendation
            for i, rec in enumerate(user_recs):
                feedback_pattern = feedback_patterns[i % len(feedback_patterns)]
                feedback_id = f"{user_data['user_id']}_{rec['content_id']}_{datetime.now().timestamp()}"
                
                optimizer.record_user_feedback(
                    feedback_id=feedback_id,
                    algorithm_id='recommendation_v1',
                    feedback_type='engagement',
                    feedback_data={
                        **feedback_pattern,
                        'user_profile': user_data['engagement_patterns']
                    }
                )
                user_feedback.append({
                    'feedback_id': feedback_id,
                    'content_id': rec['content_id'],
                    'metrics': feedback_pattern
                })
            
            # Get optimization results
            optimization_result = optimizer.process({
                'user_id': user_data['user_id'],
                'feedback_history': user_feedback
            })
            
            results[user_id] = optimization_result.results[0]
            metrics.record_success('optimization', time.time() - start_time)
            print(f"  ✅ Optimized recommendations for {user_data['name']}")
            
        except Exception as e:
            print(f"  ❌ Failed optimization for {user_id}: {str(e)}")
            metrics.record_failure('optimization', time.time() - start_time)
            raise
    
    return results

def test_moderation(content_results: Dict[str, Any], metrics: TestMetrics) -> Dict[str, Any]:
    """Test community moderation system with various content types"""
    moderator = CommunityModerationSystem(db_config=TestDatabaseConfig())
    results = {}
    
    print("\n🛡️ Testing Community Moderation:")
    
    for content_id, content in content_results.items():
        start_time = time.time()
        try:
            # Test content moderation
            moderation_result = moderator.process({
                'content_id': content['content_id'],
                'text': content['text'],
                'analysis': content['analysis'],
                'metadata': {
                    'flags': content.get('flags', []),
                    'tags': content.get('tags', [])
                }
            })
            
            results[content_id] = moderation_result.results[0]
            metrics.record_success('moderation', time.time() - start_time)
            print(f"  ✅ Moderated: {content_id}")
            
            # Test spam detection specifically for spam content
            if 'potential_spam' in content.get('flags', []):
                spam_score = moderator.check_spam_score(content['text'])
                print(f"  ℹ️ Spam score for {content_id}: {spam_score:.2f}")
            
        except Exception as e:
            print(f"  ❌ Failed moderation for {content_id}: {str(e)}")
            metrics.record_failure('moderation', time.time() - start_time)
            raise
    
    return results

def test_engagement_analytics(users_data: Dict[str, Any], content_results: Dict[str, Any], metrics: TestMetrics) -> Dict[str, Any]:
    """Test engagement analytics with various user interactions"""
    analyzer = EngagementAnalytics(db_config=TestDatabaseConfig())
    results = {}
    
    print("\n📊 Testing Engagement Analytics:")
    
    # Simulate user engagement data
    engagement_data = []
    current_time = time.time()
    for user_id, user in users_data.items():
        for content_id, content in list(content_results.items())[:3]:  # Test with first 3 contents
            engagement_data.append({
                'user_id': user_id,
                'content_id': content_id,
                'session_duration': user['engagement_patterns']['session_duration'],
                'scroll_depth': random.uniform(0.3, 1.0),
                'time_of_day': str(random.randint(0, 23)),  # Random hour
                'interaction_type': random.choice(['view', 'like', 'share', 'comment']),
                'timestamp': current_time - random.uniform(0, 24 * 60 * 60)  # Random time in last 24h
            })
    
    start_time = time.time()
    try:
        # Analyze engagement patterns
        engagement_results = analyzer.process({
            'engagement_data': engagement_data,
            'time_window': 24 * 60 * 60  # 24 hours
        })
        
        results['engagement_patterns'] = engagement_results.results[0]
        metrics.record_success('engagement', time.time() - start_time)
        print("  ✅ Analyzed engagement patterns")
        
    except Exception as e:
        print(f"  ❌ Failed to analyze engagement: {str(e)}")
        metrics.record_failure('engagement', time.time() - start_time)
        raise
    
    return results

def test_temporal_considerations(content_results: Dict[str, Any], metrics: TestMetrics) -> Dict[str, Any]:
    """Test temporal considerations for content relevance"""
    temporal = TemporalConsiderations(db_config=TestDatabaseConfig())
    results = {}
    
    print("\n⏰ Testing Temporal Considerations:")
    
    # Create temporal test cases
    now = datetime.now()
    temporal_cases = [
        {'timestamp': now.timestamp(), 'label': 'current'},
        {'timestamp': (now - timedelta(hours=12)).timestamp(), 'label': 'recent'},
        {'timestamp': (now - timedelta(days=7)).timestamp(), 'label': 'week_old'},
        {'timestamp': (now - timedelta(days=30)).timestamp(), 'label': 'month_old'}
    ]
    
    start_time = time.time()
    try:
        # Test temporal relevance for different time periods
        for case in temporal_cases:
            content_data = []
            for content in content_results.values():
                content_data.append({
                    'content_id': content['content_id'],
                    'timestamp': case['timestamp'],
                    'type': content.get('type', 'discussion'),
                    'engagement_metrics': {
                        'level': random.uniform(0.3, 0.9),
                        'recent_views': random.randint(10, 100),
                        'total_views': random.randint(100, 1000),
                        'recent_interactions': random.randint(5, 50),
                        'total_interactions': random.randint(50, 500)
                    },
                    'quality_metrics': {
                        'score': content.get('analysis', {}).get('quality_score', 0.5)
                    }
                })
            
            temporal_scores = temporal.process({
                'content_data': content_data,
                'reference_time': now.timestamp()
            })
            
            results[case['label']] = temporal_scores.results
        
        metrics.record_success('temporal', time.time() - start_time)
        print("  ✅ Analyzed temporal relevance")
        
    except Exception as e:
        print(f"  ❌ Failed temporal analysis: {str(e)}")
        metrics.record_failure('temporal', time.time() - start_time)
        raise
    
    return results

def test_source_consensus(content_results: Dict[str, Any], metrics: TestMetrics) -> Dict[str, Any]:
    """Test source of truth consensus mechanism"""
    consensus = SourceOfTruthConsensus(db_config=TestDatabaseConfig())
    results = {}
    
    print("\n🤝 Testing Source Consensus:")
    
    # Test different consensus scenarios
    test_cases = [
        {
            'content_id': 'technical_consensus',
            'sources': [
                {'source': 'official_docs', 'content': content_results['technical_post']},
                {'source': 'community_wiki', 'content': content_results['educational_post']}
            ]
        },
        {
            'content_id': 'market_consensus',
            'sources': [
                {'source': 'market_data', 'content': content_results['market_analysis']},
                {'source': 'news_update', 'content': content_results['news_post']}
            ]
        }
    ]
    
    start_time = time.time()
    try:
        for case in test_cases:
            consensus_result = consensus.process({
                'content_id': case['content_id'],
                'sources': case['sources']
            })
            
            results[case['content_id']] = consensus_result.results[0]
            print(f"  ✅ Analyzed consensus for {case['content_id']}")
        
        metrics.record_success('consensus', time.time() - start_time)
        
    except Exception as e:
        print(f"  ❌ Failed consensus analysis: {str(e)}")
        metrics.record_failure('consensus', time.time() - start_time)
            raise
    
    return results

def main():
    """Run all algorithm tests with comprehensive metrics"""
    print("🚀 Starting Comprehensive Algorithm Tests\n")
    
    metrics = TestMetrics()
    
    try:
        # Initialize test database
        init_test_db()
        
        # Load test data
        users, content = load_test_data()
        
        # Run tests for each algorithm
        content_results = test_content_analysis(content, metrics)
        recommendation_results = test_recommendations(users, content_results, metrics)
        optimization_results = test_feedback_optimization(users, recommendation_results, metrics)
        moderation_results = test_moderation(content_results, metrics)
        engagement_results = test_engagement_analytics(users, content_results, metrics)
        temporal_results = test_temporal_considerations(content_results, metrics)
        consensus_results = test_source_consensus(content_results, metrics)
        
        # Save results
        results = {
            'content_analysis': content_results,
            'recommendations': recommendation_results,
            'optimization': optimization_results,
            'moderation': moderation_results,
            'engagement': engagement_results,
            'temporal': temporal_results,
            'consensus': consensus_results,
            'metrics': metrics.get_summary()
        }
        
        with open(Path(__file__).parent / 'test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n✨ Tests completed successfully!")
        print("📁 Test Metrics Summary:")
        for algo, stats in metrics.metrics.items():
            success_rate = stats['success'] / (stats['success'] + stats['failed']) * 100 if (stats['success'] + stats['failed']) > 0 else 0
            avg_time = stats['time'] / (stats['success'] + stats['failed']) if (stats['success'] + stats['failed']) > 0 else 0
            print(f"  - {algo}: {success_rate:.1f}% success rate, {avg_time:.3f}s avg execution time")
        print("\n📁 Detailed results saved in test_results.json")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
