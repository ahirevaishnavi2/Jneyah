from flask import Flask, render_template, request, jsonify
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all ML models
from ml_models.pattern_classifier import PatternClassifier
from ml_models.scam_classifier import ScamClassifier
from ml_models.advanced_classifier import AdvancedThreatClassifier
from ml_models.text_threat_detector import TextThreatDetector
from ml_models.url_similarity_detector import URLSimilarityDetector

# Optional utils
try:
    from utils.entity_explainer import highlight_entities
    from utils.threat_graph import ThreatGraph
    from utils.risk_engine import calculate_risk
except:
    highlight_entities = lambda t, e: {}
    ThreatGraph = lambda: type("TG", (), {"add_entities": lambda self, x: None, "get_graph_data": lambda self: {}})()
    calculate_risk = lambda scam_type, entities: 0

# ---------------------------
# FLASK APP
# ---------------------------
app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../static"
)

# ---------------------------
# INITIALIZE ALL MODELS
# ---------------------------
try:
    advanced_clf = AdvancedThreatClassifier()
    advanced_clf.load()
    print("✅ Advanced Threat Classifier loaded")
except Exception as e:
    print(f"⚠️ Advanced Threat Classifier failed: {e}")
    advanced_clf = None

try:
    pattern_clf = PatternClassifier()
    print("✅ Pattern Classifier loaded")
except Exception as e:
    print(f"⚠️ Pattern Classifier failed: {e}")
    pattern_clf = None

try:
    scam_clf = ScamClassifier()
    print("✅ Scam Classifier loaded")
except Exception as e:
    print(f"⚠️ Scam Classifier failed: {e}")
    scam_clf = None

try:
    text_threat_detector = TextThreatDetector()
    text_threat_detector.load()
    print("✅ Text Threat Detector loaded")
except Exception as e:
    print(f"⚠️ Text Threat Detector failed: {e}")
    text_threat_detector = None

try:
    url_detector = URLSimilarityDetector()
    url_detector.load()
    print("✅ URL Similarity Detector loaded")
except Exception as e:
    print(f"⚠️ URL Similarity Detector failed: {e}")
    url_detector = None

# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/advanced-classifier")
def advanced_page():
    return render_template("advanced-classifier.html")

@app.route("/pattern-classifier")
def pattern_page():
    return render_template("pattern-classifier.html")

@app.route("/scam-classifier")
def scam_page():
    return render_template("scam-classifier.html")

@app.route("/text-threat-detector")
def text_threat_page():
    return render_template("text-threat-detector.html")

@app.route("/url-similarity-detector")
def url_similarity_page():
    return render_template("url-similarity-detector.html")

# ---------------------------
# API ENDPOINTS
# ---------------------------
@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        text = request.json.get("text", "").strip()
        if not text:
            return jsonify({"success": False, "error": "Empty text"})

        result_json = {"success": True, "text": text, "analysis": {}}

        # SCAM vs ADVANCED Classification
        social_keywords = ["lottery", "prize", "reward", "won", "kyc", "bank", "urgent"]
        if any(word in text.lower() for word in social_keywords) and scam_clf:
            try:
                scam_result = scam_clf.predict(text)
                result_json["analysis"]["scam"] = scam_result
            except Exception as e:
                result_json["analysis"]["scam"] = {"scam_type": "unknown", "confidence": 0}
        elif advanced_clf:
            try:
                advanced_result = advanced_clf.predict(text)
                result_json["analysis"]["advanced"] = advanced_result
            except Exception as e:
                result_json["analysis"]["advanced"] = {"prediction": "error", "confidence": 0}

        # PATTERN CLUSTERING
        if pattern_clf:
            try:
                pattern_result = pattern_clf.predict(text)
                result_json["analysis"]["pattern"] = pattern_result
            except Exception as e:
                result_json["analysis"]["pattern"] = {
                    "cluster": "error",
                    "similarity": 0,
                    "risk_score": 0,
                    "detected_emotions": []
                }

        # ENTITIES, EXPLANATION, RISK
        entities = []
        if "advanced" in result_json["analysis"]:
            entities.append(result_json["analysis"]["advanced"].get("prediction"))
        if "scam" in result_json["analysis"]:
            entities.append(result_json["analysis"]["scam"].get("scam_type"))

        result_json["entities_detected"] = entities
        result_json["explanation"] = highlight_entities(text, entities)

        graph = ThreatGraph()
        graph.add_entities(entities)
        result_json["threat_graph"] = graph.get_graph_data()

        result_json["risk"] = calculate_risk(entities[0] if entities else "unknown", entities)

        return jsonify(result_json)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/text-threat-detect", methods=["POST"])
def text_threat_detect():
    try:
        text = request.json.get("text", "").strip()
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        if not text_threat_detector:
            return jsonify({"success": False, "error": "Text Threat Detector not available"})
        
        result = text_threat_detector.predict(text)
        
        return jsonify({
            "success": True,
            "text": text,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/url-similarity-detect", methods=["POST"])
def url_similarity_detect():
    try:
        url = request.json.get("url", "").strip()
        if not url:
            return jsonify({"success": False, "error": "Empty URL"})
        
        if not url_detector:
            return jsonify({"success": False, "error": "URL Similarity Detector not available"})
        
        result = url_detector.predict(url)
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/url-similarity-batch", methods=["POST"])
def url_similarity_batch():
    try:
        urls = request.json.get("urls", [])
        if not urls or not isinstance(urls, list):
            return jsonify({"success": False, "error": "No URLs provided"})
        
        if not url_detector:
            return jsonify({"success": False, "error": "URL Similarity Detector not available"})
        
        results = []
        for url in urls[:10]:  # Limit to 10 URLs
            if url.strip():
                result = url_detector.predict(url.strip())
                results.append(result)
        
        return jsonify({
            "success": True,
            "count": len(results),
            "results": results
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/url-database-info", methods=["GET"])
def url_database_info():
    try:
        if url_detector:
            count = len(url_detector.malicious_urls.get('urls', []))
            return jsonify({
                "success": True,
                "count": count,
                "families": list(url_detector.url_families.keys())
            })
        else:
            return jsonify({"success": False, "error": "URL detector not available"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "models_loaded": {
            "advanced_classifier": advanced_clf is not None,
            "pattern_classifier": pattern_clf is not None,
            "scam_classifier": scam_clf is not None,
            "text_threat_detector": text_threat_detector is not None,
            "url_similarity_detector": url_detector is not None
        }
    })

# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 CYBER THREAT INTELLIGENCE PLATFORM")
    print("="*60)
    print("\n📊 Available Features:")
    print("  1. Advanced Threat Classifier")
    print("  2. Pattern Classifier")
    print("  3. Scam Classifier")
    print("  4. Text-Based Threat Detector")
    print("  5. URL Similarity Detector")
    print("\n🌐 Server running at: http://localhost:5000")
    print("📡 Health check: http://localhost:5000/api/health")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)