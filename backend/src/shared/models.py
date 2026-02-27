from dataclasses import dataclass


@dataclass
class Ingredient:
    name: str
    quantity: float
    unit: str


@dataclass
class Instruction:
    step: str
    description: str
    notes: str


@dataclass
class Recipe:
    name: str
    description: str
    total_time: int
    servings: int
    ingredients: list[Ingredient]
    is_vegetarian: bool
    is_gluten_free: bool
    is_nut_free: bool
    is_dairy_free: bool
    instructions: list[Instruction]
    image_url: str
    source_url: str
