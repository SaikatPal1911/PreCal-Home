from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


# ─── AUTH ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


# ─── ANALYSIS ────────────────────────────────────────────────────────────────

class MeasurementsIn(BaseModel):
    # Painting / walls
    wallLength: Optional[float] = None
    wallHeight: Optional[float] = None
    numWalls: Optional[int] = None
    numDoorsInWall: Optional[int] = None
    numWindowsInWall: Optional[int] = None
    # Ceiling
    ceilingLength: Optional[float] = None
    ceilingWidth: Optional[float] = None
    ceilingType: Optional[str] = None
    # Doors
    doorHeight: Optional[float] = None
    doorWidth: Optional[float] = None
    numDoors: Optional[int] = None
    # Windows
    windowHeight: Optional[float] = None
    windowWidth: Optional[float] = None
    numWindows: Optional[int] = None
    # Furniture
    furnitureType: Optional[str] = None
    furnitureLength: Optional[float] = None
    furnitureWidth: Optional[float] = None
    furnitureHeight: Optional[float] = None
    numFurnitureUnits: Optional[int] = None
    unit: Optional[str] = "meters"

class PreferencesIn(BaseModel):
    colorPalette: Optional[str] = None
    designStyle: Optional[str] = None
    specialRequirements: Optional[str] = None
    preferredMaterial: Optional[str] = None

class AnalysisRequest(BaseModel):
    category: str          # painting | ceiling | doors | windows | furniture
    budget: str            # luxury | moderate | budget
    propertyType: str      # urban | rural
    measurements: MeasurementsIn = Field(default_factory=MeasurementsIn)
    preferences: PreferencesIn = Field(default_factory=PreferencesIn)
    imageUrl: Optional[str] = None

class MaterialItemOut(BaseModel):
    id: str
    name: str
    specification: str
    quantity: float
    unit: str
    unitPrice: float
    totalPrice: float

class BudgetBreakdownOut(BaseModel):
    material: float
    labour: float
    transport: float
    misc: float
    contingency: float
    total: float

class DesignRecommendationOut(BaseModel):
    title: str
    label: str
    description: str
    primaryColor: Optional[str] = None
    primaryColorHex: Optional[str] = None
    complementaryColors: Optional[List[Dict[str, str]]] = None
    finish: Optional[str] = None
    material: Optional[str] = None
    tags: List[str] = []

class AnalysisResultOut(BaseModel):
    id: str
    projectName: str
    category: str
    budget: str
    propertyType: str
    imagePreviewUrl: Optional[str] = None
    measurements: Dict[str, Any]
    preferences: Dict[str, Any]
    recommendations: List[DesignRecommendationOut]
    materials: List[MaterialItemOut]
    budgetBreakdown: BudgetBreakdownOut
    createdAt: str


# ─── PROJECTS ─────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    category: str
    thumbnail: Optional[str] = None
    budget: Optional[float] = None
    result: Dict[str, Any]   # full AnalysisResult JSON

class ProjectOut(BaseModel):
    id: str
    user_id: str
    name: str
    category: str
    thumbnail: Optional[str] = None
    budget: Optional[float] = None
    result: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ─── PROFESSIONALS ────────────────────────────────────────────────────────────

class ProfessionalOut(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    profession: str
    specialization: str
    serviceArea: str
    experience: int
    rating: float
    reviews: int
    startingPrice: float
    consultationFee: float
    availability: str
    verified: bool
    distance: Optional[float] = None
    portfolio: List[str] = []
    skills: List[str] = []
    services: List[str] = []
    slots: List[str] = []
    bio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ─── BOOKINGS ─────────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    professional_id: str
    customer_name: str
    phone: str
    location: str
    category: Optional[str] = None
    date: str
    time_slot: str
    requirements: Optional[str] = None

class BookingOut(BaseModel):
    id: str
    professional_id: str
    customer_name: str
    phone: str
    location: str
    category: Optional[str] = None
    date: str
    time_slot: str
    requirements: Optional[str] = None
    reference_number: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ─── IMAGE UPLOAD ─────────────────────────────────────────────────────────────

class ImageUploadOut(BaseModel):
    id: str
    filename: str
    url: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
