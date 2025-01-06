"""
Direct Algorithm Test Runner
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from algorithms.content_analysis import ContentAnalysis
from algorithms.recommendation import ContentRecommendationSystem
from algorithms.feedback_loop_optimization import FeedbackLoopOptimizer

def load_test_data():
    """Load test users and content"""
    data_dir = Path(__file__).parent
    
    with open(data_dir / "users.json") as f:
        users = json.load(f)
    
    with open(data_dir / "content.json") as f:
        content = json.load(f)
        
    return users, content

def test_content_analysis(content_data):
    """Test content analysis algorithm"""
    analyzer = ContentAnalysis()
    results = {}
    
    print("🔍 Testing Content Analysis:")
    for content_id, content in content_data.items():
        try:
            result = analyzer.process({
                'content_id': content['content_id'],
                'text': content['text']
            })
            print(f"  ✅ Analyzed: {content['title']}")
            results[content_id] = result.dict()
        except Exception as e:
            print(f"  ❌ Failed to analyze {content_id}: {str(e)}")
            raise  # Re-raise to see full stack trace
    
    return results

def test_recommendations(users_data, content_results):
    """Test recommendation algorithm"""
    recommender = ContentRecommendationSystem()
    results = {}
    
    print("\n🎯 Testing Recommendations:")
    
    # Add content to recommendation system
    for content_id, content in content_results.items():
        recommender.add_content(
            content_id=content['content_id'],
            text=content['text'],
            timestamp=datetime.now().timestamp(),
            authenticity_score=content['analysis'].get('evidence', {}).get('strength_score', 0.5)
        )
    
    # Get recommendations for each user
    for user_type, user in users_data.items():
        try:
            recommendations = recommender.recommend_content(user['user_id'])
            print(f"  ✅ Generated recommendations for {user['name']}")
            results[user['user_id']] = recommendations
        except Exception as e:
            print(f"  ❌ Failed to generate recommendations for {user_type}: {str(e)}")
            raise  # Re-raise to see full stack trace
    
    return results

def test_feedback_optimization(users_data, recommendations):
    """Test feedback loop optimization"""
    optimizer = FeedbackLoopOptimizer()
    results = {}
    
    print("\n💭 Testing Feedback Optimization:")
    
    for user_id, user_recs in recommendations.items():
        try:
            # Simulate feedback for each recommendation
            for rec in user_recs:
                feedback_id = f"{user_id}_{rec['content_id']}_{datetime.now().timestamp()}"
                optimizer.record_user_feedback(
                    feedback_id=feedback_id,
                    algorithm_id='recommendation',
                    feedback_type='engagement',
                    feedback_data={
                        'engagement_score': 0.8,
                        'read_time': 120,
                        'scroll_depth': 0.9
                    }
                )
            print(f"  ✅ Processed feedback for user {user_id}")
            
            # Get optimization status
            results[user_id] = optimizer.get_optimization_status('recommendation')
        except Exception as e:
            print(f"  ❌ Failed to process feedback for {user_id}: {str(e)}")
            raise  # Re-raise to see full stack trace
    
    return results

def main():
    """Run all algorithm tests"""
    print("🚀 Starting Algorithm Tests\n")
    
    try:
        # Load test data
        users, content = load_test_data()
        
        # Run tests
        content_results = test_content_analysis(content)
        recommendation_results = test_recommendations(users, content_results)
        optimization_results = test_feedback_optimization(users, recommendation_results)
        
        # Save results
        results = {
            'content_analysis': content_results,
            'recommendations': recommendation_results,
            'optimization': optimization_results
        }
        
        with open(Path(__file__).parent / 'test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n✨ Tests completed successfully!")
        print("📁 Results saved in test_results.json")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
