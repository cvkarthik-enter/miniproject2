# pricing_data.py

# A. Global Constants (To be editable)
CONSTANTS = {
    "BASE_THICKNESS_MM": 30,
    "THICKNESS_SURCHARGE_RATE": 3.25,  # INR/sqft/mm
    "DOUBLE_LEAF_FACTOR": 0.16,       # 16% surcharge
    "EDGE_BANDING_RATE": 50.00,       # INR/sqft
    "SQMM_TO_SQFT": 92903.04          # Conversion factor
}

# B. Material Base Rates (R_base lookup)
MATERIAL_BASE_RATES = {
    ("Hardwood", "Hardwood"): 144.00,  # INR/sqft
    ("Pinewood (S.Y.P)", "Ecolax Board"): 144.00,
    ("Hardwood", "Ecolax Board"): 131.00,
    ("Hardwood", "Pinewood (S.Y.P)"): 165.00,
    ("Pinewood (S.Y.P)", "Hardwood"): 156.00,
    ("Pinewood (S.Y.P)", "Pinewood (S.Y.P)"): 175.00,
    # ... add all other 6 combinations
}

# C. Core Surcharges (C_DC)
CORE_SURCHARGES = {
    "Double Core": 9.00,  # INR/sqft
    "Core + HDF": 18.00,  # INR/sqft
}

# D. Finish Rates (Example: Laminate Fixed Fee, Veneer Rate)
LAMINATE_RATES = {
    "Wenge walnut shade 0.8mm": 3250.00,  # INR/door
    "Wenge walnut shade 1mm": 4250.00,  # INR/door
    "Black walnut shade with 3 lines": 5125.00,  # INR/door
}

VENEER_RATES = {
    "Smoke Oak Veneer": 90.00,  # INR/sqft
    "Teak Veneer - plain": 55.00,  # INR/sqft
    "Teak Veneer - design1": 68.00,  # INR/sqft
}

# E. Thickness-Conditional Fees (Vision Hole)
VISION_HOLE_FEES = [
    {"T_min": 30, "T_max": 35, "F_VH": 45.00},
    {"T_min": 36, "T_max": 50, "F_VH": 65.00},
]

# F. Add-on SqFt Rates (Grooving/Routing)
# Key: "Feature_Option_Sides" -> Rate (INR/sqft)
ADDON_SQFT_RATES = {
    "Coating_Resin_Coated_One_Side": 80.00,
    "Coating_Resin_Coated_Both_Sides": 180.00,  # Specific fixed rate for both sides
    "Grooving_One_Side": 12.00,
    "Grooving_Both_Sides": 22.00,
    "Routing_One_Side": 15.00,
    "Routing_Both_Sides": 28.00,
}