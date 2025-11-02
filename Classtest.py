import uuid

# --- 1. Raw Material Model ---
class RawMaterial:
    """Represents a basic raw material."""
    def __init__(self, name, unit_cost):
        self.name = name
        self.unit_cost = unit_cost

    def __str__(self):
        return f"{self.name} (Cost: ${self.unit_cost:.2f})"

# --- 2. Product Type Model (The Standardizer) ---
class ProductType:
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
        # e.g., ["length_cm", "width_cm"]
        self.required_variables = []
        # Function/Lambda to calculate final price based on material cost and user variables
        # Default: just material cost * 1.5 markup
        self.price_formula = lambda material_cost, vars: material_cost * 1.5

    def add_material(self, material_name, factor):
        """Adds or updates a raw material and its proportional factor."""
        self.materials_recipe[material_name] = factor

    def add_variable(self, variable_name):
        """Adds a user-required variable."""
        if variable_name not in self.required_variables:
            self.required_variables.append(variable_name)

    def set_price_formula(self, formula):
        """Sets a custom pricing formula (a lambda function)."""
        self.price_formula = formula

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


# --- 3. Product Instance Model ---
class Product:
    """Represents an individual manufactured product based on a ProductType."""
    def __init__(self, product_type, user_variables, all_materials):
        self.id = uuid.uuid4()
        self.product_type = product_type
        self.user_variables = user_variables
        self.material_cost = 0
        self.final_price = 0
        
        # Evaluate cost and price upon creation
        self._evaluate_cost_and_price(all_materials)

    def _evaluate_cost_and_price(self, all_materials):
        """Calculates the final cost and price based on the product type's recipe and user variables."""
        
        # 1. Base Material Cost from Product Type (Standardized)
        base_cost = self.product_type.calculate_material_cost(all_materials)
        
        # 2. Apply a scaling factor from user input (example logic)
        # Assuming the first user variable (e.g., "size_factor") scales the cost.
        scaling_factor = self.user_variables.get(self.product_type.required_variables[0], 1) if self.product_type.required_variables else 1
        
        self.material_cost = base_cost * scaling_factor
        
        # 3. Calculate Final Price using the Product Type's formula
        self.final_price = self.product_type.price_formula(self.material_cost, self.user_variables)

    def __str__(self):
        vars_str = ', '.join([f"{k}: {v}" for k, v in self.user_variables.items()])
        return (f"Product ID: {str(self.id).split('-')[0]} | Type: {self.product_type.name}\n"
                f"  Variables: {vars_str}\n"
                f"  Material Cost: ${self.material_cost:.2f} | Final Price: ${self.final_price:.2f}")


# --- 4. Product Manager (The System Controller) ---
class ProductManager:
    """Manages Product Types and Products, handles user interaction."""
    def __init__(self):
        # Data Storage
        # {name: ProductType_object}
        self.product_types = {}
        # [Product_object]
        self.products = []
        # {name: RawMaterial_object} - Pre-populated for demonstration
        self.raw_materials = {
            "Steel": RawMaterial("Steel", 5.00),
            "Plastic": RawMaterial("Plastic", 1.50),
            "Wood": RawMaterial("Wood", 3.00),
        }

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

        print("\n--- Define Recipe & Variables ---")
        
        # Raw Materials
        print("Available Raw Materials: " + ", ".join(self.raw_materials.keys()))
        while self._get_input("Add a Raw Material to the recipe? (yes/no)").lower() == 'yes':
            mat_name = self._get_input("Enter Raw Material Name").title()
            if mat_name in self.raw_materials:
                factor = self._get_input(f"Enter proportional factor for {mat_name} (e.g., 2.5)", float)
                new_type.add_material(mat_name, factor)
            else:
                print(f"Error: Raw Material '{mat_name}' not found.")

        # Dependent Variables
        print("\n--- Define Dependent Variables ---")
        print("These variables will be asked for on product creation.")
        while self._get_input("Add a required user variable? (yes/no)").lower() == 'yes':
            var_name = self._get_input("Enter Variable Name (e.g., 'size_factor', 'color')")
            new_type.add_variable(var_name.lower().replace(" ", "_"))

        self.product_types[name] = new_type
        print(f"\n✅ Product Type '{name}' created successfully!")
    
    def view_existing_product_types(self):
        """Displays details of all existing ProductTypes."""
        print("\n--- 📝 Existing Product Types ---")
        if not self.product_types:
            print("No product types have been defined yet.")
            return

        for name, p_type in self.product_types.items():
            print("-" * 40)
            print(p_type.get_details(self.raw_materials))
        print("-" * 40)

    def modify_existing_product_type(self):
        """Simple modification option (can be expanded)."""
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
            mat_name = self._get_input("Enter Raw Material Name").title()
            if mat_name in self.raw_materials:
                factor = self._get_input(f"Enter NEW proportional factor for {mat_name}", float)
                p_type.add_material(mat_name, factor)
                print(f"✅ Recipe updated for {name}.")
            else:
                print(f"Error: Raw Material '{mat_name}' not found.")
        elif choice == 2:
            var_name = self._get_input("Enter NEW Variable Name").lower().replace(" ", "_")
            p_type.add_variable(var_name)
            print(f"✅ Variable '{var_name}' added to {name}.")
        else:
            print("Invalid choice.")
            
    # --- Product Creation Method ---
    def create_product_instance(self):
        """Creates an actual product instance based on a selected ProductType."""
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
            # Simple attempt to cast to float if it looks like a number
            try:
                user_vars[var_name] = float(value)
            except ValueError:
                user_vars[var_name] = value

        new_product = Product(p_type, user_vars, self.raw_materials)
        self.products.append(new_product)
        print("\n✅ Product created:")
        print(new_product)

    # --- Main Application Loop ---
    def run(self):
        """The main command-line interface loop."""
        print("--- Custom Manufacturing Product System ---")
        while True:
            print("\n" + "="*30)
            print("Main Menu:")
            print("1. Create New Product Type")
            print("2. View Existing Product Types")
            print("3. Modify Existing Product Type")
            print("4. Create New Product (Instance)")
            print("5. View All Products")
            print("6. Exit")
            print("="*30)

            choice = self._get_input("Enter your choice (1-6)", str)
            
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
                print("Thank you for using the system. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")


# --- Execution ---
if __name__ == "__main__":
    manager = ProductManager()
    manager.run()