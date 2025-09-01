"""
Recipe data models for the Recipe Parser.

This module defines the Pydantic models used to structure recipe data
extracted from unstructured text using LangExtract.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """A structured representation of a single ingredient."""
    
    name: str = Field(
        description="The name of the ingredient, e.g., 'all-purpose flour'"
    )
    quantity: Optional[float] = Field(
        default=None,
        description="The numeric quantity, e.g., 2.5"
    )
    unit: Optional[str] = Field(
        default=None,
        description="The unit of measurement, e.g., 'cups', 'grams', 'tbsp'"
    )


class Recipe(BaseModel):
    """The top-level schema for the entire recipe."""
    
    title: str = Field(
        description="The title of the recipe, e.g., 'Classic Chocolate Chip Cookies'"
    )
    description: str = Field(
        description="The introductory description or summary of the recipe"
    )
    prep_time: str = Field(
        description="The preparation time, e.g., '15 minutes'"
    )
    cook_time: str = Field(
        description="The cooking/baking time, e.g., '12 minutes'"
    )
    servings: str = Field(
        description="The yield of the recipe, e.g., '24 cookies'"
    )
    ingredients: List[Ingredient] = Field(
        description="A list of all ingredients, structured using the Ingredient model"
    )
    instructions: List[str] = Field(
        description="An ordered list of the cooking steps"
    )