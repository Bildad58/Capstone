Inventory Management System

Project Overview
This Django-based Inventory Management System allows users to manage product inventories, track inventory changes, and maintain supplier, category, and store information. It also keeps a log of inventory changes such as sales, restocks, adjustments, and returns.

Models
1. Category
    Fields:
        name: A unique name for the category.
        description: An optional description for the category.
        Purpose: Represents a category to which inventory products belong.

2. Supplier
    Fields:
        name: Supplier's name.
        contact: A unique contact number.
        email: Supplier's email address.
        address: Supplier's physical address.
        Purpose: Represents suppliers who provide products.

3. Store
    Fields:
        name: Store's name.
        email: Store's email address.
        address: Store's physical address.
        contact: A unique contact number for the store.
        Purpose: Represents the physical store where products are stored.

4. InventoryProduct
    Fields:
        name: Name of the product.
        description: Optional description of the product.
        category: Foreignkey relation to Category.
        quantity: The current stock of the product.
        price: Price of the product.
        date_added: Automatically set when the product is added.
        last_updated: Automatically set when the product is updated.
        user: The user who added or manages the product.
        supplier: ForeignKey relation to Supplier.
        store: ForeignKey relation to Store.
        barcode: Optional unique barcode for the product.
        reorder_level: The stock quantity at which the product should be reordered.
        Purpose: Represents the products in the inventory system, along with details like quantity, price, and supplier.

5. InventoryChange
    Fields:
        product: ForeignKey relation to InventoryProduct.
        quantity: The new quantity after the change.
        quantity_change: The amount of the change.
        timestamp: Automatically set when the change occurs.
        user: The user who made the change.
        reason: The reason for the change (Sale, Restock, Adjustment, Return).
        Purpose: Tracks changes in the product inventory (e.g., sales, restocks, adjustments).

Key Features
    Product Management: Add and manage products with detailed information like quantity, price, category, supplier, and store.
    Inventory Change Tracking: Log and track inventory changes such as sales, restocking, adjustments, or returns.
    Category and Supplier Management: Maintain categories for products and supplier information for product sourcing.
    Store Tracking: Associate products with a physical store location.
