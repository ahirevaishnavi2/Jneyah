from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .ocr_service import OCRService
from ingredients.ingredient_service import IngredientService
from user.user_profile_service import UserProfileService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scan", tags=["scan"])

# Initialize OCR service
ocr_service = OCRService()

@router.post("/upload")
async def scan_product_label(
    user_id: str = Form(...),
    image: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Upload and scan product label image
    """
    try:
        # Validate image
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        contents = await image.read()
        
        # Extract text using OpenAI Vision
        extracted_text = ocr_service.extract_text_from_image(contents)
        
        # Extract ingredients from text
        ingredients = ocr_service.extract_ingredients(extracted_text)
        
        # Get user profile
        user_profile = UserProfileService.get_user_profile(user_id)
        
        # Analyze each ingredient with safety data
        analyzed_ingredients = []
        for ing in ingredients:
            # Get safety data
            safety_data = IngredientService.analyze_ingredient(ing['name'])
            
            # Calculate personalized risk
            personalized_risk = calculate_personalized_risk(safety_data, user_profile)
            
            analyzed_ingredients.append({
                "name": ing['name'],
                "original": ing.get('original', ing['name']),
                "category": ing.get('category', 'unknown'),
                "confidence": ing.get('confidence', 0.8),
                "safety": {
                    "name": safety_data.name if safety_data else ing['name'],
                    "description": safety_data.description if safety_data else "No data available",
                    "risk_level": personalized_risk["level"],
                    "risk_score": personalized_risk["score"],
                    "benefits": safety_data.benefits if safety_data else [],
                    "side_effects": safety_data.side_effects if safety_data else ["Insufficient data"],
                    "personalized_warnings": personalized_risk["warnings"]
                } if safety_data else {
                    "name": ing['name'],
                    "description": "Ingredient not found in database",
                    "risk_level": personalized_risk["level"],
                    "risk_score": personalized_risk["score"],
                    "benefits": [],
                    "side_effects": ["Insufficient data"],
                    "personalized_warnings": personalized_risk["warnings"]
                }
            })
        
        # Calculate overall product safety
        overall_analysis = analyze_product_safety(analyzed_ingredients, user_profile)
        
        return {
            "success": True,
            "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "ingredients": analyzed_ingredients,
            "ingredient_count": len(analyzed_ingredients),
            "analysis": overall_analysis,
            "user_profile_applied": {
                "skin_type": user_profile.get("skinType"),
                "concerns": user_profile.get("skinConcerns", []),
                "allergies": user_profile.get("skincareAllergies", [])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_personalized_risk(safety_data, user_profile):
    """Calculate personalized risk based on user profile"""
    base_score = safety_data.risk_score if safety_data else 40
    base_level = safety_data.risk_level if safety_data else "unknown"
    warnings = []
    
    ingredient_name = safety_data.name.lower() if safety_data else ""
    
    # Check pregnancy
    if user_profile.get("pregnancy") != "no":
        if "retinol" in ingredient_name or "vitamin a" in ingredient_name:
            base_score += 30
            warnings.append("Avoid during pregnancy")
        if "salicylic" in ingredient_name:
            base_score += 20
            warnings.append("Use with caution during pregnancy")
    
    # Check sensitive skin
    if user_profile.get("skinType") == "sensitive":
        if "fragrance" in ingredient_name or "parfum" in ingredient_name:
            base_score += 25
            warnings.append("May irritate sensitive skin")
        if "alcohol" in ingredient_name:
            base_score += 15
            warnings.append("Can be drying for sensitive skin")
    
    # Check allergies
    allergies = user_profile.get("skincareAllergies", [])
    if "fragrance" in allergies and ("fragrance" in ingredient_name or "parfum" in ingredient_name):
        base_score += 40
        warnings.append("You're allergic to fragrances!")
    
    # Determine level
    base_score = min(100, base_score)
    if base_score >= 70:
        level = "high"
    elif base_score >= 40:
        level = "medium"
    else:
        level = "low"
    
    return {
        "score": base_score,
        "level": level,
        "base_level": base_level,
        "warnings": warnings
    }

def analyze_product_safety(ingredients, user_profile):
    """Analyze overall product safety"""
    high_count = 0
    medium_count = 0
    low_count = 0
    total_score = 0
    concerns = []
    
    for ing in ingredients:
        risk_level = ing["safety"]["risk_level"]
        risk_score = ing["safety"]["risk_score"]
        
        if risk_level == "high":
            high_count += 1
            concerns.append(f"{ing['name']}: High risk for your profile")
        elif risk_level == "medium":
            medium_count += 1
        else:
            low_count += 1
        
        total_score += risk_score
    
    avg_score = total_score / len(ingredients) if ingredients else 0
    
    # Determine overall risk
    if high_count > 0:
        overall_level = "high"
        recommendation = "⚠️ Not recommended for your profile - contains high-risk ingredients"
    elif medium_count > 2:
        overall_level = "medium"
        recommendation = "⚠️ Use with caution - multiple medium-risk ingredients"
    else:
        overall_level = "low"
        recommendation = "✅ Appears safe for your profile"
    
    return {
        "overall_level": overall_level,
        "overall_score": round(avg_score, 1),
        "high_risk_count": high_count,
        "medium_risk_count": medium_count,
        "low_risk_count": low_count,
        "total_ingredients": len(ingredients),
        "concerns": concerns[:3],
        "recommendation": recommendation
    }

# from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
# from fastapi.responses import JSONResponse, FileResponse
# from typing import List, Optional
# import uuid
# from datetime import datetime
# import os
# from pathlib import Path
# import shutil
# import re
# import json

# from auth.auth_service import verify_token
# from fastapi import Depends, HTTPException
# from database.db_connection import Database
# from fastapi.security import HTTPBearer


# router = APIRouter(prefix="/api/scan", tags=["scan"])

# # Create upload directory
# UPLOAD_DIR = Path("uploads/scans")
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# # Enhanced ingredient database with categories and risks
# INGREDIENT_DATABASE = {
#     'water': {'risk': 'low', 'category': 'solvent', 'concern': False},
#     'aqua': {'risk': 'low', 'category': 'solvent', 'concern': False},
#     'glycerin': {'risk': 'low', 'category': 'humectant', 'concern': False},
#     'niacinamide': {'risk': 'low', 'category': 'active', 'concern': False},
#     'hyaluronic acid': {'risk': 'low', 'category': 'humectant', 'concern': False},
#     'vitamin c': {'risk': 'low', 'category': 'active', 'concern': False},
#     'ascorbic acid': {'risk': 'low', 'category': 'active', 'concern': False},
#     'citric acid': {'risk': 'low', 'category': 'preservative', 'concern': False},
#     'sodium chloride': {'risk': 'low', 'category': 'thickener', 'concern': False},
#     'panthenol': {'risk': 'low', 'category': 'conditioner', 'concern': False},
#     'allantoin': {'risk': 'low', 'category': 'soothing', 'concern': False},
#     'tocopherol': {'risk': 'low', 'category': 'antioxidant', 'concern': False},
#     'zinc oxide': {'risk': 'low', 'category': 'sunscreen', 'concern': False},
#     'titanium dioxide': {'risk': 'low', 'category': 'sunscreen', 'concern': False},
    
#     # Medium risk ingredients
#     'sodium laureth sulfate': {'risk': 'medium', 'category': 'surfactant', 'concern': True, 'reason': 'Can cause skin irritation'},
#     'sodium lauryl sulfate': {'risk': 'medium', 'category': 'surfactant', 'concern': True, 'reason': 'Can be drying and irritating'},
#     'cocamidopropyl betaine': {'risk': 'low', 'category': 'surfactant', 'concern': False},
#     'fragrance': {'risk': 'medium', 'category': 'perfume', 'concern': True, 'reason': 'Potential allergen'},
#     'parfum': {'risk': 'medium', 'category': 'perfume', 'concern': True, 'reason': 'Potential allergen'},
#     'alcohol': {'risk': 'medium', 'category': 'solvent', 'concern': True, 'reason': 'Can be drying'},
#     'alcohol denat': {'risk': 'medium', 'category': 'solvent', 'concern': True, 'reason': 'Can be drying'},
#     'propylene glycol': {'risk': 'medium', 'category': 'humectant', 'concern': True, 'reason': 'Potential irritant'},
#     'salicylic acid': {'risk': 'medium', 'category': 'active', 'concern': True, 'reason': 'Can cause irritation in sensitive skin'},
#     'retinol': {'risk': 'medium', 'category': 'active', 'concern': True, 'reason': 'Can cause irritation, not for sensitive skin'},
    
#     # High risk ingredients
#     'formaldehyde': {'risk': 'high', 'category': 'preservative', 'concern': True, 'reason': 'Known carcinogen'},
#     'paraben': {'risk': 'high', 'category': 'preservative', 'concern': True, 'reason': 'Endocrine disruptor'},
#     'methylparaben': {'risk': 'high', 'category': 'preservative', 'concern': True, 'reason': 'Endocrine disruptor'},
#     'propylparaben': {'risk': 'high', 'category': 'preservative', 'concern': True, 'reason': 'Endocrine disruptor'},
#     'phthalate': {'risk': 'high', 'category': 'plasticizer', 'concern': True, 'reason': 'Endocrine disruptor'},
#     'triclosan': {'risk': 'high', 'category': 'antimicrobial', 'concern': True, 'reason': 'Antibiotic resistance concern'},
#     'oxybenzone': {'risk': 'high', 'category': 'sunscreen', 'concern': True, 'reason': 'Environmental and health concerns'},
#     'benzophenone': {'risk': 'high', 'category': 'sunscreen', 'concern': True, 'reason': 'Potential allergen'},
# }

# # Product type mappings
# PRODUCT_INGREDIENTS = {
#     'face_cream': ['Water', 'Glycerin', 'Niacinamide', 'Hyaluronic Acid', 'Vitamin C', 'Citric Acid', 'Fragrance', 'Tocopherol'],
#     'shampoo': ['Water', 'Sodium Laureth Sulfate', 'Cocamidopropyl Betaine', 'Glycerin', 'Fragrance', 'Citric Acid', 'Sodium Chloride', 'Panthenol'],
#     'sunscreen': ['Water', 'Zinc Oxide', 'Titanium Dioxide', 'Glycerin', 'Alcohol', 'Fragrance', 'Citric Acid', 'Tocopherol'],
#     'cleanser': ['Water', 'Sodium Laureth Sulfate', 'Cocamidopropyl Betaine', 'Glycerin', 'Salicylic Acid', 'Fragrance', 'Citric Acid', 'Allantoin'],
#     'serum': ['Water', 'Hyaluronic Acid', 'Vitamin C', 'Niacinamide', 'Glycerin', 'Citric Acid', 'Panthenol', 'Tocopherol'],
# }

# async def get_current_user_dependency(
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ):
#     try:
#         token = credentials.credentials
#         user = auth_service.get_current_user(token)
#         return {
#             "user_id": user.id,
#             "email": user.email,
#             "role": user.role
#         }
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")

# # Then use it in your routes:
# @router.get("/scan/test")
# async def scan_test(user: Dict[str, Any] = Depends(get_current_user_dependency)):
#     return {
#         "message": "Scan route working",
#         "user": user
#     }
# @router.post("/upload")
# async def upload_image(
#     image: UploadFile = File(...),
#     current_user: dict = Depends(get_current_user_dependency)
# ):
#     # ... rest of the code
#     """Handle image upload for ingredient analysis"""
#     try:
#         user_id = current_user["user_id"]
        
#         # Check file
#         if not image.filename:
#             raise HTTPException(status_code=400, detail="No image file provided")
        
#         # Generate unique filename
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         filename = f"{user_id}_{timestamp}_{image.filename}"
#         filepath = UPLOAD_DIR / filename
        
#         # Save file locally
#         with open(filepath, "wb") as buffer:
#             shutil.copyfileobj(image.file, buffer)
        
#         # Create URL for the saved file
#         image_url = f"/uploads/scans/{filename}"
        
#         # Determine product type from filename for mock data
#         product_type = determine_product_type(image.filename)
#         mock_ingredients = get_mock_ingredients(product_type)
        
#         # Extract and analyze ingredients
#         ingredients_list = extract_ingredients_simple(mock_ingredients)
#         analysis_results = analyze_ingredients_simple(ingredients_list)
#         risk_score = calculate_risk_score_simple(analysis_results)
        
#         # Store scan history
#        from database.db_connection import get_db
# db = get_db()

#         scan_id = str(uuid.uuid4())
        
#         scan_record = {
#             'scan_id': scan_id,
#             'user_id': user_id,
#             'timestamp': datetime.utcnow(),
#             'image_url': image_url,
#             'filename': image.filename,
#             'product_type': product_type,
#             'ingredients': ingredients_list,
#             'analysis': analysis_results,
#             'risk_score': risk_score
#         }
        
#         # Create collections if they don't exist
#         if 'scans' not in db.list_collection_names():
#             db.create_collection('scans')
        
#         db.scans.insert_one(scan_record)
        
#         # Prepare citizen-friendly response
#         response = {
#             'scan_id': scan_id,
#             'status': 'success',
#             'product_type': product_type,
#             'ingredients_found': len(ingredients_list),
#             'analysis': analysis_results,
#             'risk_summary': {
#                 'level': risk_score['level'],
#                 'color': risk_score['color'],
#                 'score': risk_score['score'],
#                 'primary_concerns': risk_score['primary_concerns'][:3],
#                 'recommendation': risk_score['recommendation'],
#                 'alternatives': risk_score.get('alternatives', [])
#             },
#             'quick_tips': generate_quick_tips(analysis_results, risk_score['level']),
#             'timestamp': datetime.utcnow().isoformat(),
#             'image_preview': image_url,
#             'note': 'Analysis based on simulated OCR. Real implementation would use image processing.'
#         }
        
#         return JSONResponse(content=response)
        
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         print(f"Error in upload_image: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# @router.post("/manual-entry")
# async def manual_entry(
#     ingredients_text: str = Form(...),
#     current_user: dict = Depends(get_current_user_dependency)

# ):
#     """Handle manual ingredient entry"""
#     try:
#         user_id = current_user["user_id"]
        
#         if not ingredients_text or len(ingredients_text.strip()) < 10:
#             raise HTTPException(status_code=400, detail="Ingredients text required (minimum 10 characters)")
        
#         # Extract ingredients from text
#         ingredients_list = extract_ingredients_simple(ingredients_text)
        
#         if not ingredients_list:
#             raise HTTPException(status_code=400, detail="No valid ingredients found in text")
        
#         # Analyze ingredients
#         analysis_results = analyze_ingredients_simple(ingredients_list)
#         risk_score = calculate_risk_score_simple(analysis_results)
        
#         # Store manual entry
#         from database.db_connection import get_db
# db = get_db()

#         entry_id = str(uuid.uuid4())
        
#         manual_entry_record = {
#             'entry_id': entry_id,
#             'user_id': user_id,
#             'timestamp': datetime.utcnow(),
#             'ingredients_text': ingredients_text,
#             'ingredients': ingredients_list,
#             'analysis': analysis_results,
#             'risk_score': risk_score
#         }
        
#         # Create collections if they don't exist
#         if 'manual_entries' not in db.list_collection_names():
#             db.create_collection('manual_entries')
        
#         db.manual_entries.insert_one(manual_entry_record)
        
#         response = {
#             'entry_id': entry_id,
#             'status': 'success',
#             'analysis': analysis_results,
#             'risk_summary': {
#                 'level': risk_score['level'],
#                 'color': risk_score['color'],
#                 'score': risk_score['score'],
#                 'primary_concerns': risk_score['primary_concerns'][:3],
#                 'recommendation': risk_score['recommendation'],
#                 'alternatives': risk_score.get('alternatives', [])
#             },
#             'quick_tips': generate_quick_tips(analysis_results, risk_score['level'])
#         }
        
#         return JSONResponse(content=response)
        
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         print(f"Error in manual_entry: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @router.get("/history")
# async def get_scan_history(current_user: dict = Depends(get_current_user_dependency)
# ):
#     """Get user's scan history"""
#     try:
#         user_id = current_user["user_id"]
        
#     from database.db_connection import get_db
# db = get_db()

          
#         # Initialize lists
#         scans = []
#         manual_entries = []
        
#         # Get scans if collection exists
#         if 'scans' in db.list_collection_names():
#             scans_cursor = db.scans.find(
#                 {'user_id': user_id},
#                 {'_id': 0, 'scan_id': 1, 'timestamp': 1, 'filename': 1, 'risk_score.level': 1, 'risk_score.color': 1, 'ingredients': 1}
#             ).sort('timestamp', -1).limit(20)
#             scans = list(scans_cursor)
        
#         # Get manual entries if collection exists
#         if 'manual_entries' in db.list_collection_names():
#             manual_cursor = db.manual_entries.find(
#                 {'user_id': user_id},
#                 {'_id': 0, 'entry_id': 1, 'timestamp': 1, 'risk_score.level': 1, 'risk_score.color': 1, 'ingredients': 1}
#             ).sort('timestamp', -1).limit(20)
#             manual_entries = list(manual_cursor)
        
#         # Combine and sort
#         history = scans + manual_entries
#         history.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        
#         return {'history': history[:20]}
        
#     except Exception as e:
#         print(f"Error in get_scan_history: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @router.get("/recent")
# async def get_recent_scans(current_user: dict = Depends(get_current_user_dependency)
# ):
#     """Get recent scans with detailed info"""
#     try:
#         user_id = current_user["user_id"]
        
#         from database.db_connection import get_db
# db = get_db()

        
#         recent_scans = []
#         if 'scans' in db.list_collection_names():
#             cursor = db.scans.find(
#                 {'user_id': user_id},
#                 {'_id': 0, 'scan_id': 1, 'timestamp': 1, 'filename': 1, 'product_type': 1, 
#                  'risk_score.level': 1, 'risk_score.color': 1, 'risk_score.score': 1}
#             ).sort('timestamp', -1).limit(5)
#             recent_scans = list(cursor)
        
#         return {'recent_scans': recent_scans}
        
#     except Exception as e:
#         print(f"Error in get_recent_scans: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# # Helper functions
# def determine_product_type(filename: str) -> str:
#     """Determine product type from filename"""
#     filename_lower = filename.lower()
    
#     if any(word in filename_lower for word in ['face', 'cream', 'moisturiz', 'lotion']):
#         return 'face_cream'
#     elif any(word in filename_lower for word in ['shampoo', 'condition', 'hair']):
#         return 'shampoo'
#     elif any(word in filename_lower for word in ['sun', 'spf', 'sunscreen']):
#         return 'sunscreen'
#     elif any(word in filename_lower for word in ['cleanse', 'wash', 'soap']):
#         return 'cleanser'
#     elif any(word in filename_lower for word in ['serum', 'treatment']):
#         return 'serum'
#     else:
#         return 'general'

# def get_mock_ingredients(product_type: str) -> str:
#     """Get mock ingredients based on product type"""
#     ingredients = PRODUCT_INGREDIENTS.get(product_type, PRODUCT_INGREDIENTS['face_cream'])
    
#     # Add some random high-risk ingredients occasionally for demo
#     import random
#     if random.random() < 0.3:  # 30% chance
#         high_risk_options = ['Paraben', 'Formaldehyde', 'Methylparaben', 'Oxybenzone']
#         ingredients.append(random.choice(high_risk_options))
    
#     return ', '.join(ingredients)

# def extract_ingredients_simple(text: str) -> List[dict]:
#     """Extract ingredients from text"""
#     # Clean text
#     text = text.lower().strip()
    
#     # Split by common separators
#     separators = [',', ';', '\n', '•', '*', '-', '. ']
#     for sep in separators:
#         text = text.replace(sep, ',')
    
#     # Split and clean
#     ingredients = []
#     for item in text.split(','):
#         item = item.strip()
#         if item and len(item) > 2 and not item.isdigit():
#             # Clean the ingredient name
#             item_clean = clean_ingredient_name(item)
#             if item_clean:
#                 # Check if ingredient is in database
#                 db_info = INGREDIENT_DATABASE.get(item_clean, {})
                
#                 ingredients.append({
#                     'original': item.title(),
#                     'normalized': item_clean,
#                     'confidence': 0.9 if db_info else 0.5,
#                     'is_known': bool(db_info),
#                     'risk': db_info.get('risk', 'unknown'),
#                     'category': db_info.get('category', 'unknown'),
#                     'concern': db_info.get('concern', False),
#                     'reason': db_info.get('reason', '')
#                 })
    
#     return ingredients

# def clean_ingredient_name(name: str) -> str:
#     """Clean ingredient name"""
#     # Remove common prefixes/suffixes
#     name = name.lower().strip()
    
#     # Remove percentages and parentheses content
#     name = re.sub(r'\([^)]*\)', '', name)  # Remove parentheses content
#     name = re.sub(r'\d+%', '', name)  # Remove percentages
#     name = re.sub(r'\d+\.?\d*', '', name)  # Remove numbers
    
#     # Remove common words
#     remove_words = ['and', 'or', 'with', 'plus', 'extract', 'oil', 'water', 'solution']
#     for word in remove_words:
#         name = name.replace(word, '')
    
#     # Clean up
#     name = re.sub(r'\s+', ' ', name)  # Remove extra spaces
#     name = name.strip(' ,.-')
    
#     return name

# def analyze_ingredients_simple(ingredients: List[dict]) -> dict:
#     """Analyze ingredients"""
#     ingredients_of_concern = []
#     generally_safe = []
#     unidentified = []
    
#     for ingredient in ingredients:
#         if ingredient.get('concern'):
#             ingredients_of_concern.append({
#                 **ingredient,
#                 'risk_level': ingredient.get('risk', 'medium'),
#                 'suggestion': get_alternative_suggestion(ingredient['normalized'])
#             })
#         elif not ingredient.get('is_known'):
#             unidentified.append({
#                 **ingredient,
#                 'note': 'Ingredient not in our database. Please research separately.'
#             })
#         else:
#             generally_safe.append(ingredient)
    
#     return {
#         'ingredients_of_concern': ingredients_of_concern,
#         'generally_safe': generally_safe,
#         'unidentified': unidentified,
#         'total_ingredients': len(ingredients),
#         'concern_count': len(ingredients_of_concern),
#         'safe_count': len(generally_safe),
#         'unknown_count': len(unidentified)
#     }

# def get_alternative_suggestion(ingredient: str) -> str:
#     """Get alternative suggestions for concerning ingredients"""
#     suggestions = {
#         'sodium laureth sulfate': 'Try sulfate-free surfactants like Decyl Glucoside',
#         'sodium lauryl sulfate': 'Try gentle surfactants like Cocamidopropyl Betaine',
#         'fragrance': 'Choose fragrance-free or naturally scented products',
#         'parfum': 'Look for "fragrance-free" labeled products',
#         'alcohol': 'Use alcohol-free toners and products',
#         'paraben': 'Look for paraben-free preservatives',
#         'formaldehyde': 'Avoid formaldehyde-releasing preservatives',
#         'oxybenzone': 'Use mineral sunscreens with Zinc Oxide instead'
#     }
#     return suggestions.get(ingredient, 'Consider looking for products without this ingredient')

# def calculate_risk_score_simple(analysis: dict) -> dict:
#     """Calculate risk score"""
#     concern_count = analysis.get('concern_count', 0)
#     total_count = analysis.get('total_ingredients', 1)
    
#     risk_percentage = (concern_count / total_count) * 100
    
#     if concern_count == 0:
#         level = 'low'
#         color = 'green'
#         score = 95
#         recommendation = 'This product appears safe for most users'
#     elif risk_percentage < 20:
#         level = 'low'
#         color = 'green'
#         score = 75
#         recommendation = 'Generally safe with minor concerns'
#     elif risk_percentage < 40:
#         level = 'medium'
#         color = 'yellow'
#         score = 50
#         recommendation = 'Use with caution, moderate concerns detected'
#     else:
#         level = 'high'
#         color = 'red'
#         score = 25
#         recommendation = 'High risk ingredients detected. Consider alternatives.'
    
#     # Get primary concerns
#     primary_concerns = []
#     for ingredient in analysis.get('ingredients_of_concern', []):
#         if ingredient.get('risk_level') in ['high', 'medium']:
#             primary_concerns.append({
#                 'name': ingredient['original'],
#                 'risk': ingredient['risk_level'],
#                 'reason': ingredient.get('reason', 'Potential concern')
#             })
    
#     # Get alternatives
#     alternatives = []
#     for ingredient in analysis.get('ingredients_of_concern', [])[:2]:
#         if ingredient.get('suggestion'):
#             alternatives.append(ingredient['suggestion'])
    
#     return {
#         'level': level,
#         'color': color,
#         'score': score,
#         'primary_concerns': primary_concerns[:3],
#         'recommendation': recommendation,
#         'alternatives': alternatives,
#         'percentage': risk_percentage
#     }

# def generate_quick_tips(analysis: dict, risk_level: str) -> List[str]:
#     """Generate quick tips"""
#     tips = []
    
#     if risk_level == 'high':
#         tips.append("⚠️ **High Risk Detected**: Consider avoiding this product or consulting with a healthcare professional")
#     elif risk_level == 'medium':
#         tips.append("⚠️ **Moderate Risk**: Use with caution, especially if you have sensitive skin")
    
#     # Add tips based on ingredients
#     for ingredient in analysis.get('ingredients_of_concern', []):
#         name = ingredient.get('original', '').lower()
#         if 'fragrance' in name or 'parfum' in name:
#             tips.append("🌿 **Fragrance Alert**: Can cause skin irritation. Look for fragrance-free options.")
#             break
    
#     for ingredient in analysis.get('ingredients_of_concern', []):
#         name = ingredient.get('original', '').lower()
#         if 'alcohol' in name:
#             tips.append("💧 **Alcohol Warning**: May dry out skin. Consider alcohol-free alternatives.")
#             break
    
#     if analysis.get('unknown_count', 0) > 0:
#         tips.append("🔍 **Unknown Ingredients**: Some ingredients not in our database. Research separately.")
    
#     if risk_level == 'low':
#         tips.append("✅ **Good Choice**: This product appears to be generally safe based on our analysis")
    
#     # Add general tips
#     if len(tips) < 3:
#         tips.append("📝 **Tip**: Always patch test new products on a small area first")
    
#     return tips[:5]

# # File serving endpoint
# @router.get("/uploads/scans/{filename}")
# async def serve_scan_image(filename: str):
#     """Serve uploaded scan images"""
#     filepath = UPLOAD_DIR / filename
#     if filepath.exists():
#         return FileResponse(filepath)
#     raise HTTPException(status_code=404, detail="Image not found")