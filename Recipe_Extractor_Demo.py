"""
Recipe extraction engine using Google's LangExtract.

This module handles the core extraction logic, converting unstructured
recipe text into structured Recipe objects.
"""
import logging
import json
from typing import Optional
import langextract as lx
from langextract.data import ExampleData, Extraction

from Models import Recipe, Ingredient

logger = logging.getLogger(__name__)


class RecipeExtractor:
    """Extracts structured recipe data from unstructured text using LangExtract."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """Initialize the recipe extractor.
        
        Args:
            api_key: API key for the language model
            model: The model to use for extraction
        """
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized RecipeExtractor with model: {model}")
    
    def extract_recipe(self, text: str) -> Optional[Recipe]:
        """Extract recipe information from text.
        
        Args:
            text: The raw recipe text
            
        Returns:
            A Recipe object with extracted information, or None if extraction fails
        """
        logger.info(f"Extracting recipe from text (length: {len(text)} chars)")
        
        if len(text.strip()) < 100:
            logger.warning("Text too short for meaningful recipe extraction")
            return None
        
        try:
            # Define the prompt for extraction
            prompt_description = """
            Extract recipe information from the provided text. 

            Identify and extract:
            1. The recipe title
            2. A brief description or summary
            3. Preparation time
            4. Cooking/baking time
            5. Number of servings or yield
            6. All ingredients with their quantities and units
            7. Step-by-step instructions

            For ingredients, break down each one into:
            - name: the ingredient name (e.g., "all-purpose flour")
            - quantity: the numeric amount (e.g., 2.5)
            - unit: the measurement unit (e.g., "cups")

            Return the extracted information in the following JSON structure:
            {
            "extractions": [
                {
                "extraction_class": "Recipe",
                "extraction_text": "{
                    \\"title\\": \\"Recipe Title\\",
                    \\"description\\": \\"Brief description\\",
                    \\"prep_time\\": \\"15 minutes\\",
                    \\"cook_time\\": \\"30 minutes\\",
                    \\"servings\\": \\"4 servings\\",
                    \\"ingredients\\": [
                    {
                        \\"name\\": \\"ingredient name\\",
                        \\"quantity\\": 2.0,
                        \\"unit\\": \\"cups\\"
                    }
                    ],
                    \\"instructions\\": [
                    \\"Step 1 text\\",
                    \\"Step 2 text\\"
                    ]
                }"
                }
            ]
            }
            """
            
            # Create example data to guide the extraction
            examples = [
                ExampleData(
                    text="""
                    Chocolate Chip Cookies

                    These are the best chocolate chip cookies you'll ever make! Crispy on the outside and chewy on the inside.

                    Prep Time: 15 minutes
                    Cook Time: 12 minutes
                    Yield: 24 cookies

                    Ingredients:
                    - 2 1/4 cups all-purpose flour
                    - 1 tsp baking soda
                    - 1 tsp salt
                    - 1 cup butter, softened
                    - 3/4 cup granulated sugar
                    - 3/4 cup packed brown sugar
                    - 2 large eggs
                    - 2 tsp vanilla extract
                    - 2 cups chocolate chips

                    Instructions:
                    1. Preheat oven to 375°F.
                    2. In a bowl, combine flour, baking soda, and salt.
                    3. In another bowl, beat butter and sugars until creamy.
                    4. Add eggs and vanilla to butter mixture; mix well.
                    5. Gradually stir in flour mixture.
                    6. Stir in chocolate chips.
                    7. Drop by rounded tablespoon onto ungreased cookie sheets.
                    8. Bake 9-11 minutes or until golden brown.
                    """,
                    extractions=[
                        Extraction(
                            extraction_class="Recipe",
                            extraction_text="""{
                            "title": "Chocolate Chip Cookies",
                            "description": "These are the best chocolate chip cookies you'll ever make! Crispy on the outside and chewy on the inside.",
                            "prep_time": "15 minutes",
                            "cook_time": "12 minutes",
                            "servings": "24 cookies",
                            "ingredients": [
                                {"name": "all-purpose flour", "quantity": 2.25, "unit": "cups"},
                                {"name": "baking soda", "quantity": 1.0, "unit": "tsp"},
                                {"name": "salt", "quantity": 1.0, "unit": "tsp"},
                                {"name": "butter, softened", "quantity": 1.0, "unit": "cup"},
                                {"name": "granulated sugar", "quantity": 0.75, "unit": "cup"},
                                {"name": "packed brown sugar", "quantity": 0.75, "unit": "cup"},
                                {"name": "eggs", "quantity": 2.0, "unit": "large"},
                                {"name": "vanilla extract", "quantity": 2.0, "unit": "tsp"},
                                {"name": "chocolate chips", "quantity": 2.0, "unit": "cups"}
                            ],
                            "instructions": [
                                "Preheat oven to 375°F.",
                                "In a bowl, combine flour, baking soda, and salt.",
                                "In another bowl, beat butter and sugars until creamy.",
                                "Add eggs and vanilla to butter mixture; mix well.",
                                "Gradually stir in flour mixture.",
                                "Stir in chocolate chips.",
                                "Drop by rounded tablespoon onto ungreased cookie sheets.",
                                "Bake 9-11 minutes or until golden brown."
                            ]
                            }"""
                        )
                    ]
                )
            ]
            
            # Perform extraction
            result = lx.extract(
                text_or_documents=text,
                prompt_description=prompt_description,
                model_id=self.model,
                examples=examples,
                api_key=self.api_key
            )
            
            # Parse the results
            if result and hasattr(result, 'extractions') and result.extractions:
                for extraction in result.extractions:
                    if extraction.extraction_class == "Recipe":
                        try:
                            # Parse the JSON string into a Recipe object
                            recipe_data = json.loads(extraction.extraction_text)
                            
                            # Skip partial extractions (e.g., from later chunks)
                            if not recipe_data.get('title'):
                                logger.debug("Skipping partial extraction without title")
                                continue
                            
                            # Convert ingredient dictionaries to Ingredient objects
                            ingredients = []
                            for ing in recipe_data.get('ingredients', []):
                                # Handle ingredients with missing quantity or unit
                                ingredient = Ingredient(
                                    name=ing.get('name', ''),
                                    quantity=ing.get('quantity'),
                                    unit=ing.get('unit')
                                )
                                ingredients.append(ingredient)
                            
                            # Create the Recipe object
                            recipe = Recipe(
                                title=recipe_data.get('title', ''),
                                description=recipe_data.get('description', ''),
                                prep_time=recipe_data.get('prep_time', ''),
                                cook_time=recipe_data.get('cook_time', ''),
                                servings=recipe_data.get('servings', ''),
                                ingredients=ingredients,
                                instructions=recipe_data.get('instructions', [])
                            )
                            
                            logger.info(f"Successfully extracted recipe: {recipe.title}")
                            logger.info(f"  - {len(recipe.ingredients)} ingredients")
                            logger.info(f"  - {len(recipe.instructions)} instructions")
                            
                            return recipe
                            
                        except Exception as e:
                            logger.error(f"Error parsing recipe extraction: {e}")
                            logger.error(f"Extraction text: {extraction.extraction_text}")
            
            logger.warning("No recipe extractions found in the result")
            return None
            
        except Exception as e:
            logger.error(f"Error during recipe extraction: {str(e)}", exc_info=True)
            return None