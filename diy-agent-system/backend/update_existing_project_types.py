#!/usr/bin/env python3
"""
Update existing products with appropriate project types
"""
import sqlite3
import json
from pathlib import Path

def update_existing_products():
    """Add project types to existing products"""
    
    db_path = Path(__file__).parent / "local_test.db"
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all products
        cursor.execute("SELECT id, title, category, merchant FROM product_recommendations WHERE project_types = '[]' OR project_types IS NULL")
        products = cursor.fetchall()
        
        print(f"Found {len(products)} products to update:")
        
        for product_id, title, category, merchant in products:
            print(f"  - ID {product_id}: {title}")
            
            # Assign project types based on product type
            project_types = []
            
            title_lower = title.lower()
            
            # Table saws -> woodworking
            if 'table saw' in title_lower or 'saw' in title_lower:
                project_types = ['woodworking', 'general']
            # Drills -> multiple types (very versatile)
            elif 'drill' in title_lower:
                project_types = ['woodworking', 'electrical', 'general', 'home_improvement']
            # Circular saws -> woodworking
            elif 'circular' in title_lower:
                project_types = ['woodworking', 'general']
            # PVC/pipe -> plumbing
            elif 'pvc' in title_lower or 'pipe' in title_lower:
                project_types = ['plumbing', 'general']
            # Wire/electrical -> electrical
            elif 'wire' in title_lower or 'electrical' in title_lower:
                project_types = ['electrical', 'general']
            # Screws/fasteners -> general woodworking
            elif 'screw' in title_lower or 'pocket' in title_lower:
                project_types = ['woodworking', 'general']
            # Default for tools
            elif category == 'tools':
                project_types = ['general', 'home_improvement']
            # Default for materials
            elif category == 'materials':
                project_types = ['general']
            else:
                project_types = ['general']
            
            # Update the product
            project_types_json = json.dumps(project_types)
            cursor.execute(
                "UPDATE product_recommendations SET project_types = ? WHERE id = ?",
                (project_types_json, product_id)
            )
            
            print(f"    -> Updated with project types: {project_types}")
        
        conn.commit()
        print(f"\nSuccessfully updated {len(products)} products!")
        
        # Verify the updates
        print("\nVerification:")
        cursor.execute("SELECT title, project_types FROM product_recommendations")
        all_products = cursor.fetchall()
        
        for title, project_types in all_products:
            project_types_list = json.loads(project_types) if project_types else []
            print(f"  - {title[:50]}... -> {project_types_list}")
        
    except Exception as e:
        print(f"Update failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_existing_products()