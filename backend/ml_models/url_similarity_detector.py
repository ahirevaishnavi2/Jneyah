import os
import re
import json
import hashlib
import urllib.parse
import tldextract
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

class URLSimilarityDetector:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "saved_models")
        os.makedirs(self.model_path, exist_ok=True)
        
        # Load known malicious URLs database
        self.malicious_urls = self.load_malicious_urls()
        
        # URL families
        self.url_families = {
            'bank_scam': ['bank', 'verify', 'login', 'secure', 'account', 'chase', 'wellsfargo', 'bofa'],
            'crypto_scam': ['crypto', 'bitcoin', 'btc', 'eth', 'wallet', 'mining', 'exchange', 'coinbase'],
            'job_scam': ['job', 'career', 'hiring', 'apply', 'interview', 'work', 'employment', 'opportunity'],
            'tech_support': ['support', 'help', 'virus', 'antivirus', 'microsoft', 'apple', 'update', 'install'],
            'phishing': ['login', 'verify', 'account', 'security', 'confirm', 'update', 'password'],
            'malware': ['download', 'install', 'update', 'setup', 'patch', 'crack', 'keygen', 'serial']
        }
        
        # Suspicious TLDs
        self.suspicious_tlds = ['.xyz', '.top', '.club', '.online', '.site', '.website', '.space']
        
        # Heuristic rules
        self.heuristic_rules = {
            'suspicious_characters': ['@', '\\', '//', '..', '--', '__'],
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'hex_encoding': r'%[0-9a-fA-F]{2}',
            'long_url': 100,  # characters
            'shorteners': ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 'adf.ly']
        }
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            analyzer='char',
            ngram_range=(2, 4),
            max_features=1000
        )
        
    def load_malicious_urls(self):
        """Load known malicious URLs from database"""
        db_path = os.path.join(self.model_path, "malicious_urls.json")
        
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                return json.load(f)
        else:
            # Default malicious URLs database
            return {
                "urls": [
                    "http://bank-verify-now.com/login",
                    "https://secure-payment-update.com",
                    "http://free-bitcoin-miner.com/download",
                    "https://apple-support-center.com/help",
                    "http://microsoft-update-2024.com/patch",
                    "http://job-hiring-urgent.com/apply",
                    "https://crypto-wallet-verify.com",
                    "http://facebook-login-secure.com",
                    "https://amazon-account-verify.com",
                    "http://netflix-payment-update.com"
                ],
                "hashes": [],
                "families": {
                    "http://bank-verify-now.com/login": "bank_scam",
                    "https://secure-payment-update.com": "bank_scam",
                    "http://free-bitcoin-miner.com/download": "crypto_scam",
                    "https://apple-support-center.com/help": "tech_support",
                    "http://microsoft-update-2024.com/patch": "tech_support",
                    "http://job-hiring-urgent.com/apply": "job_scam",
                    "https://crypto-wallet-verify.com": "crypto_scam",
                    "http://facebook-login-secure.com": "phishing",
                    "https://amazon-account-verify.com": "phishing",
                    "http://netflix-payment-update.com": "phishing"
                }
            }
    
    def save_malicious_urls(self):
        """Save malicious URLs database"""
        db_path = os.path.join(self.model_path, "malicious_urls.json")
        with open(db_path, 'w') as f:
            json.dump(self.malicious_urls, f, indent=2)
    
    def parse_url(self, url):
        """Parse URL into components"""
        try:
            parsed = urllib.parse.urlparse(url)
            extracted = tldextract.extract(url)
            
            return {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'domain': extracted.domain,
                'subdomain': extracted.subdomain,
                'suffix': extracted.suffix,
                'path': parsed.path,
                'query': parsed.query,
                'fragment': parsed.fragment,
                'full_domain': f"{extracted.domain}.{extracted.suffix}",
                'has_subdomain': bool(extracted.subdomain),
                'tld': extracted.suffix
            }
        except:
            return None
    
    def extract_url_features(self, url):
        """Extract features from URL for analysis"""
        parsed = self.parse_url(url)
        if not parsed:
            return None
        
        features = []
        
        # 1. Domain features
        features.append(f"domain_{parsed['domain']}")
        features.append(f"tld_{parsed['tld']}")
        
        if parsed['has_subdomain']:
            features.append("has_subdomain")
        
        # 2. Path features
        if parsed['path']:
            path_parts = parsed['path'].split('/')
            for part in path_parts:
                if part and len(part) > 2:
                    features.append(f"path_{part}")
        
        # 3. Query features
        if parsed['query']:
            params = urllib.parse.parse_qs(parsed['query'])
            for key in params.keys():
                features.append(f"param_{key}")
        
        # 4. Length features
        if len(url) > self.heuristic_rules['long_url']:
            features.append("long_url")
        
        # 5. Suspicious characters
        for char in self.heuristic_rules['suspicious_characters']:
            if char in url:
                features.append(f"suspicious_char_{char}")
        
        # 6. IP address
        if re.search(self.heuristic_rules['ip_address'], url):
            features.append("contains_ip")
        
        # 7. Hex encoding
        hex_matches = re.findall(self.heuristic_rules['hex_encoding'], url)
        if hex_matches:
            features.append(f"hex_encoded_{len(hex_matches)}")
        
        # 8. URL shortener
        for shortener in self.heuristic_rules['shorteners']:
            if shortener in url:
                features.append(f"shortener_{shortener}")
        
        # 9. Family keywords
        for family, keywords in self.url_families.items():
            for keyword in keywords:
                if keyword in url.lower():
                    features.append(f"family_{family}")
        
        # 10. Suspicious TLD
        if any(tld in url for tld in self.suspicious_tlds):
            features.append("suspicious_tld")
        
        return ' '.join(features)
    
    def calculate_similarity(self, url1, url2):
        """Calculate similarity between two URLs"""
        features1 = self.extract_url_features(url1)
        features2 = self.extract_url_features(url2)
        
        if not features1 or not features2:
            return 0
        
        # Vectorize and calculate cosine similarity
        vectors = self.vectorizer.fit_transform([features1, features2])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        return similarity
    
    def detect_url_family(self, url):
        """Detect URL family based on keywords"""
        url_lower = url.lower()
        family_scores = {}
        
        for family, keywords in self.url_families.items():
            score = 0
            for keyword in keywords:
                if keyword in url_lower:
                    score += 1
            family_scores[family] = score
        
        # Get top family
        if family_scores:
            top_family = max(family_scores, key=family_scores.get)
            if family_scores[top_family] > 0:
                return top_family
        
        return "unknown"
    
    def analyze_domain_behavior(self, url):
        """Analyze domain behavior patterns"""
        parsed = self.parse_url(url)
        if not parsed:
            return {}
        
        analysis = {
            'domain_age_risk': 'unknown',
            'ssl_risk': 'high',
            'reputation_risk': 'high',
            'typosquatting_risk': 'low'
        }
        
        # Check for typosquatting (common domains)
        popular_domains = ['facebook', 'google', 'amazon', 'microsoft', 'apple', 'bank', 'paypal']
        domain_lower = parsed['domain'].lower()
        
        for popular in popular_domains:
            if popular in domain_lower and domain_lower != popular:
                # Calculate Levenshtein distance
                if self.levenshtein_distance(popular, domain_lower) <= 2:
                    analysis['typosquatting_risk'] = 'high'
                    analysis['typosquatting_target'] = popular
        
        # SSL check (simple - https vs http)
        if parsed['scheme'] == 'https':
            analysis['ssl_risk'] = 'medium'
        else:
            analysis['ssl_risk'] = 'high'
        
        # Subdomain analysis
        if parsed['has_subdomain'] and len(parsed['subdomain'].split('.')) > 2:
            analysis['subdomain_risk'] = 'high'
        
        return analysis
    
    def levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def train(self, training_data_path=None):
        """Train the similarity model"""
        print("🔄 Training URL Similarity Detector...")
        
        # Extract features from all known malicious URLs
        urls = self.malicious_urls['urls']
        features = []
        
        for url in urls:
            feat = self.extract_url_features(url)
            if feat:
                features.append(feat)
        
        # Fit vectorizer
        self.vectorizer.fit(features)
        
        # Save model
        joblib.dump(self.vectorizer, f"{self.model_path}/url_vectorizer.pkl")
        
        # Save configuration
        config = {
            'url_families': self.url_families,
            'heuristic_rules': self.heuristic_rules,
            'suspicious_tlds': self.suspicious_tlds
        }
        
        with open(f"{self.model_path}/url_detector_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ URL Similarity Detector trained and saved!")
    
    def load(self):
        """Load trained model"""
        try:
            self.vectorizer = joblib.load(f"{self.model_path}/url_vectorizer.pkl")
            
            # Load configuration
            with open(f"{self.model_path}/url_detector_config.json", 'r') as f:
                config = json.load(f)
                self.url_families = config['url_families']
                self.heuristic_rules = config['heuristic_rules']
                self.suspicious_tlds = config['suspicious_tlds']
        except:
            print("⚠️ Could not load saved model, using defaults")
    
    def predict(self, url):
        """Analyze URL for malware similarity"""
        self.load()
        
        if not self.is_valid_url(url):
            return {
                'error': 'Invalid URL format',
                'similarity_score': 0,
                'family': 'unknown',
                'behavior_analysis': {}
            }
        
        # Clean URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Find most similar malicious URL
        max_similarity = 0
        most_similar_url = None
        similar_urls = []
        
        for malicious_url in self.malicious_urls['urls']:
            similarity = self.calculate_similarity(url, malicious_url)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_url = malicious_url
            
            if similarity > 0.3:  # Threshold for similarity
                similar_urls.append({
                    'url': malicious_url,
                    'similarity': round(similarity, 3),
                    'family': self.malicious_urls['families'].get(malicious_url, 'unknown')
                })
        
        # Sort similar URLs by similarity
        similar_urls.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Detect family
        family = self.detect_url_family(url)
        
        # Domain behavior analysis
        behavior_analysis = self.analyze_domain_behavior(url)
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(url, max_similarity, family, behavior_analysis)
        
        return {
            'url': url,
            'similarity_score': round(max_similarity, 3),
            'most_similar_url': most_similar_url,
            'url_family': family,
            'behavior_analysis': behavior_analysis,
            'risk_score': risk_score,
            'similar_urls': similar_urls[:5],  # Top 5 similar URLs
            'heuristic_warnings': self.get_heuristic_warnings(url)
        }
    
    def is_valid_url(self, url):
        """Check if URL is valid"""
        pattern = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return re.match(pattern, url) is not None
    
    def calculate_risk_score(self, url, similarity, family, behavior_analysis):
        """Calculate risk score for URL"""
        risk = 0
        
        # Base risk from similarity
        risk += similarity * 60
        
        # Family risk
        family_risk = {
            'bank_scam': 25,
            'crypto_scam': 20,
            'job_scam': 15,
            'tech_support': 20,
            'phishing': 30,
            'malware': 35,
            'unknown': 10
        }
        risk += family_risk.get(family, 10)
        
        # Behavior analysis risk
        if behavior_analysis.get('ssl_risk') == 'high':
            risk += 15
        if behavior_analysis.get('typosquatting_risk') == 'high':
            risk += 25
        if behavior_analysis.get('subdomain_risk') == 'high':
            risk += 10
        
        # URL length risk
        if len(url) > 100:
            risk += 5
        
        # Suspicious TLD risk
        if any(tld in url for tld in self.suspicious_tlds):
            risk += 20
        
        return min(risk, 100)
    
    def get_heuristic_warnings(self, url):
        """Get heuristic warnings for URL"""
        warnings = []
        
        # Check for suspicious characters
        for char in self.heuristic_rules['suspicious_characters']:
            if char in url:
                warnings.append(f"Suspicious character '{char}' found")
        
        # Check for IP address
        if re.search(self.heuristic_rules['ip_address'], url):
            warnings.append("URL contains IP address instead of domain")
        
        # Check for URL shortener
        for shortener in self.heuristic_rules['shorteners']:
            if shortener in url:
                warnings.append(f"Uses URL shortener ({shortener})")
        
        # Check length
        if len(url) > self.heuristic_rules['long_url']:
            warnings.append(f"URL is unusually long ({len(url)} characters)")
        
        # Check for hex encoding
        hex_matches = re.findall(self.heuristic_rules['hex_encoding'], url)
        if len(hex_matches) > 3:
            warnings.append(f"Contains {len(hex_matches)} hex-encoded characters")
        
        return warnings

# For testing
if __name__ == "__main__":
    detector = URLSimilarityDetector()
    detector.train()
    
    # Test URLs
    test_urls = [
        "http://bank-verify-secure.com/login",
        "https://free-bitcoin-generator.com",
        "http://microsoft-support-center.com/help",
        "https://amazon.com",
        "http://192.168.1.1/login",
        "bit.ly/suspicious-link"
    ]
    
    for url in test_urls:
        print(f"\n🔗 Analyzing URL: {url}")
        result = detector.predict(url)
        print(f"   Similarity Score: {result['similarity_score']}")
        print(f"   URL Family: {result['url_family']}")
        print(f"   Risk Score: {result['risk_score']}")
        print(f"   Warnings: {len(result['heuristic_warnings'])}")