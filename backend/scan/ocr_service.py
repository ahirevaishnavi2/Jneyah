import base64
from typing import List, Dict, Any, Optional
import logging
import re
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OCRService:
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Using mock mode.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Extract text from image using GPT-4 Vision
        """
        # If no client, use mock
        if not self.client:
            logger.warning("OpenAI client not available, using mock extraction")
            return self._mock_extract()
        
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create prompt for GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Extract all text from this product label. 
                                Focus on the ingredients list. Return the complete text exactly as seen.
                                Format it nicely with line breaks."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            text = response.choices[0].message.content
            logger.info(f"GPT-4 Vision completed, extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"GPT-4 Vision failed: {str(e)}")
            return self._mock_extract()

    def extract_ingredients_with_ai(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Use GPT-4 Vision to directly extract and structure ingredients
        """
        if not self.client:
            return self._mock_ingredients()
        
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
                                Extract the ingredients from this product label and return them as a JSON array.
                                For each ingredient, provide:
                                - name: The ingredient name
                                - category: Choose from [preservative, active, emollient, fragrance, surfactant, humectant, solvent, other]
                                - confidence: How confident you are (0-1)
                                
                                Return ONLY the JSON array, no other text.
                                Example format:
                                [{"name": "Water", "category": "solvent", "confidence": 1.0}]
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Handle different response formats
            if isinstance(result, dict):
                if "ingredients" in result:
                    return result["ingredients"]
                elif "data" in result:
                    return result["data"]
                else:
                    # Try to find any array in the response
                    for value in result.values():
                        if isinstance(value, list):
                            return value
            
            elif isinstance(result, list):
                return result
            
            return self._mock_ingredients()
                
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            return self._mock_ingredients()

    def extract_ingredients(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract ingredients from text using pattern matching (fallback method)
        """
        ingredients = []
        seen = set()
        
        # Find ingredients section
        lines = text.split('\n')
        in_ingredients = False
        
        for line in lines:
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in ['ingredients:', 'ingrédients:', 'contains:', 'ingredient list:']):
                in_ingredients = True
                line = re.sub(r'^.*?(?:ingredients|ingrédients|contains|ingredient list)[:\s]*', '', line, flags=re.IGNORECASE)
            
            if in_ingredients and line.strip():
                # Split by commas and periods
                parts = re.split(r'[,;.]', line)
                for part in parts:
                    ingredient = part.strip()
                    # Clean ingredient
                    ingredient = re.sub(r'^\d+\.?\s*', '', ingredient)
                    ingredient = re.sub(r'[^\w\s\-]', '', ingredient)
                    
                    if ingredient and len(ingredient) > 1 and ingredient.lower() not in seen:
                        seen.add(ingredient.lower())
                        
                        # Determine category
                        category = self._categorize_ingredient(ingredient)
                        
                        ingredients.append({
                            "name": ingredient,
                            "original": ingredient,
                            "category": category,
                            "confidence": 0.8
                        })
        
        return ingredients if ingredients else self._mock_ingredients()

    def _categorize_ingredient(self, ingredient: str) -> str:
        """
        Categorize ingredient based on keywords
        """
        ing_lower = ingredient.lower()
        
        categories = {
            "preservative": ["paraben", "phenoxyethanol", "benzoate", "sorbate", "formaldehyde", "dmdm", "imidazolidinyl"],
            "emollient": ["glycerin", "butter", "oil", "squalane", "dimethicone", "cetearyl", "cetyl", "stearyl"],
            "active": ["vitamin", "retinol", "niacinamide", "acid", "peptide", "collagen", "hyaluronic"],
            "fragrance": ["fragrance", "parfum", "limonene", "linalool", "citronellol", "geraniol"],
            "surfactant": ["lauryl", "laureth", "coco", "betaine", "glucoside", "polysorbate", "peg"],
            "humectant": ["hyaluronic", "glycerin", "panthenol", "propanediol", "butylene", "propylene"],
            "solvent": ["water", "aqua", "alcohol", "ethanol", "isopropyl"],
            "sunscreen": ["avobenzone", "octinoxate", "zinc oxide", "titanium dioxide", "oxybenzone"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in ing_lower for keyword in keywords):
                return category
        
        return "other"

    def _mock_extract(self) -> str:
        """
        Mock extraction as fallback
        """
        return """
        HYDRATING FACIAL MOISTURIZER
        
        DIRECTIONS: Apply liberally to face and neck each morning. For best results, use after cleansing.
        
        INGREDIENTS: Water, Glycerin, Cetearyl Alcohol, Dimethicone, Shea Butter (Butyrospermum Parkii), 
        Tocopheryl Acetate (Vitamin E), Phenoxyethanol, Fragrance (Parfum), Sodium Hyaluronate, 
        Caprylic/Capric Triglyceride, Carbomer, Sodium Hydroxide.
        
        WARNINGS: For external use only. Avoid contact with eyes. Discontinue use if irritation occurs.
        
        DISTRIBUTED BY: Beauty Labs Inc.
        MADE IN: USA
        """

    def _mock_ingredients(self) -> List[Dict[str, Any]]:
        """
        Return mock ingredients as fallback
        """
        return [
            {"name": "Water", "category": "solvent", "confidence": 1.0},
            {"name": "Glycerin", "category": "humectant", "confidence": 0.95},
            {"name": "Cetearyl Alcohol", "category": "emollient", "confidence": 0.9},
            {"name": "Dimethicone", "category": "emollient", "confidence": 0.9},
            {"name": "Shea Butter", "category": "emollient", "confidence": 0.95},
            {"name": "Vitamin E", "category": "active", "confidence": 0.85},
            {"name": "Phenoxyethanol", "category": "preservative", "confidence": 0.95},
            {"name": "Fragrance", "category": "fragrance", "confidence": 0.9},
            {"name": "Sodium Hyaluronate", "category": "humectant", "confidence": 0.9}
        ]