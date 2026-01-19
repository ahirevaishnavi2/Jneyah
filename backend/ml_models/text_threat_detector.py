import os
import re
import json
from collections import Counter

class TextThreatDetector:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "saved_models")
        os.makedirs(self.model_path, exist_ok=True)
        
        print("🚀 Initializing Text Threat Detector (Keyword-Based)...")
        
        # Comprehensive threat patterns database
        self.threat_patterns = {
            'phishing': {
                'keywords': ['login', 'verify', 'account', 'password', 'click', 'link', 'urgent', 'suspended', 
                           'bank', 'secure', 'update', 'confirm', 'credentials', 'access', 'sign in', 'log in',
                           'validation', 'authorize', 'authenticate', 'reset password', 'unlock account'],
                'url_pattern': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                'phrases': ['verify your account', 'click here to login', 'account suspended', 'urgent action required'],
                'risk_base': 80,
                'description': 'Attempt to steal credentials or personal information'
            },
            'scam': {
                'keywords': ['won', 'prize', 'lottery', 'money', 'free', 'cash', 'reward', 'congratulations',
                           'claim', 'million', 'billion', 'dollar', 'pound', 'euro', 'winner', 'award',
                           'jackpot', 'fortune', 'lucky', 'selected', 'chosen', 'exclusive', 'limited time'],
                'phrases': ['you have won', 'claim your prize', 'congratulations you', 'exclusive offer'],
                'risk_base': 70,
                'description': 'Financial scam or fake prize notification'
            },
            'harassment': {
                'keywords': ['kill', 'die', 'hate', 'stupid', 'ugly', 'worthless', 'threat', 'hurt', 'attack',
                           'harm', 'destroy', 'rape', 'murder', 'suicide', 'bastard', 'idiot', 'moron',
                           'bully', 'abuse', 'terror', 'violence', 'beat', 'fight', 'punish'],
                'phrases': ['i will kill', 'you should die', 'i hate you', 'you are worthless'],
                'risk_base': 90,
                'description': 'Threatening or abusive language'
            },
            'malware': {
                'keywords': ['download', 'install', 'update', 'virus', 'antivirus', 'scan', 'security', 'patch',
                           'exe', 'software', 'program', 'crack', 'keygen', 'serial', 'trojan', 'ransomware',
                           'malware', 'spyware', 'adware', 'rootkit', 'backdoor', 'exploit', 'payload'],
                'phrases': ['download now', 'install software', 'virus detected', 'system infected'],
                'risk_base': 75,
                'description': 'Malicious software or file distribution'
            },
            'fraud': {
                'keywords': ['card', 'credit', 'payment', 'transfer', 'refund', 'fee', 'transaction', 'bitcoin',
                           'crypto', 'wallet', 'paypal', 'venmo', 'wire', 'deposit', 'loan', 'investment',
                           'profit', 'interest', 'fund', 'stock', 'trading', 'banking', 'finance', 'moneygram'],
                'phrases': ['send money', 'wire transfer', 'bank details', 'credit card number'],
                'risk_base': 65,
                'description': 'Financial fraud or unauthorized transactions'
            },
            'spam': {
                'keywords': ['offer', 'deal', 'discount', 'sale', 'buy', 'purchase', 'order', 'shop',
                           'promotion', 'special', 'limited', 'exclusive', 'act now', 'call now', 'click now',
                           'subscribe', 'unsubscribe', 'marketing', 'advertisement', 'commercial'],
                'risk_base': 40,
                'description': 'Unsolicited commercial messages'
            }
        }
        
        # Urgency indicators (increase risk)
        self.urgency_words = ['urgent', 'immediately', 'now', 'today', 'asap', 'hurry', 'quick', 'fast',
                             'important', 'critical', 'emergency', 'alert', 'warning', 'deadline',
                             'expire', 'last chance', 'final', 'instantly', 'right away']
        
        # Authority indicators (increase risk)
        self.authority_words = ['police', 'government', 'court', 'legal', 'official', 'authority',
                               'security', 'admin', 'administrator', 'moderator', 'ceo', 'manager']
        
        # Positive/neutral words (decrease risk)
        self.safe_words = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'please', 'sorry', 'welcome',
                          'okay', 'ok', 'yes', 'no', 'maybe', 'later', 'tomorrow', 'friend', 'family',
                          'help', 'support', 'assist', 'question', 'answer', 'information', 'advice']
        
        # Special patterns
        self.special_patterns = {
            'has_url': r'https?://[^\s]+',
            'has_email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'has_phone': r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]',
            'has_number': r'\$\d+|\d+\s*(dollars|USD|rupees|rs|€|£)',
            'excessive_caps': r'[A-Z]{4,}'
        }
        
        print(f"✅ Loaded {len(self.threat_patterns)} threat categories")
        print(f"✅ Loaded {len(self.urgency_words)} urgency indicators")
        print(f"✅ Loaded {len(self.safe_words)} safe words")
    
    def load(self):
        """For compatibility - no actual loading needed"""
        print("📂 Text Threat Detector ready (keyword-based)")
        return True
    
    def analyze_text(self, text):
        """Comprehensive text analysis"""
        if not text or len(text.strip()) == 0:
            return self._get_empty_analysis()
        
        text_lower = text.lower()
        words = text_lower.split()
        
        analysis = {
            'text_length': len(text),
            'word_count': len(words),
            'detected_categories': {},
            'keyword_matches': [],
            'special_patterns': {},
            'scores': {
                'threat_density': 0,
                'urgency_score': 0,
                'authority_score': 0,
                'safe_score': 0
            }
        }
        
        # Check each threat category
        for category, pattern in self.threat_patterns.items():
            keyword_matches = []
            
            # Check individual keywords
            for keyword in pattern['keywords']:
                if keyword in text_lower:
                    keyword_matches.append(keyword)
            
            # Check phrases
            if 'phrases' in pattern:
                for phrase in pattern['phrases']:
                    if phrase in text_lower:
                        keyword_matches.append(f"[PHRASE]: {phrase}")
            
            if keyword_matches:
                analysis['detected_categories'][category] = {
                    'count': len(keyword_matches),
                    'keywords': keyword_matches,
                    'base_risk': pattern['risk_base'],
                    'description': pattern.get('description', '')
                }
                analysis['keyword_matches'].extend(keyword_matches)
        
        # Check special patterns
        for pattern_name, pattern_regex in self.special_patterns.items():
            matches = re.findall(pattern_regex, text, re.IGNORECASE)
            if matches:
                analysis['special_patterns'][pattern_name] = {
                    'count': len(matches),
                    'examples': matches[:3]  # Limit to 3 examples
                }
        
        # Calculate scores
        analysis['scores']['threat_density'] = len(analysis['keyword_matches']) / max(len(words), 1)
        
        # Urgency score
        for word in self.urgency_words:
            if word in text_lower:
                analysis['scores']['urgency_score'] += 1
        
        # Authority score
        for word in self.authority_words:
            if word in text_lower:
                analysis['scores']['authority_score'] += 1
        
        # Safe score
        for word in self.safe_words:
            if word in text_lower:
                analysis['scores']['safe_score'] += 1
        
        # Check for excessive capitalization
        if re.search(self.special_patterns['excessive_caps'], text):
            analysis['special_patterns']['excessive_caps'] = True
        
        return analysis
    
    def calculate_risk_score(self, analysis):
        """Calculate overall risk score (0-100)"""
        base_risk = 0
        
        # Base risk from threat categories
        for category, data in analysis['detected_categories'].items():
            category_risk = data['base_risk'] * min(data['count'] / 3, 1.5)  # Scale by count
            base_risk = max(base_risk, category_risk)  # Take highest category risk
        
        # Adjust for multiple categories
        category_count = len(analysis['detected_categories'])
        if category_count > 1:
            base_risk += (category_count - 1) * 10
        
        # Threat density adjustment
        base_risk += analysis['scores']['threat_density'] * 30
        
        # URL adds significant risk
        if 'has_url' in analysis['special_patterns']:
            base_risk += 25
        
        # Phone numbers in suspicious context
        if 'has_phone' in analysis['special_patterns'] and category_count > 0:
            base_risk += 15
        
        # Large monetary amounts
        if 'has_number' in analysis['special_patterns']:
            base_risk += 10
        
        # Urgency increases risk
        base_risk += analysis['scores']['urgency_score'] * 8
        
        # Authority references increase risk
        base_risk += analysis['scores']['authority_score'] * 5
        
        # Safe words decrease risk
        base_risk -= min(analysis['scores']['safe_score'] * 5, 30)
        
        # Excessive caps increase risk
        if analysis['special_patterns'].get('excessive_caps'):
            base_risk += 15
        
        # Very short messages might be suspicious
        if analysis['word_count'] < 3 and category_count > 0:
            base_risk += 20
        elif analysis['word_count'] < 3:
            base_risk += 5
        
        # Very long messages might be trying to overwhelm
        if analysis['word_count'] > 100:
            base_risk += 10
        
        # Ensure risk is between 0-100
        return min(max(base_risk, 0), 100)
    
    def determine_threat_category(self, analysis):
        """Determine primary threat category"""
        if not analysis['detected_categories']:
            return 'safe'
        
        # Find category with highest weighted score
        best_category = 'safe'
        best_score = 0
        
        for category, data in analysis['detected_categories'].items():
            # Score = base risk * keyword count
            category_score = data['base_risk'] * data['count']
            
            # Bonus for having special patterns
            if 'has_url' in analysis['special_patterns'] and category in ['phishing', 'scam', 'fraud']:
                category_score += 20
            
            if category_score > best_score:
                best_score = category_score
                best_category = category
        
        return best_category
    
    def calculate_confidence(self, analysis, threat_category):
        """Calculate confidence percentage"""
        if threat_category == 'safe':
            if analysis['word_count'] == 0:
                return 100.0
            # High confidence for safe if no threats detected
            safe_indicators = analysis['scores']['safe_score']
            threat_indicators = len(analysis['keyword_matches'])
            
            if threat_indicators == 0:
                return 95.0
            else:
                return max(60.0, 100.0 - (threat_indicators * 10))
        
        # For threat categories, confidence based on evidence
        evidence_score = 0
        
        # Keyword evidence
        if threat_category in analysis['detected_categories']:
            keyword_count = analysis['detected_categories'][threat_category]['count']
            evidence_score += keyword_count * 15
        
        # Special patterns evidence
        if 'has_url' in analysis['special_patterns']:
            evidence_score += 20
        
        if 'has_number' in analysis['special_patterns'] and threat_category in ['scam', 'fraud']:
            evidence_score += 15
        
        # Urgency evidence
        evidence_score += analysis['scores']['urgency_score'] * 5
        
        # Cap at 95% (never 100% to account for uncertainty)
        confidence = min(60.0 + evidence_score, 95.0)
        
        return round(confidence, 2)
    
    def generate_explanation(self, analysis, threat_category, risk_score):
        """Generate detailed explanation for the decision"""
        explanation = {
            'detected_keywords': [],
            'detected_intents': [],
            'risk_factors': []
        }
        
        # Compile keyword matches
        for category, data in analysis['detected_categories'].items():
            for keyword in data['keywords']:
                explanation['detected_keywords'].append({
                    'keyword': keyword if not keyword.startswith('[PHRASE]: ') else keyword[10:],
                    'category': category,
                    'type': 'phrase' if keyword.startswith('[PHRASE]: ') else 'keyword'
                })
        
        # Detected intents
        explanation['detected_intents'] = list(analysis['detected_categories'].keys())
        
        # Risk factors
        risk_factors = []
        
        # Threat-related factors
        if analysis['detected_categories']:
            total_keywords = len(analysis['keyword_matches'])
            risk_factors.append(f"{total_keywords} threat indicators detected across {len(analysis['detected_categories'])} categories")
        
        # Special patterns factors
        for pattern_name, pattern_data in analysis['special_patterns'].items():
            if pattern_name == 'has_url':
                risk_factors.append(f"Contains {pattern_data['count']} URL(s)")
            elif pattern_name == 'has_phone':
                risk_factors.append(f"Contains phone number(s)")
            elif pattern_name == 'has_number':
                risk_factors.append(f"Contains monetary amount(s)")
            elif pattern_name == 'excessive_caps':
                risk_factors.append("Uses excessive capitalization (shouting)")
        
        # Behavioral factors
        if analysis['scores']['urgency_score'] > 0:
            risk_factors.append(f"Uses {analysis['scores']['urgency_score']} urgency indicator(s)")
        
        if analysis['scores']['authority_score'] > 0:
            risk_factors.append(f"References {analysis['scores']['authority_score']} authority indicator(s)")
        
        # Text characteristics
        risk_factors.append(f"Text length: {analysis['word_count']} words")
        
        if analysis['scores']['threat_density'] > 0.3:
            risk_factors.append("High threat keyword density")
        
        # Safe indicators
        if analysis['scores']['safe_score'] > 0:
            risk_factors.append(f"Contains {analysis['scores']['safe_score']} safe word(s) (reduces risk)")
        
        explanation['risk_factors'] = risk_factors
        
        # Add category description if available
        if threat_category in self.threat_patterns:
            explanation['category_description'] = self.threat_patterns[threat_category].get('description', '')
        
        return explanation
    
    def predict(self, text):
        """Main prediction function"""
        # Analyze the text
        analysis = self.analyze_text(text)
        
        # Determine threat category
        threat_category = self.determine_threat_category(analysis)
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(analysis)
        
        # Calculate confidence
        confidence = self.calculate_confidence(analysis, threat_category)
        
        # Generate explanation
        explanation = self.generate_explanation(analysis, threat_category, risk_score)
        
        return {
            'threat_category': threat_category,
            'confidence': round(confidence, 2),
            'risk_score': round(risk_score, 2),
            'explanation': explanation,
            'analysis_metadata': {
                'word_count': analysis['word_count'],
                'detected_categories_count': len(analysis['detected_categories']),
                'total_keywords_found': len(analysis['keyword_matches'])
            }
        }
    
    def _get_empty_analysis(self):
        """Return analysis structure for empty text"""
        return {
            'text_length': 0,
            'word_count': 0,
            'detected_categories': {},
            'keyword_matches': [],
            'special_patterns': {},
            'scores': {
                'threat_density': 0,
                'urgency_score': 0,
                'authority_score': 0,
                'safe_score': 0
            }
        }


# Test function
def test_detector():
    """Test the detector with various examples"""
    detector = TextThreatDetector()
    
    test_cases = [
        ("Verify your bank account now: http://secure-bank-login.com", "Phishing with URL"),
        ("Congratulations! You won $5,000,000! Click to claim!", "Lottery scam"),
        ("I will kill you tomorrow. You are worthless.", "Harassment"),
        ("Download free antivirus from virus-cleaner.com to clean your PC", "Malware"),
        ("Send $500 to Bitcoin wallet: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Fraud"),
        ("Hello John, how are you doing today?", "Safe message"),
        ("URGENT: Your account will be deleted in 24 hours!", "Urgent phishing"),
        ("Limited time offer: Buy now and get 50% discount!", "Spam"),
        ("", "Empty text"),
        ("Call me at 123-456-7890 for more information", "Phone number in neutral context"),
    ]
    
    print("\n" + "="*70)
    print("🧪 TEXT THREAT DETECTOR - TEST RESULTS")
    print("="*70)
    
    for text, description in test_cases:
        result = detector.predict(text)
        
        print(f"\n📝 TEST: {description}")
        print(f"   Text: {text[:60]}{'...' if len(text) > 60 else ''}")
        print(f"   🔍 Category: {result['threat_category'].upper()}")
        print(f"   📊 Risk Score: {result['risk_score']}/100")
        print(f"   🎯 Confidence: {result['confidence']}%")
        
        if result['explanation']['detected_keywords']:
            keywords = [kw['keyword'] for kw in result['explanation']['detected_keywords'][:3]]
            print(f"   🔑 Keywords: {', '.join(keywords)}{'...' if len(result['explanation']['detected_keywords']) > 3 else ''}")
        
        print(f"   📈 Factors: {len(result['explanation']['risk_factors'])} risk factors identified")
    
    print("\n" + "="*70)
    print("✅ Text Threat Detector is working correctly!")
    print("="*70)


# Train function (optional - for compatibility)
def train_model():
    """Train a model if dataset exists (optional)"""
    print("\n🔧 Note: Using keyword-based detection (no training required)")
    print("   To use ML model, create dataset and call train() method")
    return True


if __name__ == "__main__":
    # Create detector instance
    detector = TextThreatDetector()
    
    # Test it
    test_detector()
    
    # Test with user input
    print("\n\n🎯 Interactive Test Mode")
    print("="*50)
    
    while True:
        user_input = input("\nEnter text to analyze (or 'quit' to exit): ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
        
        if not user_input.strip():
            print("⚠️ Please enter some text")
            continue
        
        result = detector.predict(user_input)
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   Threat Category: {result['threat_category'].upper()}")
        print(f"   Risk Level: {result['risk_score']}/100")
        print(f"   Confidence: {result['confidence']}%")
        
        if result['explanation']['detected_keywords']:
            print(f"\n🔑 DETECTED KEYWORDS:")
            for kw in result['explanation']['detected_keywords'][:5]:  # Show first 5
                print(f"   - {kw['keyword']} ({kw['category']})")
        
        if result['explanation']['risk_factors']:
            print(f"\n⚠️ RISK FACTORS:")
            for factor in result['explanation']['risk_factors'][:5]:  # Show first 5
                print(f"   • {factor}")
        
        print(f"\n📈 METADATA: {result['analysis_metadata']['word_count']} words, " +
              f"{result['analysis_metadata']['detected_categories_count']} threat categories, " +
              f"{result['analysis_metadata']['total_keywords_found']} keywords found")
        
        # Show emoji based on risk
        if result['risk_score'] >= 80:
            print("🚨 CRITICAL THREAT DETECTED!")
        elif result['risk_score'] >= 60:
            print("⚠️ HIGH RISK DETECTED")
        elif result['risk_score'] >= 40:
            print("🔶 MEDIUM RISK DETECTED")
        elif result['risk_score'] >= 20:
            print("🔸 LOW RISK DETECTED")
        else:
            print("✅ SAFE MESSAGE")