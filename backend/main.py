from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import sys
from typing import List, Optional

# Get the absolute path to frontend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# ==================== IMPORT BOTH DETECTORS ====================

# Import TEXT threat detector (from controller.py)
sys.path.append(BASE_DIR)
try:
    from controller import ThreatDetector
    text_detector = ThreatDetector()
    print("✅ Text threat detector initialized successfully")
except Exception as e:
    print(f"⚠️ Failed to initialize text detector: {e}")
    text_detector = None

# Import MALWARE detector (from malware.py)
try:
    from malware import MalwareDetectionLogic
    malware_detector = MalwareDetectionLogic('malicious_phish.csv')
    print("✅ Malware URL detector initialized successfully")
except Exception as e:
    print(f"⚠️ Failed to initialize malware detector: {e}")
    malware_detector = None

# ==================== CREATE APP ====================

app = FastAPI(
    title="CyberShield AI - Complete Threat Detection",
    description="Detect phishing, scams, harassment, malware, fraud in text messages AND URLs",
    version="2.0.0"
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== REQUEST MODELS ====================

class TextRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

class BatchURLRequest(BaseModel):
    urls: List[str]

# ==================== TEXT DETECTION ROUTES ====================

@app.get("/")
def serve_dashboard():
    """Serve the main dashboard (text detection)"""
    html_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": f"index.html not found at: {html_path}"}

@app.get("/malware-detection")
def serve_malware_detection():
    """Serve the malware detection page"""
    html_path = os.path.join(FRONTEND_DIR, "malware_detect.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": f"malware_detect.html not found at: {html_path}"}

# ==================== ORIGINAL TEXT ENDPOINTS (for your index.html) ====================

@app.post("/analyze")
def analyze_text_post(request: TextRequest):
    """Analyze text using POST request with JSON - ORIGINAL ENDPOINT"""
    if not text_detector:
        raise HTTPException(status_code=500, detail="Text detector not initialized")
    
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = text_detector.analyze(request.text)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/analyze")
def analyze_text_get(text: str):
    """Analyze text using GET request with URL parameter - ORIGINAL ENDPOINT"""
    if not text_detector:
        raise HTTPException(status_code=500, detail="Text detector not initialized")
    
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = text_detector.analyze(text)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# ==================== NEW TEXT ENDPOINTS (for consistency) ====================

@app.post("/api/text/analyze")
async def analyze_text_new_post(request: TextRequest):
    """Analyze text - NEW API endpoint"""
    return await analyze_text_post(request)

@app.get("/api/text/analyze")
def analyze_text_new_get(text: str):
    """Analyze text - NEW API endpoint"""
    return analyze_text_get(text)

# ==================== MALWARE DETECTION ROUTES ====================

@app.post("/api/malware/detect")
async def detect_malware(request: URLRequest):
    """Analyze single URL for malware"""
    if not malware_detector:
        raise HTTPException(status_code=500, detail="Malware detector not initialized")
    
    try:
        print(f"🔍 Analyzing URL: {request.url[:100]}...")
        result = malware_detector.analyze_url(request.url)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/api/malware/batch-detect")
async def batch_detect_malware(request: BatchURLRequest):
    """Analyze multiple URLs for malware"""
    if not malware_detector:
        raise HTTPException(status_code=500, detail="Malware detector not initialized")
    
    try:
        print(f"📦 Batch analyzing {len(request.urls)} URLs...")
        results = malware_detector.batch_analyze(request.urls)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis error: {str(e)}")

@app.get("/api/malware/examples")
def get_example_urls():
    """Get example URLs for testing"""
    return {
        "examples": [
            {
                "type": "bank_scam",
                "url": "https://secure-login-bank-verify.paypal.tk/login.php?id=12345",
                "name": "Bank Phishing",
                "description": "PayPal credential theft attempt"
            },
            {
                "type": "crypto_scam",
                "url": "http://free-bitcoin-miner-download.exe.xyz/walletconnect",
                "name": "Crypto Malware",
                "description": "Bitcoin miner malware distribution"
            },
            {
                "type": "job_scam",
                "url": "https://work-from-home-immediate-hiring-job.site/apply-now",
                "name": "Job Scam",
                "description": "Fake job recruitment fraud"
            },
            {
                "type": "legitimate",
                "url": "https://www.google.com/search?q=python",
                "name": "Legitimate",
                "description": "Safe Google search"
            },
            {
                "type": "suspicious",
                "url": "http://9779.info/%E5%84%BF%E7%AB%A5%E7%AB%8B%E4%BD%93%E7%BA%B8%E8%B4%B4%E7%94%BB/",
                "name": "Suspicious URL",
                "description": "Numeric domain with encoded path"
            }
        ]
    }

@app.get("/api/malware/stats")
def get_malware_stats():
    """Get malware detection statistics"""
    if not malware_detector:
        return {"error": "Detector not initialized"}
    
    try:
        stats = {
            "dataset_size": len(malware_detector.df),
            "malicious_count": len(malware_detector.malicious_df),
            "benign_count": len(malware_detector.benign_df),
            "families": {
                "bank_scam": len(malware_detector.df[malware_detector.df['family'] == 'bank_scam']),
                "crypto_scam": len(malware_detector.df[malware_detector.df['family'] == 'crypto_scam']),
                "job_scam": len(malware_detector.df[malware_detector.df['family'] == 'job_scam'])
            },
            "heuristic_rules": sum(len(rules['rules']) for rules in malware_detector.heuristic_rules.values()),
            "vectorizer_features": malware_detector.malicious_vectors.shape[1] if hasattr(malware_detector, 'malicious_vectors') else 0
        }
        return stats
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/malware/test")
def test_malware_detection():
    """Test malware detection with sample URLs"""
    if not malware_detector:
        return {"error": "Detector not initialized"}
    
    test_urls = [
        "http://9779.info/%E5%84%BF%E7%AB%A5%E7%AB%8B%E4%BD%93%E7%BA%B8%E8%B4%B4%E7%94%BB/",
        "https://secure-login-bank-verify.paypal.tk/login.php",
        "http://free-bitcoin-miner-download.exe.xyz",
        "https://www.google.com",
        "http://185.162.128.43/login.php"
    ]
    
    results = malware_detector.batch_analyze(test_urls)
    
    summary = {
        "total_urls": len(results),
        "malicious_detected": sum(1 for r in results if r.get('is_malicious', False)),
        "results": results
    }
    
    return summary

# ==================== TEST & HEALTH ROUTES ====================

@app.get("/test")
def test_samples():
    """Test the API with sample messages from test_samples.py - ORIGINAL ENDPOINT"""
    try:
        from test_samples import TEST_SAMPLES
        samples = [sample[0] for sample in TEST_SAMPLES]
        
        results = []
        for sample in samples:
            result = text_detector.analyze(sample)
            results.append({
                "input": sample,
                "result": result
            })
        
        return {
            "total_tested": len(results),
            "samples": results
        }
    except ImportError:
        return {"error": "test_samples.py not found"}

@app.get("/test-advanced")
def test_advanced():
    """Test with both text and expected category - ORIGINAL ENDPOINT"""
    try:
        from test_samples import TEST_SAMPLES
        
        results = []
        correct = 0
        
        for text, expected_category in TEST_SAMPLES:
            result = text_detector.analyze(text)
            detected_category = result["threat_category"]
            is_correct = detected_category == expected_category
            
            if is_correct:
                correct += 1
            
            results.append({
                "text": text,
                "expected": expected_category,
                "detected": detected_category,
                "correct": is_correct,
                "risk_score": result["risk_score"],
                "confidence": result["confidence"]
            })
        
        accuracy = (correct / len(TEST_SAMPLES)) * 100 if TEST_SAMPLES else 0
        
        return {
            "total_tests": len(TEST_SAMPLES),
            "correct": correct,
            "incorrect": len(TEST_SAMPLES) - correct,
            "accuracy": f"{accuracy:.1f}%",
            "breakdown": results
        }
    except ImportError:
        return {"error": "test_samples.py not found"}

@app.get("/api/test/text")
def test_text_samples():
    """Test the text API with sample messages - NEW ENDPOINT"""
    return test_samples()

@app.get("/api/test/advanced")
def test_advanced_new():
    """Test with both text and expected category - NEW ENDPOINT"""
    return test_advanced()

@app.get("/stats")
def get_stats():
    """Get API statistics - ORIGINAL ENDPOINT"""
    return {
        "status": "running",
        "model_trained": True,
        "training_samples": len(text_detector.df) if text_detector else 0,
        "spam_count": len(text_detector.df[text_detector.df['label'] == 'spam']) if text_detector else 0,
        "ham_count": len(text_detector.df[text_detector.df['label'] == 'ham']) if text_detector else 0,
        "test_samples_available": len(getattr(text_detector, 'test_samples', [])) if text_detector else 0
    }

@app.get("/api/stats")
def get_stats_new():
    """Get API statistics for both systems - NEW ENDPOINT"""
    text_stats = {
        "status": "initialized" if text_detector else "not_initialized",
        "training_samples": len(text_detector.df) if text_detector else 0,
        "spam_count": len(text_detector.df[text_detector.df['label'] == 'spam']) if text_detector else 0,
        "ham_count": len(text_detector.df[text_detector.df['label'] == 'ham']) if text_detector else 0,
    }
    
    malware_stats = {
        "status": "initialized" if malware_detector else "not_initialized",
        "dataset_size": len(malware_detector.df) if malware_detector else 0,
        "malicious_count": len(malware_detector.malicious_df) if malware_detector else 0,
        "benign_count": len(malware_detector.benign_df) if malware_detector else 0,
    }
    
    return {
        "system": "CyberShield AI - Complete Threat Detection",
        "version": "2.0.0",
        "text_detection": text_stats,
        "malware_detection": malware_stats,
        "endpoints": {
            "text_analysis": "GET /analyze?text=... or POST /api/text/analyze",
            "malware_detection": "POST /api/malware/detect",
            "dashboard": "GET /",
            "malware_dashboard": "GET /malware-detection"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "text_detection": text_detector is not None,
            "malware_detection": malware_detector is not None,
            "api_version": "2.0.0"
        }
    }

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("=" * 70)
    print("🛡️  CYBERSHIELD AI - COMPLETE THREAT DETECTION SYSTEM")
    print("=" * 70)
    print("📡 Main Dashboard (Text Analysis): http://localhost:8000")
    print("🔗 Malware URL Detection: http://localhost:8000/malware-detection")
    print("📊 API Docs: http://localhost:8000/docs")
    print("=" * 70)
    print("📁 Available endpoints:")
    print("   TEXT ANALYSIS (Original - for your index.html):")
    print("     GET  /analyze?text=... - Analyze text")
    print("     POST /analyze         - Analyze text (JSON)")
    print("     GET  /test            - Test text detection")
    print("     GET  /test-advanced   - Advanced testing")
    print()
    print("   TEXT ANALYSIS (New API):")
    print("     GET  /api/text/analyze?text=...")
    print("     POST /api/text/analyze")
    print()
    print("   MALWARE URL DETECTION:")
    print("     POST /api/malware/detect    - Analyze single URL")
    print("     POST /api/malware/batch-detect - Analyze multiple URLs")
    print("     GET  /api/malware/examples  - Get example URLs")
    print("     GET  /api/malware/stats     - Get malware statistics")
    print("     GET  /api/malware/test      - Test malware detection")
    print("=" * 70)
    
    # Check file existence
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    malware_path = os.path.join(FRONTEND_DIR, "malware_detect.html")
    
    if os.path.exists(index_path):
        print("✅ index.html found")
    else:
        print(f"⚠️ index.html NOT found at: {index_path}")
    
    if os.path.exists(malware_path):
        print("✅ malware_detect.html found")
    else:
        print(f"⚠️ malware_detect.html NOT found at: {malware_path}")
    
    print("=" * 70)
    print("🚀 Starting server... Press Ctrl+C to stop")
    print("=" * 70)
    
    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)