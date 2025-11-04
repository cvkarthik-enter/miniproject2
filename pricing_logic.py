# pricing_logic.py
from pricing_data import CONSTANTS, MATERIAL_BASE_RATES, CORE_SURCHARGES, \
                         LAMINATE_RATES, VENEER_RATES, VISION_HOLE_FEES, \
                         ADDON_SQFT_RATES

# --- Helper Functions (Ensuring Availability) ---

def calculate_area_sqft(L_mm, W_mm, factor=1):
    """Calculates door surface area in sqft, multiplied by factor (e.g., 2 for both sides)."""
    conversion = CONSTANTS["SQMM_TO_SQFT"]
    area_mm2 = L_mm * W_mm
    return round(area_mm2 / conversion * factor, 4)

def calculate_edge_area_sqft(L_mm, W_mm, T_mm):
    """
    Calculates the total edge surface area in sqft.
    Formula: [2 * (L_mm + W_mm) * T_mm] / SQMM_TO_SQFT
    """
    conversion = CONSTANTS["SQMM_TO_SQFT"]
    
    # Perimeter (L + W) * 2
    perimeter_mm = 2 * (L_mm + W_mm)
    
    # Total edge surface area in mm^2
    edge_area_mm2 = perimeter_mm * T_mm
    
    # Conversion to sqft
    edge_area_sqft = edge_area_mm2 / conversion
    
    return round(edge_area_sqft, 4)

# --- Core Logic Functions (Fixes applied primarily to get_psf_rate) ---

def get_psf_rate(rails_material, filler_material, T_mm, core_option):
    """Calculates the final dynamic PSF Rate (INR/sqft) for the door skeleton."""
    T_base = CONSTANTS["BASE_THICKNESS_MM"]
    S_inc = CONSTANTS["THICKNESS_SURCHARGE_RATE"]
    
    # 1. Base Material Lookup
    material_key = (rails_material, filler_material)
    R_base = MATERIAL_BASE_RATES.get(material_key)
    if R_base is None:
        raise ValueError(f"Pricing not defined for material combination: {material_key}")

    # 2. Thickness Surcharge
    thickness_increase = max(0, T_mm - T_base)
    thickness_surcharge = thickness_increase * S_inc
    PSF_rate = R_base + thickness_surcharge
    
    # 3. Conditional Core Surcharge
    if T_mm <= 35:
        if core_option == "Double Core":
            PSF_rate += CORE_SURCHARGES["Double Core"]
        elif core_option == "Core + HDF":
            PSF_rate += CORE_SURCHARGES["Core + HDF"]
    
    elif T_mm >= 36:
        if core_option == "Core + HDF":
            h_df_cost = CORE_SURCHARGES["Core + HDF"]
            dc_cost = CORE_SURCHARGES["Double Core"]
            differential_surcharge = h_df_cost - dc_cost
            PSF_rate += differential_surcharge
    
    return round(PSF_rate, 2)

def calculate_skeleton_cost(L_mm, W_mm, T_mm, rails, filler, core_option):
    """Calculates the base cost of the door structure (Skeleton Cost)."""
    psf_rate = get_psf_rate(rails, filler, T_mm, core_option)
    area_1x = calculate_area_sqft(L_mm, W_mm, factor=1)
    return round(area_1x * psf_rate, 2)

def calculate_finish_cost(L_mm, W_mm, door_type, finish_option):
    """Calculates the primary material finishing cost (Laminate is fixed, Veneer is 2x Area)."""
    if door_type == "Laminate":
        rate = LAMINATE_RATES.get(finish_option)
        return round(rate, 2) if rate is not None else 0.0
    
    elif door_type == "Veneer":
        rate = VENEER_RATES.get(finish_option)
        if rate is not None:
            # FIX: Ensure calculation proceeds if rate is found
            area_2x = calculate_area_sqft(L_mm, W_mm, factor=2)
            return round(area_2x * rate, 2)
    return 0.0

def calculate_addon_cost(L_mm, W_mm, T_mm, skeleton_cost, add_ons):
    """Calculates the total cost for all optional add-ons."""
    total_addon_cost = 0.0
    area_1x_sqft = calculate_area_sqft(L_mm, W_mm, factor=1)

    # 1. Double Leaf Surcharge (Percentage-Based)
    if add_ons.get('double_leaf', 'no').lower() == 'yes':
        total_addon_cost += skeleton_cost * CONSTANTS["DOUBLE_LEAF_FACTOR"]
    
    # 2. Vision Hole (Fixed Fee, Conditional on Thickness)
    if add_ons.get('vision_hole', 'no').lower() == 'yes':
        vh_fee = next((f["F_VH"] for f in VISION_HOLE_FEES 
                       if f["T_min"] <= T_mm <= f["T_max"]), 0.0)
        total_addon_cost += vh_fee

    # 3. Edge Banding (Edge Surface Area Based)
    if add_ons.get('edge_banding', 'yes').lower() == 'yes': 
        edge_area_sqft = calculate_edge_area_sqft(L_mm, W_mm, T_mm)
        total_addon_cost += edge_area_sqft * CONSTANTS["EDGE_BANDING_RATE"]

    # 4. Area-Based Add-ons (Coating, Grooving, Routing)
    area_addons_map = {
        'coating': 'Coating', 
        'grooving': 'Grooving', 
        'routing': 'Routing'
    }
    
    for addon_key, prefix in area_addons_map.items():
        option = add_ons.get(addon_key, 'none')
        if option.lower() != 'none':
            # FIX: Simplify key generation for accurate dictionary lookup (e.g., 'Resin Coated (Both Sides)' -> 'Resin_Coated_Both_Sides')
            # Assuming options are formatted like "Option Name (Side)" or just "Option Name"
            
            # This generates the exact key: e.g., 'Coating_Resin_Both_Sides'
            lookup_key = f"{prefix}_{'_'.join(option.split()).replace('(', '').replace(')', '')}" 
            rate = ADDON_SQFT_RATES.get(lookup_key)
            
            if rate:
                total_addon_cost += area_1x_sqft * rate
            else:
                print(f"[DEBUG ERROR] Add-on rate not found for key: {lookup_key}")
                
    return round(total_addon_cost, 2)

def calculate_total_price(L_mm, W_mm, T_mm, rails, filler, core_option, door_type, finish_option, add_ons):
    """Orchestrates the entire pricing process."""
    
    skeleton_cost = calculate_skeleton_cost(L_mm, W_mm, T_mm, rails, filler, core_option)
    finish_cost = calculate_finish_cost(L_mm, W_mm, door_type, finish_option)
    addon_cost = calculate_addon_cost(L_mm, W_mm, T_mm, skeleton_cost, add_ons)
    
    total_price = skeleton_cost + finish_cost + addon_cost
    
    return {
        "skeleton_cost": skeleton_cost,
        "finish_cost": finish_cost,
        "addon_cost": addon_cost,
        "total_price": round(total_price, 2)
    }

# --- Example of running the calculation ---
if __name__ == '__main__':
    # --- Sample Input Data ---
    SAMPLE_L = 2133.6 # 84 inches
    SAMPLE_W = 914.4  # 36 inches
    SAMPLE_T = 40.0   # 40mm
    
    # Core Material (Matching the 'Hardwood/Ecolax Board' base rate)
    SAMPLE_RAILS = "Hardwood"
    SAMPLE_FILLER = "Ecolax Board"
    SAMPLE_CORE = "Core + HDF" # Triggers differential surcharge for T=40mm
    
    # Finish and Add-ons
    SAMPLE_DOOR_TYPE = "Veneer"
    SAMPLE_FINISH = "Smoke Oak Veneer"
    
    SAMPLE_ADDONS = {
        'double_leaf': 'no',
        'vision_hole': 'yes',
        'edge_banding': 'yes',
        'coating': 'Resin Coated (Both Sides)', 
        'grooving': 'Both Sides',
        'routing': 'none',
    }

    # --- Run Calculation ---
    results = calculate_total_price(
        SAMPLE_L, SAMPLE_W, SAMPLE_T, 
        SAMPLE_RAILS, SAMPLE_FILLER, SAMPLE_CORE, 
        SAMPLE_DOOR_TYPE, SAMPLE_FINISH, SAMPLE_ADDONS
    )
    
    # --- Detailed Output ---
    
    # Calculating expected area for verification
    area_1x = calculate_area_sqft(SAMPLE_L, SAMPLE_W)
    
    print("--- Detailed Door Price Breakdown (INR) ---")
    print(f"Dimensions: {int(SAMPLE_L)}mm x {int(SAMPLE_W)}mm x {SAMPLE_T}mm")
    print(f"Materials: {SAMPLE_RAILS} / {SAMPLE_FILLER} / {SAMPLE_CORE}")
    print(f"Calculated 1X Area: {area_1x:.2f} sqft")
    print("-----------------------------------------")
    print(f"1. Skeleton (Base Structure) Cost: {results['skeleton_cost']:,.2f}")
    print(f"2. Finish Material Cost:           {results['finish_cost']:,.2f}")
    print(f"3. Add-on Surcharges:              {results['addon_cost']:,.2f}")
    print("-----------------------------------------")
    print(f"TOTAL PRICE:                       {results['total_price']:,.2f}")