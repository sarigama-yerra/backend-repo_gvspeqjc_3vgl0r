"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Bespoke Cakes Schema
class PriceAdjust(BaseModel):
    label: str
    amount: float = Field(0, ge=0)

class CakeOption(BaseModel):
    name: Literal["Size", "Flavor", "Filling", "Frosting"]
    values: List[PriceAdjust]

class Cake(BaseModel):
    """
    Cakes collection schema
    Collection name: "cake"
    """
    name: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    category: Literal["Wedding", "Birthday", "Signature", "Corporate", "Seasonal"] = "Signature"
    base_price: float = Field(..., ge=0)
    image_url: Optional[str] = None
    model_url: Optional[str] = Field(None, description="URL to GLB/GLTF model")
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    options: Optional[List[CakeOption]] = None
    featured: bool = False
