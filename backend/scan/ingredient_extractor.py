import re
from typing import List, Dict, Any, Set, Optional
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class IngredientExtractor:
    
    # Known ingredient database (simplified)
    KNOWN_INGREDIENTS = {
        "paraben": "Paraben",
        "methylparaben": "Methylparaben",
        "propylparaben": "Propylparaben",
        "butylparaben": "Butylparaben",
        "ethylparaben": "Ethylparaben",
        "phenoxyethanol": "Phenoxyethanol",
        "glycerin": "Glycerin",
        "glycerol": "Glycerin",
        "vitamin c": "Vitamin C",
        "ascorbic acid": "Ascorbic Acid",
        "retinol": "Retinol",
        "niacinamide": "Niacinamide",
        "hyaluronic acid": "Hyaluronic Acid",
        "sodium hyaluronate": "Sodium Hyaluronate",
        "sodium lauryl sulfate": "Sodium Lauryl Sulfate",
        "sls": "Sodium Lauryl Sulfate",
        "fragrance": "Fragrance",
        "parfum": "Fragrance",
        "alcohol": "Alcohol",
        "alcohol denat": "Alcohol Denat",
        "zinc oxide": "Zinc Oxide",
        "titanium dioxide": "Titanium Dioxide",
        "shea butter": "Shea Butter",
        "coconut oil": "Coconut Oil",
        "jojoba oil": "Jojoba Oil",
        "dimethicone": "Dimethicone",
        "glycolic acid": "Glycolic Acid",
        "lactic acid": "Lactic Acid",
        "salicylic acid": "Salicylic Acid",
        "citric acid": "Citric Acid"
    }

    @staticmethod
    def extract_from_text(text: str) -> List[Dict[str, Any]]:
        """
        Extract ingredients from text with improved accuracy
        """
        ingredients = []
        seen = set()
        
        # Split by common delimiters
        lines = text.split('\n')
        for line in lines:
            # Look for ingredient list patterns
            if any(keyword in line.lower() for keyword in ['ingredients:', 'ingrédients:', 'contains:', 'ingredient list:']):
                ingredients.extend(IngredientExtractor.parse_ingredient_line(line))
                continue
            
            # Split by commas and periods
            parts = re.split(r'[,\.]', line)
            for part in parts:
                # Look for individual ingredients
                found = IngredientExtractor.find_ingredients_in_text(part)
                ingredients.extend(found)
        
        # Deduplicate and clean
        unique_ingredients = []
        for ing in ingredients:
            key = ing['name'].lower()
            if key not in seen:
                seen.add(key)
                unique_ingredients.append(ing)
        
        return unique_ingredients

    @staticmethod
    def parse_ingredient_line(line: str) -> List[Dict[str, Any]]:
        """
        Parse a line containing ingredient list
        """
        ingredients = []
        
        # Remove the "Ingredients:" label
        line = re.sub(r'^.*?(?:ingredients|ingrédients|contains|ingredient list)[:\s]*', '', line, flags=re.IGNORECASE)
        
        # Split by common delimiters
        parts = re.split(r'[,;\.]|\s+\|\s+', line)
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 1:
                # Check if this looks like an ingredient
                if IngredientExtractor.is_likely_ingredient(part):
                    ingredients.append({
                        "name": part,
                        "original": part,
                        "confidence": 0.9
                    })
        
        return ingredients

    @staticmethod
    def find_ingredients_in_text(text: str) -> List[Dict[str, Any]]:
        """
        Find individual ingredients within a text segment
        """
        found = []
        text_lower = text.lower()
        
        # Check known ingredients
        for key, name in IngredientExtractor.KNOWN_INGREDIENTS.items():
            if key in text_lower:
                # Extract the actual text with original casing
                pattern = re.compile(re.escape(key), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    found.append({
                        "name": name,
                        "original": match.group(),
                        "matched_key": key,
                        "confidence": 0.95
                    })
        
        # Look for INCI names (typically Latin names in parentheses)
        inci_matches = re.finditer(r'\(([^)]+)\)', text)
        for match in inci_matches:
            inci_name = match.group(1).strip()
            if len(inci_name) > 3:
                found.append({
                    "name": inci_name,
                    "original": match.group(),
                    "type": "INCI",
                    "confidence": 0.8
                })
        
        return found

    @staticmethod
    def is_likely_ingredient(text: str) -> bool:
        """
        Determine if a text segment is likely an ingredient name
        """
        # Too short
        if len(text) < 3:
            return False
        
        # Too long (probably a sentence)
        if len(text) > 50:
            return False
        
        # Contains numbers (could be percentages or concentrations)
        if re.search(r'\d+%|\d+\s*%', text):
            return False
        
        # Common ingredient patterns
        patterns = [
            r'^[A-Z][a-z]+',  # Starts with capital letter
            r'\s+[A-Z][a-z]+\s+',  # Has capitalized words
            r'[A-Z]{2,}',  # Has acronyms
            r'\w+\s+acid',  # Something acid
            r'\w+\s+oil',  # Something oil
            r'\w+\s+extract',  # Something extract
            r'\w+\s+butter',  # Something butter
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False

    @staticmethod
    def normalize_ingredient_name(name: str) -> str:
        """
        Normalize ingredient name for matching
        """
        # Convert to lowercase
        name = name.lower()
        
        # Remove common prefixes
        name = re.sub(r'^\d+\.?\s*', '', name)
        
        # Remove percentages
        name = re.sub(r'\d+%\s*', '', name)
        
        # Remove parentheses content
        name = re.sub(r'\([^)]*\)', '', name)
        
        # Remove extra spaces
        name = ' '.join(name.split())
        
        return name.strip()

    @staticmethod
    def match_ingredient(ingredient: str, threshold: float = 0.8) -> Optional[str]:
        """
        Match an ingredient to known database using fuzzy matching
        """
        normalized = IngredientExtractor.normalize_ingredient_name(ingredient)
        
        # Try exact match first
        if normalized in IngredientExtractor.KNOWN_INGREDIENTS:
            return IngredientExtractor.KNOWN_INGREDIENTS[normalized]
        
        # Try fuzzy matching
        best_match = None
        best_ratio = 0
        
        for known_key, known_name in IngredientExtractor.KNOWN_INGREDIENTS.items():
            ratio = SequenceMatcher(None, normalized, known_key).ratio()
            if ratio > best_ratio and ratio > threshold:
                best_ratio = ratio
                best_match = known_name
        
        return best_match