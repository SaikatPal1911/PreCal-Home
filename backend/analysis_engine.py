"""
PreCal Home – Python Analysis Engine
Ports the TypeScript mock analysis logic to a real Python backend.
Computes materials, budget breakdown, and design recommendations
based on category, budget, property type, and measurements.
"""
import math
import uuid
from datetime import datetime
from typing import Optional

from schemas import (
    AnalysisRequest, AnalysisResultOut,
    MaterialItemOut, BudgetBreakdownOut, DesignRecommendationOut,
)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:6]}"


def _mult(base: float, budget: str, luxury=1.8, moderate=1.2) -> float:
    if budget == "luxury":
        return round(base * luxury)
    elif budget == "moderate":
        return round(base * moderate)
    return round(base)


# ─── MATERIAL BUILDERS ───────────────────────────────────────────────────────

def _painting_materials(area: float, budget: str) -> list[MaterialItemOut]:
    liters = math.ceil(area / 10)
    primer_spec = {
        "luxury": "Asian Paints Damp Shield",
        "moderate": "Berger All Guard Primer",
    }.get(budget, "Generic White Primer")
    paint_spec = {
        "luxury": "Asian Paints Royale Matt",
        "moderate": "Berger Silk Breathe Easy",
    }.get(budget, "Asian Paints Tractor Emulsion")

    def up(base): return _mult(base, budget)

    primer_qty = math.ceil(liters * 0.5)
    putty_qty = math.ceil(area * 1.2)
    sand_qty = math.ceil(area / 15)
    tape_qty = math.ceil(area / 20)

    return [
        MaterialItemOut(id="m1", name="Premium Primer", specification=primer_spec,
                        quantity=primer_qty, unit="Litre",
                        unitPrice=up(180), totalPrice=primer_qty * up(180)),
        MaterialItemOut(id="m2", name="Interior Emulsion Paint", specification=paint_spec,
                        quantity=liters, unit="Litre",
                        unitPrice=up(220), totalPrice=liters * up(220)),
        MaterialItemOut(id="m3", name="Wall Putty / Filler", specification="Birla White WallCare Putty",
                        quantity=putty_qty, unit="kg",
                        unitPrice=28, totalPrice=putty_qty * 28),
        MaterialItemOut(id="m4", name="Sandpaper (180 Grit)", specification="Norton Sandpaper Sheet",
                        quantity=sand_qty, unit="Piece",
                        unitPrice=12, totalPrice=sand_qty * 12),
        MaterialItemOut(id="m5", name="Paint Roller Set", specification="9-inch roller with tray",
                        quantity=2, unit="Set", unitPrice=450, totalPrice=900),
        MaterialItemOut(id="m6", name="Paint Brush (2\" & 4\")", specification="Synthetic bristle",
                        quantity=4, unit="Piece", unitPrice=80, totalPrice=320),
        MaterialItemOut(id="m7", name="Masking Tape", specification="1.5-inch blue painters tape",
                        quantity=tape_qty, unit="Roll",
                        unitPrice=65, totalPrice=tape_qty * 65),
        MaterialItemOut(id="m8", name="Drop Cloth / Cover Sheet", specification="4m x 4m cotton canvas",
                        quantity=2, unit="Piece", unitPrice=350, totalPrice=700),
    ]


def _ceiling_materials(area: float, budget: str) -> list[MaterialItemOut]:
    boards = math.ceil(area / 2.88)
    gypsum_spec = "12.5mm Moisture Resistant" if budget == "luxury" else "9.5mm Standard Board"
    paint_spec = "Asian Paints Royale" if budget == "luxury" else "Berger Emulsion"
    light_spec = "9W Philips Hue-Compatible" if budget == "luxury" else "7W LED Downlight"
    gi_qty = math.ceil(area * 1.5)
    screw_qty = math.ceil(boards / 4)
    compound_qty = math.ceil(area * 0.3)
    tape_qty = math.ceil(boards / 2)
    paint_qty = math.ceil(area / 12)
    light_qty = math.ceil(area / 10)
    cove_qty = math.ceil(math.sqrt(area) * 0.8)

    def up(base): return _mult(base, budget, luxury=2.0, moderate=1.3)

    return [
        MaterialItemOut(id="c1", name="Gypsum Board", specification=gypsum_spec,
                        quantity=boards, unit="Sheet", unitPrice=up(480), totalPrice=boards * up(480)),
        MaterialItemOut(id="c2", name="GI Framework / Grid", specification="0.5mm GI Channel (Main + Cross Tee)",
                        quantity=gi_qty, unit="Running Ft", unitPrice=35, totalPrice=gi_qty * 35),
        MaterialItemOut(id="c3", name="GI Screws (Drywall)", specification="25mm Drywall Screws (Box)",
                        quantity=screw_qty, unit="Box (200pc)", unitPrice=220, totalPrice=screw_qty * 220),
        MaterialItemOut(id="c4", name="Jointing Compound", specification="Gyproc Jointing Compound",
                        quantity=compound_qty, unit="kg", unitPrice=32, totalPrice=compound_qty * 32),
        MaterialItemOut(id="c5", name="Fibre Tape", specification="50mm self-adhesive mesh tape",
                        quantity=tape_qty, unit="Roll", unitPrice=95, totalPrice=tape_qty * 95),
        MaterialItemOut(id="c6", name="Ceiling Paint", specification=paint_spec,
                        quantity=paint_qty, unit="Litre", unitPrice=up(195), totalPrice=paint_qty * up(195)),
        MaterialItemOut(id="c7", name="LED Recessed Lights", specification=light_spec,
                        quantity=light_qty, unit="Piece", unitPrice=up(380), totalPrice=light_qty * up(380)),
        MaterialItemOut(id="c8", name="Cove LED Strip (optional)", specification="12V RGB LED Strip 5m",
                        quantity=cove_qty, unit="Roll", unitPrice=850, totalPrice=cove_qty * 850),
    ]


def _door_materials(count: int, budget: str) -> list[MaterialItemOut]:
    panel_spec = {
        "luxury": "Teak Wood Solid Panel",
        "moderate": "Engineered Wood Flush Door",
    }.get(budget, "HDF Flush Door")
    frame_spec = "Teak Wood Frame" if budget == "luxury" else "Sal Wood Frame"
    lock_spec = "Godrej Mortise Lock Set" if budget == "luxury" else "Standard Cylindrical Lock"
    finish_spec = "Melamine Polish Kit" if budget == "luxury" else "Enamel Paint"

    def up(base): return _mult(base, budget, luxury=2.2, moderate=1.4)

    return [
        MaterialItemOut(id="d1", name="Door Panel", specification=panel_spec,
                        quantity=count, unit="Piece", unitPrice=up(8500), totalPrice=count * up(8500)),
        MaterialItemOut(id="d2", name="Door Frame", specification=frame_spec,
                        quantity=count, unit="Set", unitPrice=up(3200), totalPrice=count * up(3200)),
        MaterialItemOut(id="d3", name="Door Hinges", specification="4-inch SS Butt Hinge",
                        quantity=count * 3, unit="Piece", unitPrice=95, totalPrice=count * 3 * 95),
        MaterialItemOut(id="d4", name="Door Handle / Lock", specification=lock_spec,
                        quantity=count, unit="Set", unitPrice=up(750), totalPrice=count * up(750)),
        MaterialItemOut(id="d5", name="Door Stopper", specification="Floor-mounted SS door stopper",
                        quantity=count, unit="Piece", unitPrice=120, totalPrice=count * 120),
        MaterialItemOut(id="d6", name="Wood Primer + Paint/Polish", specification=finish_spec,
                        quantity=count * 2, unit="Litre", unitPrice=up(280), totalPrice=count * 2 * up(280)),
        MaterialItemOut(id="d7", name="Installation Hardware", specification="Screws, Anchors, Expansion Bolts",
                        quantity=count, unit="Set", unitPrice=180, totalPrice=count * 180),
    ]


def _window_materials(count: int, budget: str) -> list[MaterialItemOut]:
    frame_spec = {
        "luxury": "UPVC 5-Chamber Profile",
        "moderate": "UPVC 3-Chamber Profile",
    }.get(budget, "Aluminium Sliding Frame")
    glass_spec = {
        "luxury": "6mm Double Glazed Low-E",
        "moderate": "5mm Toughened Glass",
    }.get(budget, "4mm Clear Float Glass")

    def up(base): return _mult(base, budget, luxury=2.0, moderate=1.35)

    return [
        MaterialItemOut(id="w1", name="Window Frame", specification=frame_spec,
                        quantity=count, unit="Piece", unitPrice=up(6500), totalPrice=count * up(6500)),
        MaterialItemOut(id="w2", name="Glass Panel", specification=glass_spec,
                        quantity=count * 2, unit="Piece", unitPrice=up(1800), totalPrice=count * 2 * up(1800)),
        MaterialItemOut(id="w3", name="Window Handle", specification="SS Espagnolette Handle",
                        quantity=count, unit="Set", unitPrice=350, totalPrice=count * 350),
        MaterialItemOut(id="w4", name="Window Lock", specification="UPVC Multi-Point Lock",
                        quantity=count, unit="Piece", unitPrice=480, totalPrice=count * 480),
        MaterialItemOut(id="w5", name="Mosquito Net / Screen", specification="Fibreglass mesh screen",
                        quantity=count, unit="Set", unitPrice=650, totalPrice=count * 650),
        MaterialItemOut(id="w6", name="Sealant / Silicone", specification="Weatherproof silicone sealant",
                        quantity=count * 2, unit="Tube", unitPrice=95, totalPrice=count * 2 * 95),
        MaterialItemOut(id="w7", name="Installation Kit", specification="Frame fixings, screws, foam",
                        quantity=count, unit="Set", unitPrice=220, totalPrice=count * 220),
    ]


def _furniture_materials(units: int, budget: str) -> list[MaterialItemOut]:
    board_spec = {
        "luxury": "19mm BWP Marine Plywood",
        "moderate": "18mm Commercial Plywood",
    }.get(budget, "16mm MDF Board")
    hinge_spec = "Hettich Soft-Close Hinge" if budget == "luxury" else "Standard 35mm Hinge"
    slide_spec = "Blum Tandem 550mm" if budget == "luxury" else "Telescopic Slide 400mm"
    handle_spec = "Brass Antique Handle" if budget == "luxury" else "SS Finish Handle"
    laminate_spec = "Natural Wood Veneer" if budget == "luxury" else "1mm Decorative Laminate"
    finish_spec = "PU Matt Lacquer" if budget == "luxury" else "Melamine Finish"

    def up(base): return _mult(base, budget, luxury=2.5, moderate=1.5)

    return [
        MaterialItemOut(id="f1", name="Plywood / MDF Board", specification=board_spec,
                        quantity=units * 4, unit="Sheet", unitPrice=up(1800), totalPrice=units * 4 * up(1800)),
        MaterialItemOut(id="f2", name="Edge Banding Tape", specification="22mm PVC Melamine Edge Band",
                        quantity=units * 20, unit="Meter", unitPrice=8, totalPrice=units * 20 * 8),
        MaterialItemOut(id="f3", name="Cabinet Hinges", specification=hinge_spec,
                        quantity=units * 4, unit="Piece", unitPrice=up(180), totalPrice=units * 4 * up(180)),
        MaterialItemOut(id="f4", name="Drawer Slides", specification=slide_spec,
                        quantity=units * 2, unit="Pair", unitPrice=up(520), totalPrice=units * 2 * up(520)),
        MaterialItemOut(id="f5", name="Handles / Knobs", specification=handle_spec,
                        quantity=units * 4, unit="Piece", unitPrice=up(120), totalPrice=units * 4 * up(120)),
        MaterialItemOut(id="f6", name="Laminate / Veneer Sheet", specification=laminate_spec,
                        quantity=units * 3, unit="Sheet", unitPrice=up(950), totalPrice=units * 3 * up(950)),
        MaterialItemOut(id="f7", name="Screws & Fasteners", specification="Assorted cabinet screws set",
                        quantity=units, unit="Box", unitPrice=120, totalPrice=units * 120),
        MaterialItemOut(id="f8", name="Finish / Polish", specification=finish_spec,
                        quantity=units * 2, unit="Litre", unitPrice=up(350), totalPrice=units * 2 * up(350)),
    ]


# ─── BUDGET BREAKDOWN ────────────────────────────────────────────────────────

def _compute_budget(materials: list[MaterialItemOut], budget: str, category: str) -> BudgetBreakdownOut:
    material_total = sum(m.totalPrice for m in materials)
    labour_ratio = 0.55 if category == "furniture" else (0.65 if category == "ceiling" else 0.45)
    labour = round(material_total * labour_ratio)
    transport = round(material_total * 0.06)
    misc = round(material_total * 0.04)
    contingency = round((material_total + labour) * 0.08)
    return BudgetBreakdownOut(
        material=material_total,
        labour=labour,
        transport=transport,
        misc=misc,
        contingency=contingency,
        total=material_total + labour + transport + misc + contingency,
    )


# ─── DESIGN RECOMMENDATIONS ──────────────────────────────────────────────────

def _painting_recommendations(budget: str, property_type: str) -> list[DesignRecommendationOut]:
    primary = {
        "luxury": ("Warm Ivory Elegance", "Warm Ivory", "#F5EDD7",
                   "A sophisticated ivory tone exudes timeless luxury. Pairs beautifully with gold accents and dark wood furniture.",
                   [{"name": "Antique Gold", "hex": "#C9A84C"}, {"name": "Rich Mocha", "hex": "#6B4C3B"}, {"name": "Cream", "hex": "#FAF5EB"}],
                   "Royale Matt"),
        "moderate": ("Sage Green Serenity", "Sage Green", "#7F9E7F",
                     "A calming sage green brings nature indoors. Ideal for living rooms and bedrooms. Pairs with wood and linen.",
                     [{"name": "Warm White", "hex": "#F8F5F0"}, {"name": "Terracotta", "hex": "#C17F5C"}, {"name": "Dusty Blue", "hex": "#7A9BB5"}],
                     "Satin / Sheen"),
    }.get(budget, ("Classic Off-White", "Classic Off-White", "#F2EFE6",
                   "A clean off-white creates a bright, airy feel. Versatile and budget-friendly with timeless appeal.",
                   [{"name": "Light Grey", "hex": "#E0DEDD"}, {"name": "Beige", "hex": "#F0EAD6"}, {"name": "Pale Blue", "hex": "#D6E4F0"}],
                   "Matt Emulsion"))

    budget_tag = {"luxury": "Premium", "moderate": "Mid-Range"}.get(budget, "Affordable")
    property_tag = "Urban" if property_type == "urban" else "Rural"

    return [
        DesignRecommendationOut(
            title=primary[0], label="Recommended", description=primary[3],
            primaryColor=primary[1], primaryColorHex=primary[2],
            complementaryColors=primary[4], finish=primary[5],
            tags=["Wall Paint", budget_tag, property_tag],
        ),
        DesignRecommendationOut(
            title="Dusty Rose Warmth", label="Alternative 1",
            description="A soft dusty rose adds warmth and personality. Works well in bedrooms and dining rooms with natural wood accents.",
            primaryColor="Dusty Rose", primaryColorHex="#C9907A",
            complementaryColors=[{"name": "Warm Grey", "hex": "#B0A89E"}, {"name": "Ivory", "hex": "#F5F0E8"}],
            finish="Soft Sheen", tags=["Warm Tone", "Bedroom", "Dining"],
        ),
        DesignRecommendationOut(
            title="Slate Blue Calm", label="Alternative 2",
            description="Slate blue creates a calming, focused atmosphere. Perfect for home offices, libraries, or accent walls.",
            primaryColor="Slate Blue", primaryColorHex="#7A8FA6",
            complementaryColors=[{"name": "White", "hex": "#FFFFFF"}, {"name": "Warm Linen", "hex": "#EDE8DF"}],
            finish="Eggshell", tags=["Cool Tone", "Office", "Accent Wall"],
        ),
    ]


def _ceiling_recommendations(budget: str) -> list[DesignRecommendationOut]:
    primary = {
        "luxury": ("Multi-Level Cove Ceiling",
                   "An architectural multi-level cove ceiling with integrated LED lighting creates a dramatic, hotel-like ambience.",
                   "12.5mm Moisture-Resistant Gypsum + Cove Lighting"),
        "moderate": ("Simple False Ceiling with Cove",
                     "A clean false ceiling with cove lighting adds depth and a premium feel without excessive cost.",
                     "9.5mm Gypsum + LED Cove"),
    }.get(budget, ("Basic Gypsum Flat Ceiling",
                   "A clean flat gypsum false ceiling lowers perceived ceiling height and conceals wires neatly.",
                   "9.5mm Standard Gypsum Board"))
    budget_tag = {"luxury": "Luxury", "moderate": "Moderate"}.get(budget, "Budget")

    return [
        DesignRecommendationOut(title=primary[0], label="Recommended", description=primary[1],
                                material=primary[2], tags=["Ceiling", budget_tag]),
        DesignRecommendationOut(title="Coffered Grid Design", label="Alternative 1",
                                description="A coffered grid ceiling adds classic architectural character. Best for large living or dining rooms.",
                                material="12mm Gypsum with POP moulding strips", tags=["Classic", "Living Room"]),
        DesignRecommendationOut(title="Exposed Concrete + Spotlights", label="Alternative 2",
                                description="For an industrial-modern aesthetic, clean exposed concrete with track spotlights is striking and low-maintenance.",
                                material="Exposed RCC with surface-mounted track lights", tags=["Industrial", "Modern", "Minimal"]),
    ]


def _door_recommendations(budget: str, property_type: str) -> list[DesignRecommendationOut]:
    primary = {
        "luxury": ("Solid Teak Panel Door",
                   "Solid teak doors with hand-crafted panels offer unmatched durability, elegance, and a premium finish.",
                   "Solid Teak Wood"),
        "moderate": ("Engineered Wood Flush Door",
                     "Engineered wood doors balance aesthetics and durability. Available in veneer and laminate finishes.",
                     "Engineered Hardwood Core"),
    }.get(budget, ("HDF Flush Door",
                   "HDF flush doors offer a clean, simple look at an affordable price. Great for budget renovations.",
                   "High-Density Fibreboard"))
    budget_tag = {"luxury": "Luxury", "moderate": "Mid-Range"}.get(budget, "Budget")

    return [
        DesignRecommendationOut(title=primary[0], label="Recommended", description=primary[1],
                                material=primary[2], tags=["Door", budget_tag]),
        DesignRecommendationOut(title="Glass Panel Door", label="Alternative 1",
                                description="A partially glazed door with frosted or clear glass allows light transfer between rooms while maintaining privacy.",
                                material="Wooden frame + 5mm tempered glass panel", tags=["Light-Friendly", "Modern", "Semi-Private"]),
        DesignRecommendationOut(title="Sliding Barn Door", label="Alternative 2",
                                description="Space-saving sliding barn doors are trendy and practical for urban apartments with limited swing space.",
                                material="Engineered wood on metal rail system", tags=["Space-Saving", "Trendy", "Urban"]),
    ]


def _window_recommendations(budget: str) -> list[DesignRecommendationOut]:
    primary = {
        "luxury": ("UPVC Double-Glazed Casement",
                   "UPVC double-glazed windows offer excellent thermal insulation, noise reduction, and a premium look.",
                   "UPVC + 6mm Double Glaze"),
        "moderate": ("UPVC Single-Glazed Sliding",
                     "UPVC sliding windows provide good insulation and low maintenance at a mid-range price.",
                     "UPVC + 5mm Toughened"),
    }.get(budget, ("Aluminium Sliding Window",
                   "Aluminium sliding windows are lightweight, durable, and cost-effective for budget renovations.",
                   "Aluminium + 4mm Float Glass"))
    budget_tag = {"luxury": "Premium", "moderate": "Mid-Range"}.get(budget, "Budget")

    return [
        DesignRecommendationOut(title=primary[0], label="Recommended", description=primary[1],
                                material=primary[2], tags=["Window", budget_tag]),
        DesignRecommendationOut(title="Bay Window with Seat", label="Alternative 1",
                                description="A bay window extension creates a cosy reading nook and adds architectural interest to the façade.",
                                material="UPVC or Wood frame, panoramic glass", tags=["Architectural", "Living Room", "Reading Nook"]),
        DesignRecommendationOut(title="Louvered Ventilation Window", label="Alternative 2",
                                description="Louvered windows allow constant natural ventilation without full opening — ideal for bathrooms and kitchens.",
                                material="Aluminium louvre blades, anodised finish", tags=["Ventilation", "Bathroom", "Kitchen"]),
    ]


def _furniture_recommendations(budget: str, property_type: str) -> list[DesignRecommendationOut]:
    primary = {
        "luxury": ("Custom Solid Wood Furniture",
                   "Custom solid wood pieces with natural veneer finish offer longevity and a unique, bespoke aesthetic.",
                   "Solid Teak / Sheesham Wood"),
        "moderate": ("Modular Plywood Furniture",
                     "Modular plywood furniture with laminate finish balances quality and cost — easy to customise.",
                     "18mm BWR Plywood + Laminate"),
    }.get(budget, ("MDF Laminate Furniture",
                   "MDF furniture with PVC or laminate finish is affordable, lightweight, and visually clean.",
                   "16mm MDF + PVC Foil"))
    prop_tag = "Traditional" if property_type == "rural" else "Contemporary"

    return [
        DesignRecommendationOut(title=primary[0], label="Recommended", description=primary[1],
                                material=primary[2], tags=["Furniture", prop_tag]),
        DesignRecommendationOut(title="Scandinavian Minimalist", label="Alternative 1",
                                description="Light-toned wood with clean lines and minimal ornamentation. Ideal for small urban apartments.",
                                material="Birch veneer or beech solid wood", tags=["Minimalist", "Scandinavian", "Space-Saving"]),
        DesignRecommendationOut(title="Industrial Pipe & Wood", label="Alternative 2",
                                description="Black iron pipe frames with reclaimed wood shelves create a striking industrial look.",
                                material="Black powder-coated MS pipes + reclaimed wood", tags=["Industrial", "Trendy", "DIY-Friendly"]),
    ]


# ─── MAIN ENGINE ENTRY POINT ─────────────────────────────────────────────────

def run_analysis(req: AnalysisRequest) -> AnalysisResultOut:
    category = req.category
    budget = req.budget
    property_type = req.propertyType
    m = req.measurements

    materials: list[MaterialItemOut] = []
    recommendations: list[DesignRecommendationOut] = []

    if category == "painting":
        l = m.wallLength or 4.0
        h = m.wallHeight or 3.0
        n = m.numWalls or 2
        area = l * h * n
        materials = _painting_materials(area, budget)
        recommendations = _painting_recommendations(budget, property_type)

    elif category == "ceiling":
        l = m.ceilingLength or 5.0
        w = m.ceilingWidth or 4.0
        area = l * w
        materials = _ceiling_materials(area, budget)
        recommendations = _ceiling_recommendations(budget)

    elif category == "doors":
        count = m.numDoors or 2
        materials = _door_materials(count, budget)
        recommendations = _door_recommendations(budget, property_type)

    elif category == "windows":
        count = m.numWindows or 3
        materials = _window_materials(count, budget)
        recommendations = _window_recommendations(budget)

    elif category == "furniture":
        count = m.numFurnitureUnits or 2
        materials = _furniture_materials(count, budget)
        recommendations = _furniture_recommendations(budget, property_type)

    else:
        materials = []
        recommendations = []

    budget_breakdown = _compute_budget(materials, budget, category)

    category_names = {
        "painting": "Painting & Walls",
        "ceiling": "Ceiling Design",
        "doors": "Doors",
        "windows": "Windows",
        "furniture": "Furniture",
    }

    return AnalysisResultOut(
        id=f"analysis-{uuid.uuid4().hex}",
        projectName=f"{category_names.get(category, category.title())} Project",
        category=category,
        budget=budget,
        propertyType=property_type,
        imagePreviewUrl=req.imageUrl,
        measurements=m.model_dump(exclude_none=True),
        preferences=req.preferences.model_dump(exclude_none=True),
        recommendations=recommendations,
        materials=materials,
        budgetBreakdown=budget_breakdown,
        createdAt=datetime.utcnow().isoformat(),
    )
