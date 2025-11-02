import uuid

# --- 1. Raw Material Model ---
class RawMaterial:
    """Represents a basic raw material."""
    def __init__(self, name, unit_cost):
        self.name = name
        self.unit_cost = unit_cost

    def __str__(self):
        return f"{self.name} (Cost: ${self.unit_cost:.2f})"

# --- 2. Raw Material Manager (New Centralized Class) ---
class RawMaterialManager:
    """Manages the creation and storage of all RawMaterial objects."""
    def __init__(self):
        # {name: RawMaterial_object}
        self.materials = {}

    def add_material(self, name, cost):
        """Creates and stores a new RawMaterial."""
        name = name.strip().title()
        if name in self.materials:
            print(f"Error: Raw Material '{name}' already exists.")
            return False
        
        try:
            cost = float(cost)
        except ValueError:
            print("Error: Cost must be a number.")
            return False

        self.materials[name] = RawMaterial(name, cost)
        print(f"✅ Raw Material '{name}' added with cost ${cost:.2f}.")
        return True

    def get_material(self, name):
        """Retrieves a RawMaterial object by name."""
        return self.materials.get(name.strip().title())

    def get_all_materials(self):
        """Returns the dictionary of all materials."""
        return self.materials

    def view_materials(self):
        """Prints all currently defined raw materials."""
        print("\n--- 📦 Available Raw Materials ---")
        if not self.materials:
            print("No raw materials have been defined yet.")
            return
        for mat in self.materials.values():
            print(f"  - {mat}")
        print("-" * 35)


# --- 3. Product Type Model (The Standardizer) ---
class ProductType:
    # ... (The ProductType class remains the same for simplicity)
    # ... (Its reliance on the material dictionary is passed during method calls)
    
    """
    Defines a standardized recipe for a custom product.
    Includes material proportions, pricing logic, and required user variables.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description
        # {RawMaterial_name: proportional_factor} e.g., {"Steel": 2.5, "Plastic": 1.0}
        self.materials_recipe = {}
        # List of variables required from the user when creating a product instance.
        self.required_variables = []
        # Default pricing formula: material cost * 1.5 markup
        self.price_formula = lambda material_cost, vars: material_cost * 1.5

    def add_material(self, material_name, factor):
        """Adds or updates a raw material and its proportional factor."""
        self.materials_recipe[material_name] = factor

    def add_variable(self, variable_name):
        """Adds a user-required variable."""
        if variable_name not in self.required_variables:
            self.required_variables.append(variable_name)

    def calculate_material_cost(self, all_materials):
        """Calculates the total material cost for a standard unit of this product type."""
        total_cost = 0
        for mat_name, factor in self.materials_recipe.items():
            material = all_materials.get(mat_name)
            if material:
                total_cost += material.unit_cost * factor
        return total_cost

    def get_details(self, all_materials):
        """Returns a string summary of the product type."""
        details = [
            f"  Name: {self.name}",
            f"  Description: {self.description}",
            f"  Required Variables: {', '.join(self.required_variables) if self.required_variables else 'None'}",
            "  --- Recipe (Standardized Proportions) ---"
        ]
        for mat_name, factor in self.materials_recipe.items():
            material = all_materials.get(mat_name)
            cost_contribution = material.unit_cost * factor if material else 0
            details.append(f"    - {mat_name}: Factor {factor} (Cost Contribution: ${cost_contribution:.2f})")
        
        std_cost = self.calculate_material_cost(all_materials)
        details.append(f"  Standard Material Cost (per factor): ${std_cost:.2f}")
        details.append("  *Final Price is calculated using the custom formula on product creation.*")
        
        return "\n".join(details)


# --- 4. Product Instance Model ---
class Product:
    # ... (The Product class remains the same)
    
    """Represents an individual manufactured product based on a ProductType."""
    def __init__(self, product_type, user_variables, all_materials):
        self.id = uuid.uuid4()
        self.product_type = product_type
        self.user_variables = user_variables
        self.material_cost = 0
        self.final_price = 0
        
        self._evaluate_cost_and_price(all_materials)

    def _evaluate_cost_and_price(self, all_materials):
        """Calculates the final cost and price based on the product type's recipe and user variables."""
        
        # 1. Base Material Cost from Product Type (Standardized)
        base_cost = self.product_type.calculate_material_cost(all_materials)
        
        # 2. Apply a scaling factor from user input (example logic)
        scaling_factor = self.user_variables.get(self.product_type.required_variables[0], 1) if self.product_type.required_variables else 1
        
        self.material_cost = base_cost * scaling_factor
        
        # 3. Calculate Final Price using the Product Type's formula
        self.final_price = self.product_type.price_formula(self.material_cost, self.user_variables)

    def __str__(self):
        vars_str = ', '.join([f"{k}: {v}" for k, v in self.user_variables.items()])
        return (f"Product ID: {str(self.id).split('-')[0]} | Type: {self.product_type.name}\n"
                f"  Variables: {vars_str}\n"
                f"  Material Cost: ${self.material_cost:.2f} | Final Price: ${self.final_price:.2f}")


# --- 5. Product Manager (The System Controller) ---
class ProductManager:
    """Manages Product Types and Products, handles user interaction."""
    def __init__(self):
        # Composition: ProductManager 'has-a' RawMaterialManager
        self.material_manager = RawMaterialManager()
        self.product_types = {}
        self.products = []
        
        # Pre-populate some materials for a quick start
        self.material_manager.add_material("Steel", 5.00)
        self.material_manager.add_material("Plastic", 1.50)
        self.material_manager.add_material("Wood", 3.00)


    def _get_input(self, prompt, type_cast=str):
        """Helper for robust input."""
        while True:
            try:
                user_input = input(f"{prompt} ").strip()
                if not user_input:
                    raise ValueError("Input cannot be empty.")
                return type_cast(user_input)
            except ValueError as e:
                print(f"Invalid input: {e}. Please try again.")

    # --- Raw Material Management Method ---
    def add_new_raw_material(self):
        """Prompts user to create a new raw material."""
        print("\n--- 🧱 Add New Raw Material ---")
        name = self._get_input("Enter Raw Material Name")
        cost = self._get_input("Enter Unit Cost (e.g., 5.00)", float)
        self.material_manager.add_material(name, cost)


    # --- Product Type Management Methods ---
    def create_new_product_type(self):
        """Creates a new ProductType and defines its standards."""
        print("\n--- 🛠️ Create New Product Type ---")
        name = self._get_input("Enter Product Type Name (e.g., 'Heavy Duty Frame')")
        if name in self.product_types:
            print(f"Error: Product Type '{name}' already exists.")
            return
        description = self._get_input("Enter Description")

        new_type = ProductType(name, description)

        # Accessing materials through the dedicated manager
        available_materials = self.material_manager.get_all_materials()
        if not available_materials:
            print("\n⚠️ No raw materials available. Please add some first (Menu 7).")
            return
            
        print("\n--- Define Recipe (Raw Materials) ---")
        self.material_manager.view_materials()
        
        while self._get_input("Add a Raw Material to the recipe? (yes/no)").lower() == 'yes':
            mat_name = self._get_input("Enter Raw Material Name").title()
            if mat_name in available_materials:
                factor = self._get_input(f"Enter proportional factor for {mat_name} (e.g., 2.5)", float)
                new_type.add_material(mat_name, factor)
            else:
                print(f"Error: Raw Material '{mat_name}' not found in the available list.")

        # Dependent Variables (omitted for brevity, same as before)
        print("\n--- Define Dependent Variables ---")
        while self._get_input("Add a required user variable? (yes/no)").lower() == 'yes':
            var_name = self._get_input("Enter Variable Name (e.g., 'size_factor')")
            new_type.add_variable(var_name.lower().replace(" ", "_"))

        self.product_types[name] = new_type
        print(f"\n✅ Product Type '{name}' created successfully!")
    
    # --- Other Product Type Methods (Modified to use the Manager) ---
    def view_existing_product_types(self):
        """Displays details of all existing ProductTypes."""
        print("\n--- 📝 Existing Product Types ---")
        if not self.product_types:
            print("No product types have been defined yet.")
            return

        all_materials = self.material_manager.get_all_materials()
        for name, p_type in self.product_types.items():
            print("-" * 40)
            # Pass the material list from the manager
            print(p_type.get_details(all_materials))
        print("-" * 40)

    def modify_existing_product_type(self):
        """Simple modification option."""
        print("\n--- 🔧 Modify Existing Product Type ---")
        if not self.product_types:
            print("No product types to modify.")
            return

        name = self._get_input("Enter the name of the Product Type to modify")
        p_type = self.product_types.get(name)

        if not p_type:
            print(f"Error: Product Type '{name}' not found.")
            return
        
        print(f"Modifying Product Type: {name}")
        print("1. Add/Update Raw Material Proportion")
        print("2. Add Required Variable")
        choice = self._get_input("Enter choice (1 or 2)", int)

        if choice == 1:
            self.material_manager.view_materials()
            mat_name = self._get_input("Enter Raw Material Name").title()
            if mat_name in self.material_manager.get_all_materials():
                factor = self._get_input(f"Enter NEW proportional factor for {mat_name}", float)
                p_type.add_material(mat_name, factor)
                print(f"✅ Recipe updated for {name}.")
            else:
                print(f"Error: Raw Material '{mat_name}' not found in the available list.")
        elif choice == 2:
            var_name = self._get_input("Enter NEW Variable Name").lower().replace(" ", "_")
            p_type.add_variable(var_name)
            print(f"✅ Variable '{var_name}' added to {name}.")
        else:
            print("Invalid choice.")
            
    # --- Product Creation Method (Modified to use the Manager) ---
    def create_product_instance(self):
        """Creates an actual product instance based on a selected ProductType."""
        # ... (same selection logic)
        
        print("\n--- 📦 Create New Product Instance ---")
        if not self.product_types:
            print("Cannot create product: No product types defined.")
            return
            
        self.view_existing_product_types()
        
        type_name = self._get_input("Enter the name of the Product Type to use")
        p_type = self.product_types.get(type_name)

        if not p_type:
            print(f"Error: Product Type '{type_name}' not found.")
            return

        print(f"Creating product based on '{p_type.name}'.")
        user_vars = {}
        for var_name in p_type.required_variables:
            value = self._get_input(f"Enter value for dependent variable '{var_name}'")
            try:
                user_vars[var_name] = float(value)
            except ValueError:
                user_vars[var_name] = value

        # Pass the material list from the manager
        new_product = Product(p_type, user_vars, self.material_manager.get_all_materials())
        self.products.append(new_product)
        print("\n✅ Product created:")
        print(new_product)

    # --- Main Application Loop (Updated Menu) ---
    def run(self):
        """The main command-line interface loop."""
        print("--- Custom Manufacturing Product System ---")
        while True:
            print("\n" + "="*40)
            print("Main Menu:")
            print("1. Create New Product Type")
            print("2. View Existing Product Types")
            print("3. Modify Existing Product Type")
            print("4. Create New Product (Instance)")
            print("5. View All Products")
            print("--- Raw Material Management ---")
            print("6. **VIEW** Available Raw Materials")
            print("7. **CREATE** New Raw Material")
            print("8. Exit")
            print("="*40)

            choice = self._get_input("Enter your choice (1-8)", str)
            
            if choice == '1':
                self.create_new_product_type()
            elif choice == '2':
                self.view_existing_product_types()
            elif choice == '3':
                self.modify_existing_product_type()
            elif choice == '4':
                self.create_product_instance()
            elif choice == '5':
                print("\n--- 📦 All Products Created ---")
                if not self.products:
                    print("No products have been created yet.")
                for product in self.products:
                    print("-" * 40)
                    print(product)
                print("-" * 40)
            elif choice == '6':
                self.material_manager.view_materials()
            elif choice == '7':
                self.add_new_raw_material()
            elif choice == '8':
                print("Thank you for using the system. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")


# --- Execution ---
if __name__ == "__main__":
    manager = ProductManager()
    manager.run()