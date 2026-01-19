import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import re

class ThreatDetector:
    def __init__(self):
        print("🤖 Initializing Threat Detector...")
        
        # Load Kaggle dataset
        try:
            self.df = pd.read_csv("spam.csv", encoding='latin-1')
            print(f"✅ Dataset loaded: {len(self.df)} rows")
            
            self.df = self.df[['v1', 'v2']].copy()
            self.df.columns = ['label', 'text']
            
            print(f"\n📊 Label counts: {self.df['label'].value_counts().to_dict()}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.df = pd.DataFrame({
                'label': ['ham', 'spam', 'ham', 'spam'],
                'text': ['Hello', 'Free money', 'Meeting', 'Click here']
            })
        
        # Load test samples
        try:
            from test_samples import TEST_SAMPLES
            self.test_samples = [sample[0] for sample in TEST_SAMPLES]
            print(f"✅ Loaded {len(self.test_samples)} test samples")
        except ImportError as e:
            print(f"⚠️ Test samples not found: {e}")
            self.test_samples = []
        
        # **CLEAN & DISTINCT KEYWORDS FOR EACH CATEGORY**
        self.keywords = {
            'harassment': [
                # Physical threats
                'kill', 'murder', 'slaughter', 'execute', 'eliminate',
                'hurt', 'harm', 'injure', 'beat', 'assault', 'attack', 'stab',
                'shoot', 'rape', 'molest', 'abuse', 'torture',
                'destroy you', 'end you', 'finish you', 'take you out',
                'put you down', 'get rid of you', 'remove you',
                
                # Emotional/verbal abuse
                'hate you', 'despise you', 'loathe you', 'detest you',
                'stupid', 'idiot', 'moron', 'retard', 'imbecile',
                'worthless', 'useless', 'garbage', 'trash', 'scum',
                'bastard', 'bitch', 'whore', 'slut', 'asshole',
                'motherfucker', 'fucker', 'shit', 'prick',
                'piece of shit', 'son of a bitch',
                
                # Threats with conditions
                'or i will', 'or else', 'otherwise', 'if you don\'t',
                'unless you', 'you better', 'you\'d better',
                'or suffer', 'or face', 'consequences', 'repercussions',
                'payback', 'retaliation', 'revenge', 'vengeance',
                'make you pay', 'teach you a lesson',
                
                # Stalking/threatening knowledge
                'i know where you live', 'i know your address', 'your home',
                'your house', 'i know where you work', 'your workplace',
                'i know your family', 'your family', 'your parents',
                'your kids', 'your children', 'i will find you',
                'i will track you', 'i will come for you', 'watch your back',
                
                # Blackmail/extortion
                'pay me', 'give me money', 'send me money', 'transfer money',
                'pay up', 'pay now', 'pay or', 'money or',
                'bitcoin or', 'crypto or', 'pay in cash',
                'pay in crypto', 'make payment',
                
                # Psychological threats
                'make your life hell', 'ruin your life', 'destroy your life',
                'end your career', 'ruin your reputation', 'break you',
                'humiliate you', 'embarrass you', 'expose you',
                'tell everyone', 'spread rumors', 'leak information',
                
                # Police/authority threats
                'don\'t call police', 'don\'t tell police', 'no police',
                'don\'t involve authorities', 'keep quiet', 'stay silent',
                'keep your mouth shut', 'shut up',
                
                # Suicide/self-harm threats
                'kill yourself', 'end yourself', 'take your life', 'suicide',
                'self-harm', 'cut yourself', 'hurt yourself',
                'hang yourself', 'overdose', 'jump off',
                
                # Cyberbullying/harassment
                'cyberbully', 'online harassment', 'digital stalking',
                'internet stalking', 'doxxing', 'doxx', 'dox',
                'leak info', 'personal info', 'private info',
                'nudes', 'naked photos', 'intimate photos',
                'blackmail', 'extortion', 'ransom',
                
                # Discriminatory harassment
                'racist', 'racial slur', 'sexist', 'sexual harassment',
                'homophobic', 'transphobic', 'lgbtq hate',
                'anti-semitic', 'islamophobic', 'xenophobic',
                'fat-shaming', 'body-shaming',
            ],
            
            'malware': [
                # File extensions (malicious)
                '.exe', '.scr', '.bat', '.cmd', '.msi', '.jar', '.vbs',
                '.ps1', '.js', '.hta', '.pif',
                
                # Obfuscated extensions
                '[.]exe', '[.]scr', '[.]bat', '[.]cmd',
                'dot exe', 'dot scr', 'dot bat',
                
                # Malicious filenames
                'invoice.exe', 'document.exe', 'file.exe', 'photo.exe',
                'picture.exe', 'video.exe', 'setup.exe', 'install.exe',
                'update.exe', 'patch.exe', 'crack.exe', 'keygen.exe',
                'serial.exe', 'activator.exe', 'hack.exe', 'cheat.exe',
                'trainer.exe', 'bot.exe', 'nulled.exe', 'pirated.exe',
                'torrent.exe', 'virus.exe', 'trojan.exe', 'malware.exe',
                'ransomware.exe', 'spyware.exe', 'keylogger.exe',
                
                # Download/install phrases (malware)
                'download now', 'click to download', 'download here',
                'install now', 'click to install', 'run installer',
                'execute file', 'run program', 'launch application',
                'open attachment', 'view document', 'see photo',
                'file attached', 'attachment included', 'enclosed file',
                'download attached', 'install attached', 'run attached',
                
                # Malware-related terms
                'virus', 'trojan', 'worm', 'spyware', 'adware', 'ransomware',
                'keylogger', 'rootkit', 'backdoor', 'botnet', 'malware',
                'malicious software', 'harmful program', 'infected file',
                'hack tool', 'hacking tool', 'crack tool', 'exploit',
                'vulnerability', 'security hole', 'bypass security',
                'disable antivirus', 'turn off defender', 'stop firewall',
                'steal data', 'steal information', 'take data',
                'screen capture', 'screenshot', 'keystroke logging',
                'password capture', 'credential theft', 'identity theft',
                'encrypt files', 'lock files', 'block access',
                'demand payment', 'demand ransom', 'demand bitcoin',
                'pay to unlock', 'pay to decrypt',
            ],
            
            'fraud': [
                # Identity theft
                'ssn', 'social security number', 'social security',
                'credit card number', 'credit card', 'debit card',
                'bank account number', 'bank account', 'account number',
                'routing number', 'swift code', 'iban', 'sort code',
                'atm pin', 'pin number', 'cvv', 'security code',
                'expiry date', 'expiration date',
                
                # Personal information
                'date of birth', 'birth date', 'dob',
                'mother maiden name', 'maiden name',
                'security question', 'security answer',
                'personal information', 'private information',
                'confidential information', 'sensitive information',
                
                # Verification scams
                'verify identity', 'id verification', 'identity verification',
                'confirm identity', 'authentication required',
                'verification code', 'authentication code',
                'security code', 'access code', 'one-time code',
                
                # Financial fraud
                'wire transfer', 'bank transfer', 'money transfer',
                'send money', 'transfer money', 'wire money',
                'western union', 'moneygram', 'paypal', 'venmo',
                'cashapp', 'zelle', 'paytm', 'upi',
                
                # Tax/refund scams
                'irs', 'internal revenue service', 'tax refund',
                'tax return', 'tax payment', 'tax due',
                'government refund', 'government payment',
                'stimulus payment', 'stimulus check',
                
                # Inheritance scams
                'inheritance', 'will', 'estate', 'deceased relative',
                'late father', 'late mother', 'dead uncle', 'dead aunt',
                'banker', 'lawyer', 'barrister', 'attorney',
                'millions', 'millions of dollars', 'fortune',
                
                # Lottery/sweepstakes fraud
                'lottery winning', 'sweepstakes winning',
                'prize money', 'claim prize', 'claim winnings',
                'processing fee', 'administration fee', 'transfer fee',
                'tax fee', 'legal fee', 'customs fee',
                
                # Business fraud
                'invoice payment', 'invoice overdue', 'unpaid invoice',
                'urgent payment', 'immediate payment', 'payment required',
                'overdue amount', 'outstanding balance', 'balance due',
                
                # Charity fraud
                'donation', 'charity', 'fundraising', 'funds needed',
                'help needed', 'urgent help', 'emergency help',
                'disaster relief', 'earthquake', 'flood', 'hurricane',
                'war victims', 'refugees', 'orphans', 'poor children',
            ],
            
            'phishing': [
                # Account security alerts
                'verify your account', 'account verification',
                'secure your account', 'account security',
                'suspicious activity', 'unusual login',
                'unauthorized access', 'security breach',
                'login attempt', 'failed login', 'multiple logins',
                
                # Password/credential requests
                'reset password', 'change password', 'update password',
                'password expired', 'password reset required',
                'forgot password', 'lost password', 'recover account',
                'account recovery', 'restore access', 'regain access',
                
                # Payment/billing issues
                'payment failed', 'payment declined', 'card declined',
                'billing issue', 'subscription issue', 'renewal failed',
                'auto-renewal failed', 'payment problem',
                'failed transaction', 'transaction declined',
                
                # Service alerts
                'account suspended', 'account locked', 'account deactivated',
                'service suspended', 'access suspended', 'temporary hold',
                'permanent suspension', 'terminated account',
                
                # Verification requests
                'confirm details', 'update information', 'verify information',
                'complete verification', 'finish verification',
                'finalize account', 'complete registration',
                
                # Security updates
                'security update', 'important update', 'critical update',
                'urgent update', 'emergency update', 'mandatory update',
                'required update', 'must update', 'need to update',
                
                # Fake notifications
                'important notification', 'urgent notification',
                'security notification', 'account notification',
                'billing notification', 'payment notification',
                
                # Brand impersonation
                'paypal', 'netflix', 'amazon', 'spotify', 'apple',
                'google', 'microsoft', 'facebook', 'instagram',
                'whatsapp', 'twitter', 'youtube', 'linkedin',
                'ebay', 'aliexpress', 'walmart', 'target',
                
                # Urgency indicators
                'immediately', 'asap', 'right now', 'urgent',
                'critical', 'important', 'action required',
                'requires attention', 'needs action', 'must act',
                
                # Link/button text
                'click here', 'click link', 'click button',
                'follow link', 'use link', 'access link',
                'visit site', 'go to site', 'open site''.com',
            ],
            
            'scam': [
                # Free offers
                'free', 'complimentary', 'no charge', 'zero cost',
                'absolutely free', '100% free', 'totally free',
                'completely free', 'entirely free',
                
                # Prize/winnings
                'won', 'winner', 'congratulations', 'you won',
                'you\'ve won', 'you have won', 'prize winner',
                'lottery winner', 'sweepstakes winner',
                'contest winner', 'raffle winner',
                
                # Money offers
                'cash prize', 'cash reward', 'cash bonus',
                'money prize', 'money reward', 'money bonus',
                'cash giveaway', 'money giveaway', 'cash offer',
                'money offer', 'cash opportunity', 'money opportunity',
                
                # Limited time
                'limited time', 'limited offer', 'limited opportunity',
                'time limited', 'offer ends', 'ending soon',
                'expiring soon', 'last chance', 'final chance',
                'only today', 'today only', 'now only',
                
                # Exclusive offers
                'exclusive', 'special', 'unique', 'rare',
                'once in a lifetime', 'never before', 'first time',
                'exclusive deal', 'special deal', 'unique deal',
                
                # Guarantees
                'guaranteed', 'assured', 'certain', 'sure',
                'no risk', 'risk-free', 'safe', 'secure',
                '100% guaranteed', 'fully guaranteed',
                'money-back guarantee', 'refund guarantee',
                
                # Easy money
                'earn money', 'make money', 'get money',
                'quick cash', 'fast cash', 'easy cash',
                'instant cash', 'immediate cash',
                'passive income', 'residual income',
                
                # Work from home
                'work from home', 'work at home', 'home based',
                'remote work', 'online work', 'digital work',
                'no experience needed', 'no skills required',
                'no education required', 'no qualifications',
                
                # Investment scams
                'investment opportunity', 'trading opportunity',
                'crypto opportunity', 'bitcoin opportunity',
                'stock opportunity', 'forex opportunity',
                'high returns', 'high profits', 'high yield',
                'double your money', 'triple your money',
                '10x returns', '100x returns',
                
                # Get rich quick
                'get rich', 'become rich', 'make millions',
                'become millionaire', 'financial freedom',
                'wealthy', 'affluent', 'prosperous',
                'rich lifestyle', 'luxury lifestyle',
                
                # Contact methods
                'dm me', 'message me', 'text me', 'whatsapp me',
                'call me', 'contact me', 'reach me',
                'send me', 'email me', 'write me',
                
                # Reply instructions
                'reply win', 'reply claim', 'reply now',
                'reply yes', 'reply ok', 'reply confirm',
                'text win', 'text claim', 'text now',
                'call now', 'call immediately',
            ]
        }
        
        # ML Setup
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        
        # Train model
        self.train_model()
        
        print("✅ Threat Detector initialized!")
    
    def train_model(self):
        """Train ML model for spam/ham detection only"""
        print("\n📚 Training ML model...")
        
        X = self.df['text'].fillna('').astype(str)
        y = self.df['label'].apply(lambda x: 1 if str(x).strip().lower() == 'spam' else 0)
        
        X_vectorized = self.vectorizer.fit_transform(X)
        self.model.fit(X_vectorized, y)
        
        train_acc = self.model.score(X_vectorized, y)
        print(f"✅ Trained on {len(X)} samples")
        print(f"   Accuracy: {train_acc:.1%}")
        print(f"   Spam: {sum(y)}, Ham: {len(y)-sum(y)}")
    
    def analyze(self, text: str) -> dict:
        """Main analysis function"""
        if not text or not isinstance(text, str):
            return self._error_response("Invalid input")
        
        text = str(text).strip()
        text_lower = text.lower()
        
        # Check categories in priority order
        categories = ['harassment', 'malware', 'fraud', 'phishing', 'scam', 'safe']
        
        for category in categories:
            if category == 'safe':
                break
                
            # Check if text contains keywords for this category
            for keyword in self.keywords[category]:
                if keyword in text_lower:
                    # Found match, return this category
                    found_keywords = [kw for kw in self.keywords[category] if kw in text_lower]
                    risk_score = self._calculate_risk(category, text_lower)
                    confidence = 85.0  # High confidence when keywords match
                    
                    return {
                        "threat_category": category,
                        "risk_score": risk_score,
                        "confidence": confidence,
                        "explanation": f"⚠️ **{category.upper()} DETECTED** - Found keywords: {', '.join(found_keywords[:3])}.",
                        "keywords_found": found_keywords[:5]
                    }
        
        # If no keywords found, use ML
        ml_is_spam, ml_confidence = self._ml_predict(text)
        
        if ml_is_spam:
            return {
                "threat_category": "phishing",
                "risk_score": 70,
                "confidence": round(ml_confidence * 100, 1),
                "explanation": "⚠️ **PHISHING DETECTED** - ML model identified as suspicious.",
                "keywords_found": []
            }
        
        # Safe message
        return {
            "threat_category": "safe",
            "risk_score": 10,
            "confidence": round((1 - ml_confidence) * 100, 1),
            "explanation": "✅ No threats detected. This message appears safe.",
            "keywords_found": []
        }
    
    def _ml_predict(self, text: str):
        """ML prediction"""
        try:
            text_vec = self.vectorizer.transform([text])
            proba = self.model.predict_proba(text_vec)[0]
            
            spam_prob = proba[1] if len(proba) > 1 else 0.5
            return spam_prob > 0.5, max(spam_prob, 1 - spam_prob)
        except:
            return False, 0.5
    
    def _calculate_risk(self, category: str, text_lower: str) -> int:
        """Calculate risk score 0-100"""
        base_scores = {
            'harassment': 95,
            'malware': 90,
            'fraud': 85,
            'phishing': 80,
            'scam': 75,
            'safe': 10
        }
        
        score = base_scores.get(category, 50)
        
        # Bonus for specific indicators
        if 'http' in text_lower or 'https://' in text_lower:
            score += 10
        if 'urgent' in text_lower or 'immediate' in text_lower:
            score += 10
        if '$' in text_lower:
            score += 5
        
        return min(100, score)
    
    def _error_response(self, error_msg: str) -> dict:
        return {
            "threat_category": "error",
            "risk_score": 0,
            "confidence": 0,
            "explanation": f"Error: {error_msg}",
            "keywords_found": []
        }

# Quick test
if __name__ == "__main__":
    detector = ThreatDetector()
    
    print("\n🔍 Testing messages:")
    test_msgs = [
        "CONGRATULATIONS! You've won $50,000 Amazon Gift Card! Claim now: http://tinyurl.com/win-amazon-now Limited time offer! Reply WIN",
        "I know where you live. You better pay me $500 by tomorrow or I'll make your life hell.",
        "Your bank account needs verification. Click http://secure-bank.com/login to avoid suspension.",
        "Download invoice.exe to view your document.",
        "Your SSN 123-45-6789 needs verification immediately."
    ]
    
    for msg in test_msgs:
        result = detector.analyze(msg)
        print(f"\n📩 '{msg[:60]}...'")
        print(f"   Category: {result['threat_category'].upper()}")
        print(f"   Risk: {result['risk_score']}/100")
        print(f"   Confidence: {result['confidence']}%")