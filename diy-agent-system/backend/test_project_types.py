#!/usr/bin/env python3
"""
Test script to add products with project types
"""
import asyncio
from services.product_service import ProductService

async def test_project_types():
    """Add test products with project types"""
    
    # Add a table saw with woodworking project type
    table_saw = ProductService.create_product(
        title="DEWALT 10-Inch Table Saw",
        description="Professional table saw perfect for woodworking projects",
        product_url="https://www.amazon.com/test-table-saw",
        category="tools",
        merchant="amazon",
        original_price=599.99,
        sale_price=499.99,
        brand="DEWALT",
        model="DWE7491RS",
        rating=4.7,
        rating_count=1234,
        is_featured=True,
        project_types=["woodworking", "general"]  # This is the key field!
    )
    
    # Add PVC pipe with plumbing project type  
    pvc_pipe = ProductService.create_product(
        title="PVC Pipe 3-inch x 10ft",
        description="High-quality PVC pipe for plumbing projects",
        product_url="https://www.homedepot.com/test-pvc-pipe",
        category="materials",
        merchant="home_depot",
        original_price=15.99,
        sale_price=12.99,
        brand="Charlotte Pipe",
        rating=4.5,
        rating_count=567,
        project_types=["plumbing", "general"]  # This is the key field!
    )
    
    # Add wire cutters with electrical project type
    wire_cutters = ProductService.create_product(
        title="Klein Tools Wire Strippers/Cutters",
        description="Professional wire cutting tools for electrical work",
        product_url="https://www.amazon.com/test-wire-cutters",
        category="tools", 
        merchant="amazon",
        original_price=45.99,
        sale_price=39.99,
        brand="Klein Tools",
        model="11061",
        rating=4.8,
        rating_count=2345,
        project_types=["electrical", "general"]  # This is the key field!
    )
    
    # Add cordless drill with multiple project types
    drill = ProductService.create_product(
        title="Milwaukee M18 FUEL Drill/Driver",
        description="Versatile drill good for most DIY projects",
        product_url="https://www.homedepot.com/test-drill",
        category="tools",
        merchant="home_depot", 
        original_price=199.99,
        sale_price=159.99,
        brand="Milwaukee",
        model="2704-20",
        rating=4.9,
        rating_count=3456,
        is_featured=True,
        project_types=["woodworking", "electrical", "plumbing", "general", "home_improvement"]  # Multiple types!
    )
    
    print("Test products created:")
    if table_saw:
        print(f"✓ Table Saw: {table_saw['title']} - Project Types: {table_saw['project_types']}")
    if pvc_pipe:
        print(f"✓ PVC Pipe: {pvc_pipe['title']} - Project Types: {pvc_pipe['project_types']}")
    if wire_cutters:
        print(f"✓ Wire Cutters: {wire_cutters['title']} - Project Types: {wire_cutters['project_types']}")
    if drill:
        print(f"✓ Drill: {drill['title']} - Project Types: {drill['project_types']}")
    
    return [table_saw, pvc_pipe, wire_cutters, drill]

if __name__ == "__main__":
    products = asyncio.run(test_project_types())
    print(f"\nCreated {len([p for p in products if p])} products successfully!")