#!/usr/bin/env python3
"""
Recipe Parser - Main Script

Transforms plain-text recipes into structured, machine-readable JSON format
using Google's LangExtract library.
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from Recipe_Extractor_Demo import RecipeExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def parse_recipe(input_file: Path, output_dir: Path, api_key: str, model: str) -> bool:
    """Parse a recipe from a text file and save the results.
    
    Args:
        input_file: Path to the input text file containing the recipe
        output_dir: Directory to save the output files
        api_key: API key for the language model
        model: The model to use for extraction
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the input file
        logger.info(f"Reading recipe from: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            recipe_text = f.read()
        
        if not recipe_text.strip():
            logger.error("Input file is empty")
            return False
        
        logger.info(f"Recipe text length: {len(recipe_text)} characters")
        
        # Initialize the extractor
        extractor = RecipeExtractor(api_key=api_key, model=model)
        
        # Extract the recipe
        logger.info("Extracting recipe structure...")
        recipe = extractor.extract_recipe(recipe_text)
        
        if not recipe:
            logger.error("Failed to extract recipe from the text")
            return False
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename based on recipe title
        safe_title = "".join(c for c in recipe.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()
        if not safe_title:
            safe_title = input_file.stem
        
        # Save the JSON output
        json_file = output_dir / f"{safe_title}.json"
        logger.info(f"Saving structured recipe to: {json_file}")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(recipe.model_dump(), f, indent=2, ensure_ascii=False)
        
        # Create a simple HTML visualization
        html_file = output_dir / f"{safe_title}.html"
        logger.info(f"Creating HTML visualization: {html_file}")
        
        html_content = generate_html_visualization(recipe, recipe_text)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Print summary
        print(f"\n✅ Recipe successfully parsed!")
        print(f"📝 Title: {recipe.title}")
        print(f"⏱️  Prep Time: {recipe.prep_time}")
        print(f"🔥 Cook Time: {recipe.cook_time}")
        print(f"🍽️  Servings: {recipe.servings}")
        print(f"🥘 Ingredients: {len(recipe.ingredients)}")
        print(f"📋 Instructions: {len(recipe.instructions)} steps")
        print(f"\n📄 Output files:")
        print(f"   - JSON: {json_file}")
        print(f"   - HTML: {html_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error parsing recipe: {str(e)}", exc_info=True)
        return False


def generate_html_visualization(recipe, original_text):
    """Generate a simple HTML visualization of the parsed recipe.
    
    Args:
        recipe: The parsed Recipe object
        original_text: The original recipe text
        
    Returns:
        HTML content as a string
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{recipe.title} - Parsed Recipe</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        .panel {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        h2 {{
            color: #666;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 5px;
        }}
        .meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #666;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .description {{
            font-style: italic;
            color: #666;
            margin-bottom: 20px;
        }}
        .ingredient {{
            display: flex;
            gap: 10px;
            margin-bottom: 8px;
            padding: 8px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .quantity {{
            font-weight: bold;
            color: #2196F3;
            min-width: 50px;
        }}
        .unit {{
            color: #666;
            min-width: 50px;
        }}
        .name {{
            flex: 1;
        }}
        .instruction {{
            margin-bottom: 15px;
            padding-left: 30px;
            position: relative;
        }}
        .instruction::before {{
            content: counter(step);
            counter-increment: step;
            position: absolute;
            left: 0;
            top: 0;
            background: #2196F3;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }}
        .instructions {{
            counter-reset: step;
        }}
        .original-text {{
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            color: #444;
        }}
        @media (max-width: 768px) {{
            .container {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="panel">
            <h1>{recipe.title}</h1>
            
            <div class="meta">
                <div class="meta-item">⏱️ Prep: {recipe.prep_time}</div>
                <div class="meta-item">🔥 Cook: {recipe.cook_time}</div>
                <div class="meta-item">🍽️ Servings: {recipe.servings}</div>
            </div>
            
            <p class="description">{recipe.description}</p>
            
            <h2>Ingredients</h2>
            <div class="ingredients">
"""
    
    for ing in recipe.ingredients:
        quantity_str = f"{ing.quantity}" if ing.quantity is not None else ""
        unit_str = ing.unit if ing.unit else ""
        html += f"""
                <div class="ingredient">
                    <span class="quantity">{quantity_str}</span>
                    <span class="unit">{unit_str}</span>
                    <span class="name">{ing.name}</span>
                </div>
"""
    
    html += """
            </div>
            
            <h2>Instructions</h2>
            <div class="instructions">
"""
    
    for instruction in recipe.instructions:
        html += f"""
                <div class="instruction">{instruction}</div>
"""
    
    html += f"""
            </div>
        </div>
        
        <div class="panel">
            <h2>Original Recipe Text</h2>
            <div class="original-text">{original_text}</div>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Main entry point for the recipe parser."""
   

    # Get API key
    api_key = os.getenv("LANGEXTRACT_API_KEY")
    if not api_key:
        logger.error("API key not provided. Set LANGEXTRACT_API_KEY env var or use --api-key")
        sys.exit(1)
    
    # Parse the recipe
    success = parse_recipe(
        input_file="recipe.txt",
        output_dir=Path("./output"),
        api_key=api_key,
        model="gemini-2.5-flash"
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    print("Starting recipe extraction...")
    main()