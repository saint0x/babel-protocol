#!/bin/bash

# Colors and emojis for pretty logging
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Check Python dependencies
check_dependencies() {
    log_info "Checking Python dependencies..."
    
    # Create a temporary Python script to check dependencies
    cat > check_deps.py << EOL
import sys
import pkg_resources

required = [
    'numpy==1.24.3',
    'pandas',
    'scikit-learn',
    'torch',
    'nltk',
    'transformers',
    'spacy',
    'redis',
    'psycopg2-binary',
    'pydantic',
    'python-dotenv',
    'loguru',
    'tqdm'
]

def check_dependencies():
    missing = []
    version_mismatch = []
    
    for package in required:
        try:
            pkg_resources.require(package)
        except pkg_resources.VersionConflict as e:
            version_mismatch.append(str(e))
        except pkg_resources.DistributionNotFound:
            missing.append(package.split('==')[0])
    
    if missing or version_mismatch:
        print("MISSING:" + ",".join(missing))
        print("VERSION_MISMATCH:" + ",".join(version_mismatch))
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    check_dependencies()
EOL

    # Run dependency check
    if python3 check_deps.py > deps_output.txt 2>&1; then
        log_success "All dependencies are satisfied!"
        rm check_deps.py deps_output.txt
        return 0
    else
        local MISSING=$(grep "MISSING:" deps_output.txt | cut -d: -f2)
        local VERSION_MISMATCH=$(grep "VERSION_MISMATCH:" deps_output.txt | cut -d: -f2)
        
        if [ ! -z "$MISSING" ]; then
            log_error "Missing dependencies: $MISSING"
        fi
        if [ ! -z "$VERSION_MISMATCH" ]; then
            log_error "Version conflicts: $VERSION_MISMATCH"
        fi
        
        log_info "Please install missing dependencies and resolve version conflicts using:"
        log_info "pip install -r algorithms/requirements.txt"
        
        rm check_deps.py deps_output.txt
        return 1
    fi
}

# Run dependency check before proceeding
check_dependencies || exit 1

# Test data directory
TEST_DATA_DIR="$(dirname "$0")/data"

# Create test data directory if it doesn't exist
mkdir -p "$TEST_DATA_DIR"

# Create Python test runner
cat > "$TEST_DATA_DIR/test_runner.py" << 'EOL'
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
EOL

# Mock Users with rich backstories and interests
cat > "$TEST_DATA_DIR/users.json" << EOL
{
  "tech_enthusiast": {
    "user_id": "user_001",
    "name": "Alex Chen",
    "bio": "Former Silicon Valley engineer turned crypto researcher. Passionate about decentralized systems and AI.",
    "interests": ["blockchain", "artificial intelligence", "distributed systems", "cryptography", "tech startups"],
    "expertise_areas": ["programming", "system architecture", "blockchain"],
    "engagement_patterns": {
      "reading_depth": 0.9,
      "comment_frequency": 0.7,
      "content_creation": 0.6
    }
  },
  "philosophy_buff": {
    "user_id": "user_002",
    "name": "Sarah O'Connor",
    "bio": "Philosophy professor specializing in ethics of technology. Researching implications of AI on society.",
    "interests": ["ethics", "philosophy of mind", "AI ethics", "consciousness", "social impact"],
    "expertise_areas": ["philosophy", "ethics", "critical thinking"],
    "engagement_patterns": {
      "reading_depth": 0.95,
      "comment_frequency": 0.8,
      "content_creation": 0.4
    }
  },
  "crypto_trader": {
    "user_id": "user_003",
    "name": "Mike Rodriguez",
    "bio": "Day trader turned DeFi enthusiast. Analyzing crypto markets and blockchain protocols.",
    "interests": ["defi", "trading", "market analysis", "tokenomics", "crypto"],
    "expertise_areas": ["trading", "market analysis", "defi protocols"],
    "engagement_patterns": {
      "reading_depth": 0.7,
      "comment_frequency": 0.9,
      "content_creation": 0.8
    }
  }
}
EOL

# Test content with varying topics and complexity
cat > "$TEST_DATA_DIR/content.json" << EOL
{
  "technical_post": {
    "content_id": "post_001",
    "title": "Zero-Knowledge Proofs in Modern DeFi",
    "text": "Zero-knowledge proofs are revolutionizing DeFi privacy. This post explores how ZK-SNARKs enable private transactions while maintaining network security. We'll dive into the mathematical foundations and practical implementations in protocols like Tornado Cash.",
    "tags": ["defi", "privacy", "cryptography", "blockchain"],
    "complexity_level": 0.8,
    "expected_audience": ["tech_enthusiast", "crypto_trader"]
  },
  "philosophical_post": {
    "content_id": "post_002",
    "title": "The Ethics of Automated Decision Making",
    "text": "As AI systems increasingly make decisions affecting human lives, we must examine the ethical implications. This post discusses the philosophical frameworks for evaluating AI decision-making, focusing on transparency, fairness, and accountability.",
    "tags": ["ethics", "ai", "philosophy", "society"],
    "complexity_level": 0.7,
    "expected_audience": ["philosophy_buff", "tech_enthusiast"]
  },
  "market_analysis": {
    "content_id": "post_003",
    "title": "DeFi Market Analysis: Q4 2023",
    "text": "Analysis of DeFi market trends in Q4 2023. Examining TVL changes, new protocol launches, and yield farming opportunities. Including statistical analysis of major protocol performances and future projections.",
    "tags": ["defi", "market analysis", "trading", "crypto"],
    "complexity_level": 0.6,
    "expected_audience": ["crypto_trader", "tech_enthusiast"]
  }
}
EOL

# Run the Python test script
log_info "Running algorithm tests..."
PYTHONPATH="$(dirname "$0")/../../" python3 "$TEST_DATA_DIR/test_runner.py"

if [ $? -eq 0 ]; then
    log_success "Test flow completed successfully!"
    log_info "📁 Results saved in $TEST_DATA_DIR/test_results.json"
else
    log_error "Test flow failed!"
fi 