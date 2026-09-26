"""
Seed the database with initial professionals data (ported from mockProfessionals.ts)
Run once: python seed.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

PROFESSIONALS = [
    {
        "id": "p1", "name": "Rajesh Kumar",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rajesh&backgroundColor=b6e3f4",
        "profession": "Painter", "specialization": "Interior & Exterior Painting",
        "service_area": "South Delhi, Gurgaon", "experience": 12,
        "rating": 4.8, "reviews": 134, "starting_price": 8000, "consultation_fee": 500,
        "availability": "Available", "verified": True, "distance": 2.4,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&q=80",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
            "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=400&q=80",
        ]),
        "skills_json": json.dumps(["Oil Painting", "Texture Painting", "Waterproofing", "Putty Work"]),
        "services_json": json.dumps(["Interior Painting", "Exterior Painting", "Texture Finish", "Waterproofing"]),
        "slots_json": json.dumps(["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"]),
        "bio": "With over 12 years of experience, Rajesh specializes in premium interior and exterior painting. Known for his meticulous attention to detail and clean finishing.",
    },
    {
        "id": "p2", "name": "Priya Sharma",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Priya&backgroundColor=ffdfbf",
        "profession": "Interior Designer", "specialization": "Contemporary & Minimalist Design",
        "service_area": "Mumbai, Navi Mumbai, Thane", "experience": 8,
        "rating": 4.9, "reviews": 87, "starting_price": 25000, "consultation_fee": 2000,
        "availability": "Limited", "verified": True, "distance": 5.1,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=400&q=80",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&q=80",
            "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=400&q=80",
        ]),
        "skills_json": json.dumps(["Space Planning", "Colour Consultation", "3D Visualization", "Project Management"]),
        "services_json": json.dumps(["Full Home Design", "Single Room Makeover", "Colour Consultation", "Furniture Selection"]),
        "slots_json": json.dumps(["10:00 AM", "1:00 PM", "3:30 PM"]),
        "bio": "Priya is a NIFT-graduate interior designer who blends contemporary aesthetics with functional living. She has transformed over 80 residential spaces across Mumbai.",
    },
    {
        "id": "p3", "name": "Mohammed Farooq",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Farooq&backgroundColor=c0aede",
        "profession": "Civil Contractor", "specialization": "Renovation & Construction",
        "service_area": "Bengaluru North, Whitefield", "experience": 15,
        "rating": 4.7, "reviews": 210, "starting_price": 50000, "consultation_fee": 0,
        "availability": "Available", "verified": True, "distance": 8.3,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=400&q=80",
            "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400&q=80",
            "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=400&q=80",
        ]),
        "skills_json": json.dumps(["Structural Work", "Flooring", "Tiling", "Plumbing", "Electrical Coordination"]),
        "services_json": json.dumps(["Full Home Renovation", "Kitchen Remodel", "Bathroom Remodel", "Flooring", "Tiling"]),
        "slots_json": json.dumps(["8:00 AM", "10:00 AM", "12:00 PM", "3:00 PM"]),
        "bio": "Farooq brings 15 years of expertise in residential renovation. His team handles end-to-end projects from structural modifications to final touches.",
    },
    {
        "id": "p4", "name": "Sunita Mehra",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sunita&backgroundColor=d1d4f9",
        "profession": "Carpenter", "specialization": "Custom Furniture & Woodwork",
        "service_area": "Hyderabad, Secunderabad", "experience": 10,
        "rating": 4.6, "reviews": 95, "starting_price": 15000, "consultation_fee": 500,
        "availability": "Available", "verified": False, "distance": 3.7,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80",
            "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400&q=80",
            "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=400&q=80",
        ]),
        "skills_json": json.dumps(["Custom Furniture", "Modular Kitchens", "Wardrobes", "Wood Polishing"]),
        "services_json": json.dumps(["Custom Furniture Making", "Modular Kitchen", "Wardrobe", "Wooden Flooring", "Polishing"]),
        "slots_json": json.dumps(["9:00 AM", "11:30 AM", "2:00 PM", "5:00 PM"]),
        "bio": "Sunita and her team craft bespoke furniture solutions that combine aesthetics with durability. Specializes in modular kitchens and custom wardrobes.",
    },
    {
        "id": "p5", "name": "Arvind Nair",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Arvind&backgroundColor=b6e3f4",
        "profession": "Ceiling Specialist", "specialization": "False Ceiling & POP Work",
        "service_area": "Chennai, Tambaram", "experience": 7,
        "rating": 4.8, "reviews": 62, "starting_price": 12000, "consultation_fee": 800,
        "availability": "Available", "verified": True, "distance": 4.2,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&q=80",
            "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=400&q=80",
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400&q=80",
        ]),
        "skills_json": json.dumps(["Gypsum False Ceiling", "POP Ceiling", "Cove Lighting", "Acoustic Ceiling"]),
        "services_json": json.dumps(["False Ceiling Installation", "POP Work", "Cove Lighting Setup", "Ceiling Painting"]),
        "slots_json": json.dumps(["8:30 AM", "11:00 AM", "1:30 PM", "4:00 PM"]),
        "bio": "Arvind is a certified false ceiling specialist with expertise in gypsum board, POP designs, and integrated lighting systems.",
    },
    {
        "id": "p6", "name": "Deepak Verma",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Deepak&backgroundColor=ffdfbf",
        "profession": "Door & Window Installer", "specialization": "UPVC, Aluminium & Wooden Frames",
        "service_area": "Pune, Pimpri-Chinchwad", "experience": 9,
        "rating": 4.5, "reviews": 78, "starting_price": 5000, "consultation_fee": 300,
        "availability": "Busy", "verified": True, "distance": 6.8,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
            "https://images.unsplash.com/photo-1449247666642-264389f5f5b1?w=400&q=80",
        ]),
        "skills_json": json.dumps(["UPVC Installation", "Aluminium Frames", "Sliding Doors", "Double Glazing"]),
        "services_json": json.dumps(["Door Installation", "Window Installation", "UPVC Fitting", "Aluminium Fabrication"]),
        "slots_json": json.dumps(["10:00 AM", "2:00 PM"]),
        "bio": "Deepak specializes in UPVC and aluminium door/window installations with 9 years of experience. Known for precision fitting and clean workmanship.",
    },
    {
        "id": "p7", "name": "Lakshmi Iyer",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lakshmi&backgroundColor=c0aede",
        "profession": "Electrician", "specialization": "Home Wiring & Lighting Design",
        "service_area": "Kolkata, Salt Lake", "experience": 11,
        "rating": 4.7, "reviews": 156, "starting_price": 3000, "consultation_fee": 200,
        "availability": "Available", "verified": True, "distance": 1.9,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1558002038-1055907df827?w=400&q=80",
            "https://images.unsplash.com/photo-1565814636199-ae8133055c1c?w=400&q=80",
        ]),
        "skills_json": json.dumps(["Wiring", "LED Lighting", "Modular Switches", "Home Automation"]),
        "services_json": json.dumps(["Full Home Wiring", "LED Lighting Setup", "Modular Switches", "Ceiling Fans", "Home Automation Basics"]),
        "slots_json": json.dumps(["9:00 AM", "11:00 AM", "3:00 PM", "5:00 PM"]),
        "bio": "Lakshmi is a certified electrician with expertise in modern home wiring, LED lighting design, and smart home basics.",
    },
    {
        "id": "p8", "name": "Ravi Bhattacharya",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ravi&backgroundColor=d1d4f9",
        "profession": "Interior Designer", "specialization": "Traditional & Heritage Decor",
        "service_area": "Jaipur, Ajmer", "experience": 14,
        "rating": 4.9, "reviews": 43, "starting_price": 30000, "consultation_fee": 2500,
        "availability": "Limited", "verified": True, "distance": 12.0,
        "portfolio_json": json.dumps([
            "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=400&q=80",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80",
        ]),
        "skills_json": json.dumps(["Rajasthani Decor", "Antique Furniture", "Fresco Work", "Heritage Restoration"]),
        "services_json": json.dumps(["Full Home Design", "Heritage Restoration", "Custom Decor", "Fresco & Wall Art"]),
        "slots_json": json.dumps(["10:30 AM", "2:30 PM"]),
        "bio": "Ravi is a master of traditional Indian design, specializing in heritage décor, Rajasthani motifs, and antique furniture curation.",
    },
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(models.Professional).count()
        if existing > 0:
            print(f"Database already has {existing} professionals — skipping seed.")
            return
        for p in PROFESSIONALS:
            prof = models.Professional(**p)
            db.add(prof)
        db.commit()
        print(f"[OK] Seeded {len(PROFESSIONALS)} professionals.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
