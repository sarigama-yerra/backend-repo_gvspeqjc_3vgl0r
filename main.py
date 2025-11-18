import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Literal
from bson import ObjectId

app = FastAPI(title="Bespoke Cakes API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Models (mirror of schemas.Cake for responses) -----
class PriceAdjust(BaseModel):
    label: str
    amount: float

class CakeOption(BaseModel):
    name: Literal["Size", "Flavor", "Filling", "Frosting"]
    values: List[PriceAdjust]

class CakeOut(BaseModel):
    id: str
    slug: str
    name: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    category: Literal["Wedding", "Birthday", "Signature", "Corporate", "Seasonal"]
    base_price: float
    image_url: Optional[str] = None
    model_url: Optional[str] = None
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    options: Optional[List[CakeOption]] = None
    featured: bool = False

# ----- Helpers -----
def slugify(name: str) -> str:
    return "-".join(name.lower().strip().split())


def to_cake_out(doc) -> CakeOut:
    return CakeOut(
        id=str(doc.get("_id")),
        slug=doc.get("slug") or slugify(doc.get("name", "cake")),
        name=doc.get("name"),
        tagline=doc.get("tagline"),
        description=doc.get("description"),
        category=doc.get("category", "Signature"),
        base_price=float(doc.get("base_price", 0)),
        image_url=doc.get("image_url"),
        model_url=doc.get("model_url"),
        ingredients=doc.get("ingredients"),
        allergens=doc.get("allergens"),
        options=doc.get("options"),
        featured=bool(doc.get("featured", False)),
    )


# ----- Database bootstrap -----

def ensure_seed_data():
    try:
        from database import db
        if db is None:
            return
        col = db["cake"]
        if col.count_documents({}) == 0:
            samples = [
                {
                    "name": "Madagascar Vanilla Classic",
                    "slug": "madagascar-vanilla-classic",
                    "tagline": "Where elegance meets comfort.",
                    "description": "Moist Madagascar vanilla sponge layered with house-made salted caramel and finished with French buttercream.",
                    "category": "Signature",
                    "base_price": 75.0,
                    "image_url": "https://images.unsplash.com/photo-1559622214-3f1b2c6e49a5?q=80&w=1200&auto=format&fit=crop",
                    "model_url": None,
                    "ingredients": ["Flour", "Sugar", "Butter", "Eggs", "Vanilla"],
                    "allergens": ["Dairy", "Eggs", "Gluten"],
                    "options": [
                        {
                            "name": "Size",
                            "values": [
                                {"label": "6\" (8 servings)", "amount": 0},
                                {"label": "8\" (14 servings)", "amount": 25},
                                {"label": "10\" (24 servings)", "amount": 60},
                            ],
                        },
                        {
                            "name": "Frosting",
                            "values": [
                                {"label": "French Buttercream", "amount": 0},
                                {"label": "Swiss Meringue", "amount": 8},
                                {"label": "Ganache", "amount": 12},
                            ],
                        },
                    ],
                    "featured": True,
                },
                {
                    "name": "Dark Cocoa Truffle",
                    "slug": "dark-cocoa-truffle",
                    "tagline": "For the true chocolate purist.",
                    "description": "Rich dark chocolate sponge, layered with silky truffle ganache.",
                    "category": "Signature",
                    "base_price": 85.0,
                    "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?q=80&w=1200&auto=format&fit=crop",
                    "model_url": None,
                    "ingredients": ["Cocoa", "Butter", "Sugar", "Eggs", "Cream"],
                    "allergens": ["Dairy", "Eggs", "Gluten"],
                    "options": [
                        {
                            "name": "Size",
                            "values": [
                                {"label": "6\" (8 servings)", "amount": 0},
                                {"label": "8\" (14 servings)", "amount": 28},
                                {"label": "10\" (24 servings)", "amount": 65},
                            ],
                        },
                        {
                            "name": "Filling",
                            "values": [
                                {"label": "Truffle Ganache", "amount": 0},
                                {"label": "Raspberry Compote", "amount": 6},
                            ],
                        },
                    ],
                    "featured": True,
                },
                {
                    "name": "Berry Velvet",
                    "slug": "berry-velvet",
                    "tagline": "A jewel-toned celebration.",
                    "description": "Vanilla sponge, berry compote, mascarpone frosting.",
                    "category": "Birthday",
                    "base_price": 78.0,
                    "image_url": "https://images.unsplash.com/photo-1562777717-dc6984f65a63?q=80&w=1200&auto=format&fit=crop",
                    "model_url": None,
                    "ingredients": ["Flour", "Sugar", "Eggs", "Mascarpone", "Berries"],
                    "allergens": ["Dairy", "Eggs", "Gluten"],
                    "options": [
                        {
                            "name": "Frosting",
                            "values": [
                                {"label": "Mascarpone", "amount": 0},
                                {"label": "Buttercream", "amount": 5},
                            ],
                        }
                    ],
                    "featured": False,
                },
            ]
            col.insert_many(samples)
    except Exception:
        # Swallow errors to keep API running even if DB not available
        pass


ensure_seed_data()


@app.get("/")
def read_root():
    return {"message": "Bespoke Cakes API running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ----- Cakes Endpoints -----
@app.get("/cakes", response_model=List[CakeOut])
def list_cakes(category: Optional[str] = None, featured: Optional[bool] = None):
    from database import db
    if db is None:
        # Return static fallback if no DB
        results = ensure_static_fallback()
        return results
    query = {}
    if category:
        query["category"] = category
    if featured is not None:
        query["featured"] = featured
    docs = list(db["cake"].find(query))
    return [to_cake_out(d) for d in docs]


@app.get("/cakes/{slug}", response_model=CakeOut)
def get_cake(slug: str):
    from database import db
    if db is None:
        for c in ensure_static_fallback():
            if c.slug == slug:
                return c
        raise HTTPException(status_code=404, detail="Cake not found")
    doc = db["cake"].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Cake not found")
    return to_cake_out(doc)


# Static fallback when DB not configured
_def_fallback = [
    {
        "name": "Madagascar Vanilla Classic",
        "slug": "madagascar-vanilla-classic",
        "tagline": "Where elegance meets comfort.",
        "description": "Moist Madagascar vanilla sponge layered with house-made salted caramel and finished with French buttercream.",
        "category": "Signature",
        "base_price": 75.0,
        "image_url": "https://images.unsplash.com/photo-1559622214-3f1b2c6e49a5?q=80&w=1200&auto=format&fit=crop",
        "model_url": None,
        "featured": True,
    },
    {
        "name": "Dark Cocoa Truffle",
        "slug": "dark-cocoa-truffle",
        "tagline": "For the true chocolate purist.",
        "description": "Rich dark chocolate sponge, layered with silky truffle ganache.",
        "category": "Signature",
        "base_price": 85.0,
        "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?q=80&w=1200&auto=format&fit=crop",
        "model_url": None,
        "featured": True,
    },
]


def ensure_static_fallback() -> List[CakeOut]:
    return [
        CakeOut(
            id=str(i),
            slug=doc["slug"],
            name=doc["name"],
            tagline=doc.get("tagline"),
            description=doc.get("description"),
            category=doc.get("category", "Signature"),
            base_price=doc.get("base_price", 0),
            image_url=doc.get("image_url"),
            model_url=doc.get("model_url"),
            ingredients=None,
            allergens=None,
            options=None,
            featured=doc.get("featured", False),
        )
        for i, doc in enumerate(_def_fallback)
    ]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
