"""
Admin Dashboard API endpoints
Provides real-time statistics and data for admin dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import logging

from app.database import get_db
from app.models.user import User
from app.models.product import Product, ProductAnalysis
from app.core.auth import require_admin as get_current_admin_user
from app.agents.product_info_agent import product_info_agent

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

logger = logging.getLogger(__name__)


@router.options("/products/analyze-url")
async def analyze_url_options():
    """Handle OPTIONS request for analyze-url endpoint"""
    return Response(status_code=200)

@router.options("/products/create-from-analysis")
async def create_from_analysis_options():
    """Handle OPTIONS request for create-from-analysis endpoint"""
    return Response(status_code=200)


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get real-time dashboard statistics"""
    
    # Get current time and today's start
    now = datetime.utcnow()
    today_start = datetime.combine(now.date(), datetime.min.time())
    
    # Count total users
    total_users_query = select(func.count(User.id))
    total_users = await db.scalar(total_users_query)
    
    # Count new users today
    new_users_today_query = select(func.count(User.id)).where(
        User.created_at >= today_start
    )
    new_users_today = await db.scalar(new_users_today_query) or 0
    
    # Count total products
    total_products_query = select(func.count(Product.id))
    total_products = await db.scalar(total_products_query) or 0
    
    # Count product analyses (tools identified)
    tools_identified_query = select(func.count(ProductAnalysis.id))
    tools_identified = await db.scalar(tools_identified_query) or 0
    
    # Count today's analyses
    tools_today_query = select(func.count(ProductAnalysis.id)).where(
        ProductAnalysis.created_at >= today_start
    )
    tools_today = await db.scalar(tools_today_query) or 0
    
    # For now, we'll use calculated values for some stats
    projects_analyzed = tools_identified // 3  # Estimate
    projects_today = tools_today // 2  # Estimate
    recommendations = tools_identified * 4  # Estimate
    recommendations_today = tools_today * 4  # Estimate
    
    return {
        "total_users": total_users,
        "new_users_today": new_users_today,
        "tools_identified": tools_identified,
        "tools_today": tools_today,
        "projects_analyzed": projects_analyzed,
        "projects_today": projects_today,
        "recommendations": recommendations,
        "recommendations_today": recommendations_today,
        "total_products": total_products
    }


@router.get("/dashboard/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get recent system activity"""
    
    activities = []
    
    try:
        # Get recent user registrations
        recent_users_query = select(User).order_by(User.created_at.desc()).limit(3)
        recent_users_result = await db.scalars(recent_users_query)
        recent_users = list(recent_users_result)
        
        for user in recent_users:
            activities.append({
                "id": f"user_{user.id}",
                "type": "user",
                "icon": "User",
                "title": "New user registration",
                "description": f"{user.email} registered",
                "user": "System",
                "timestamp": user.created_at.isoformat() if user.created_at else datetime.now().isoformat()
            })
    
    except Exception as e:
        print(f"User activity error: {e}")
    
    # Add some mock recent activities if there are no real ones
    if not activities:
        activities = [
            {
                "id": "mock_1",
                "type": "user",
                "icon": "User",
                "title": "New user registration",
                "description": "admin@test.com registered",
                "user": "System",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "mock_2", 
                "type": "tool",
                "icon": "Search",
                "title": "Tool identification",
                "description": "Analysis completed",
                "user": "Anonymous",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()
            },
            {
                "id": "mock_3",
                "type": "project",
                "icon": "DataAnalysis", 
                "title": "Project analysis",
                "description": "DIY project analyzed",
                "user": "Anonymous",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
    
    # Sort activities by timestamp  
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities[:limit]


@router.get("/dashboard/feature-usage")
async def get_feature_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get feature usage statistics"""
    
    # Get counts for different analysis types
    # This is simplified - in production you'd track actual feature usage
    total_analyses = await db.scalar(select(func.count(ProductAnalysis.id))) or 0
    
    if total_analyses > 0:
        # Calculate percentages based on analysis types
        tool_identification_pct = 45  # Example percentage
        smart_finder_pct = 30
        project_analysis_pct = 15
        our_picks_pct = 10
    else:
        tool_identification_pct = 0
        smart_finder_pct = 0
        project_analysis_pct = 0
        our_picks_pct = 0
    
    return {
        "tool_identification": tool_identification_pct,
        "smart_tool_finder": smart_finder_pct,
        "project_analysis": project_analysis_pct,
        "our_picks": our_picks_pct,
        "total_usage": total_analyses
    }


@router.get("/dashboard/user-growth")
async def get_user_growth(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user growth data for the last N days"""
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get user registrations per day
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_start = datetime.combine(current_date, datetime.min.time())
        day_end = datetime.combine(current_date, datetime.max.time())
        
        count_query = select(func.count(User.id)).where(
            User.created_at >= day_start,
            User.created_at <= day_end
        )
        count = await db.scalar(count_query) or 0
        
        daily_data.append({
            "date": current_date.isoformat(),
            "count": count
        })
        
        current_date += timedelta(days=1)
    
    return daily_data


@router.get("/users/summary")
async def get_users_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user summary statistics"""
    
    # Count users by type
    user_type_counts = {}
    for user_type in ['free', 'pro', 'premium', 'admin']:
        count_query = select(func.count(User.id)).where(User.user_type == user_type.upper())
        count = await db.scalar(count_query) or 0
        user_type_counts[user_type] = count
    
    # Count active vs inactive
    active_count = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    ) or 0
    
    inactive_count = await db.scalar(
        select(func.count(User.id)).where(User.is_active == False)
    ) or 0
    
    # Count verified emails
    verified_count = await db.scalar(
        select(func.count(User.id)).where(User.email_verified == True)
    ) or 0
    
    return {
        "user_types": user_type_counts,
        "active_users": active_count,
        "inactive_users": inactive_count,
        "verified_emails": verified_count,
        "total_users": active_count + inactive_count
    }


@router.get("/products/summary")
async def get_products_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get product summary statistics"""
    
    # Count total products
    total_products = await db.scalar(select(func.count(Product.id))) or 0
    
    # Count featured products
    featured_count = await db.scalar(
        select(func.count(Product.id)).where(Product.is_featured == True)
    ) or 0
    
    # Count by category
    categories_query = select(
        Product.category,
        func.count(Product.id)
    ).group_by(Product.category)
    
    categories_result = await db.execute(categories_query)
    category_counts = {cat: count for cat, count in categories_result}
    
    # Average rating
    avg_rating = await db.scalar(
        select(func.avg(Product.rating))
    ) or 0
    
    return {
        "total_products": total_products,
        "featured_products": featured_count,
        "categories": category_counts,
        "average_rating": round(avg_rating, 2)
    }


@router.get("/users")
async def get_users(
    skip: int = 0,
    limit: int = 20,
    search: str = None,
    user_type: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get users with filtering and pagination"""
    
    query = select(User)
    
    # Apply search filter
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.full_name.ilike(search_term))
        )
    
    # Apply user type filter
    if user_type:
        query = query.where(User.user_type == user_type.upper())
    
    # Apply status filter (map frontend status to is_active)
    if status:
        if status == "active":
            query = query.where(User.is_active == True)
        elif status == "inactive":
            query = query.where(User.is_active == False)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Apply pagination and ordering
    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    
    users = await db.scalars(query)
    user_list = []
    
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username or "N/A",
            "email": user.email,
            "full_name": user.full_name or "",
            "user_type": user.user_type.lower() if user.user_type else "free",
            "status": "active" if user.is_active else "inactive",
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "email_verified": user.email_verified,
            "avatar": user.avatar_url or ""
        })
    
    return {
        "users": user_list,
        "total": total
    }


@router.get("/products")
async def get_products(
    skip: int = 0,
    limit: int = 20,
    search: str = None,
    category: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get products with filtering and pagination"""
    
    query = select(Product)
    
    # Apply search filter
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            (Product.title.ilike(search_term)) |
            (Product.brand.ilike(search_term)) |
            (Product.model.ilike(search_term))
        )
    
    # Apply category filter
    if category:
        query = query.where(Product.category == category)
    
    # Apply status filter
    if status == "active":
        query = query.where(Product.is_active == True)
    elif status == "inactive":
        query = query.where(Product.is_active == False)
    elif status == "featured":
        query = query.where(Product.is_featured == True)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Apply pagination and ordering
    query = query.order_by(Product.created_at.desc()).offset(skip).limit(limit)
    
    products = await db.scalars(query)
    product_list = []
    
    for product in products:
        # Determine status
        if product.is_featured:
            product_status = "featured"
        elif product.is_active:
            product_status = "active"  
        else:
            product_status = "inactive"
            
        product_list.append({
            "id": product.id,
            "name": product.title,
            "brand": product.brand,
            "model": product.model or "N/A",
            "category": product.category,
            "price": product.price,
            "stock": 25,  # Mock stock since not in current model
            "rating": product.rating or 0,
            "status": product_status,
            "description": product.description or "",
            "image": product.image_url or "",
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            "in_stock": product.in_stock
        })
    
    return {
        "products": product_list,
        "total": total
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_type: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user (Admin only)"""
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting/disabling the last admin
    if user.user_type == "admin" and status == "inactive":
        admin_count = await db.scalar(
            select(func.count(User.id)).where(User.user_type == "admin", User.is_active == True)
        )
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot disable the last admin user")
    
    # Update fields
    if user_type:
        user.user_type = user_type.upper()
    if status:
        user.is_active = status == "active"
    
    await db.commit()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name or "",
        "user_type": user.user_type.lower() if user.user_type else "free",
        "status": "active" if user.is_active else "inactive",
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "email_verified": user.email_verified,
        "avatar": user.avatar_url or ""
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (Admin only)"""
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    # Prevent deleting the last admin
    if user.user_type == "admin":
        admin_count = await db.scalar(
            select(func.count(User.id)).where(User.user_type == "admin", User.is_active == True)
        )
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last admin user")
    
    # Delete user
    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"}


@router.put("/products/{product_id}")
async def update_product(
    product_id: str,
    title: str = Form(None),
    brand: str = Form(None),
    model: str = Form(None),
    category: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    rating: float = Form(None),
    is_featured: bool = Form(None),
    is_active: bool = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update product (Admin only)"""
    
    # Get product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    if title is not None:
        product.title = title
    if brand is not None:
        product.brand = brand
    if model is not None:
        product.model = model
    if category is not None:
        product.category = category
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if rating is not None:
        product.rating = rating
    if is_featured is not None:
        product.is_featured = is_featured
    if is_active is not None:
        product.is_active = is_active
    
    await db.commit()
    await db.refresh(product)
    
    # Determine status
    if product.is_featured:
        product_status = "featured"
    elif product.is_active:
        product_status = "active"  
    else:
        product_status = "inactive"
    
    return {
        "id": product.id,
        "name": product.title,
        "brand": product.brand,
        "model": product.model or "N/A",
        "category": product.category,
        "price": product.price,
        "stock": 25,  # Mock stock since not in current model
        "rating": product.rating or 0,
        "status": product_status,
        "description": product.description or "",
        "image": product.image_url or "",
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "in_stock": product.in_stock
    }


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete product (Admin only)"""
    
    # Get product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete product
    await db.delete(product)
    await db.commit()
    
    return {"message": "Product deleted successfully"}


@router.get("/products")
async def get_admin_products(
    skip: int = 0,
    limit: int = 20,
    search: str = None,
    category: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get products for admin management (with real database data)"""
    
    # Build base query
    query = select(Product)
    
    # Add filters
    conditions = []
    
    if search:
        conditions.append(
            Product.title.contains(search) | 
            Product.brand.contains(search) |
            Product.description.contains(search)
        )
    
    if category:
        conditions.append(Product.category == category)
    
    if status:
        if status == 'active':
            conditions.append(Product.is_active == True)
            conditions.append(Product.is_featured == False)
        elif status == 'inactive':
            conditions.append(Product.is_active == False)
        elif status == 'featured':
            conditions.append(Product.is_featured == True)
    
    # Apply conditions
    if conditions:
        from sqlalchemy import and_
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Product.created_at.desc()).offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Format products for frontend
    product_list = []
    for product in products:
        # Map database status to frontend status
        if product.is_featured:
            status = 'featured'
        elif product.is_active:
            status = 'active'
        else:
            status = 'inactive'
            
        product_list.append({
            "id": product.id,
            "name": product.title,
            "brand": product.brand or "Unknown",
            "model": product.model or "",
            "category": product.category,
            "price": float(product.original_price or product.sale_price or 0),
            "stock": 0,  # We don't have stock field in our model
            "rating": float(product.rating or 0),
            "status": status,
            "description": product.description or "",
            "image": product.image_url,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None
        })
    
    return {
        "products": product_list,
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit
    }


@router.get("/products/summary")
async def get_products_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get products summary statistics"""
    
    # Total products
    total_result = await db.execute(select(func.count()).select_from(Product))
    total_products = total_result.scalar()
    
    # Featured products
    featured_result = await db.execute(
        select(func.count()).select_from(Product).where(Product.is_featured == True)
    )
    featured_products = featured_result.scalar()
    
    # Active products
    active_result = await db.execute(
        select(func.count()).select_from(Product).where(Product.is_active == True)
    )
    active_products = active_result.scalar()
    
    # Categories
    categories_result = await db.execute(
        select(Product.category, func.count()).group_by(Product.category)
    )
    categories = dict(categories_result.all())
    
    return {
        "total_products": total_products,
        "featured_products": featured_products,
        "active_products": active_products,
        "inactive_products": total_products - active_products,
        "categories": categories
    }


@router.post("/products/analyze-url")
async def analyze_product_url(
    product_url: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Analyze a product URL using AI agent to extract product information
    """
    try:
        logger.info(f"Admin {current_user.email} analyzing product URL: {product_url}")
        
        # Check if this URL has been analyzed recently (within 24 hours)
        existing_analysis = await db.execute(
            select(ProductAnalysis).where(
                ProductAnalysis.source_url == product_url,
                ProductAnalysis.analysis_date > datetime.utcnow() - timedelta(hours=24)
            )
        )
        existing = existing_analysis.scalar_one_or_none()
        
        if existing:
            logger.info(f"Found recent analysis for {product_url}, returning cached result")
            return {
                "success": True,
                "analysis_id": existing.id,
                "extracted_data": {
                    "title": existing.extracted_title,
                    "brand": existing.extracted_brand,
                    "price": existing.extracted_price,
                    "description": existing.extracted_description,
                    "features": json.loads(existing.extracted_features or "[]"),
                    "images": json.loads(existing.extracted_images or "[]"),
                    "rating": existing.extracted_rating,
                    "review_count": existing.extracted_reviews,
                    "category": existing.category_prediction,
                    "project_types": json.loads(existing.project_suitability or "[]"),
                    "quality_assessment": existing.quality_assessment,
                    "image_url": json.loads(existing.extracted_images or "[]")[0] if existing.extracted_images and json.loads(existing.extracted_images) else None
                }
            }
        
        # Run product info agent to analyze the URL
        result = await product_info_agent.execute({"product_url": product_url})
        
        if not result.success:
            raise HTTPException(status_code=400, detail=f"Failed to analyze URL: {result.error}")
        
        extracted_data = result.data
        
        # Create new analysis record
        analysis = ProductAnalysis(
            source_url=product_url,
            extracted_title=extracted_data.get("title"),
            extracted_brand=extracted_data.get("brand"),
            extracted_price=extracted_data.get("sale_price") or extracted_data.get("original_price"),
            extracted_description=extracted_data.get("description"),
            extracted_features=json.dumps(extracted_data.get("key_features", [])),
            extracted_images=json.dumps([extracted_data.get("image_url")] if extracted_data.get("image_url") else []),
            extracted_rating=extracted_data.get("rating"),
            extracted_reviews=extracted_data.get("rating_count"),
            category_prediction=extracted_data.get("category"),
            project_suitability=json.dumps(extracted_data.get("project_types", [])),
            quality_assessment=f"Automated analysis - {extracted_data.get('extraction_method', 'unknown')}",
            analysis_metadata=json.dumps({
                "extraction_method": extracted_data.get("extraction_method"),
                "merchant": extracted_data.get("merchant"),
                "scraped": extracted_data.get("scraped", False),
                "specifications": extracted_data.get("specifications")
            })
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        logger.info(f"Created analysis record {analysis.id} for URL: {product_url}")
        
        return {
            "success": True,
            "analysis_id": analysis.id,
            "extracted_data": {
                "title": extracted_data.get("title"),
                "brand": extracted_data.get("brand"),
                "price": extracted_data.get("sale_price") or extracted_data.get("original_price"),
                "original_price": extracted_data.get("original_price"),
                "sale_price": extracted_data.get("sale_price"),
                "description": extracted_data.get("description"),
                "features": extracted_data.get("key_features", []),
                "image_url": extracted_data.get("image_url"),
                "rating": extracted_data.get("rating"),
                "review_count": extracted_data.get("rating_count"),
                "category": extracted_data.get("category"),
                "project_types": extracted_data.get("project_types", []),
                "quality_assessment": f"Automated analysis - {extracted_data.get('extraction_method', 'unknown')}",
                "specifications": extracted_data.get("specifications"),
                "merchant": extracted_data.get("merchant")
            }
        }
        
    except Exception as e:
        logger.error(f"Product URL analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/products/create-from-analysis")
async def create_product_from_analysis(
    analysis_id: str = Form(...),
    title: str = Form(None),
    brand: str = Form(None),
    model: str = Form(None),
    category: str = Form(...),
    description: str = Form(None),
    price: float = Form(None),
    rating: float = Form(None),
    affiliate_link: str = Form(...),
    admin_notes: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new product from analysis data
    """
    try:
        logger.info(f"Admin {current_user.email} creating product from analysis {analysis_id}")
        
        # Get the analysis record
        analysis_result = await db.execute(
            select(ProductAnalysis).where(ProductAnalysis.id == analysis_id)
        )
        analysis = analysis_result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Use provided data or fall back to extracted data
        product_data = {
            "title": title or analysis.extracted_title or "Untitled Product",
            "brand": brand or analysis.extracted_brand,
            "model": model,
            "category": category,
            "description": description or analysis.extracted_description,
            "original_price": price if price is not None else analysis.extracted_price,
            "sale_price": price if price is not None else analysis.extracted_price,
            "rating": rating if rating is not None else analysis.extracted_rating,
            "review_count": analysis.extracted_reviews,
            "affiliate_link": affiliate_link,
            "source_url": analysis.source_url,
            "is_active": True,
            "is_featured": False,
            "admin_notes": admin_notes,
        }
        
        # Extract image URL from analysis
        if analysis.extracted_images:
            images = json.loads(analysis.extracted_images)
            if images:
                product_data["image_url"] = images[0]
        
        # Create new product
        new_product = Product(**product_data)
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        
        logger.info(f"Created product {new_product.id} from analysis {analysis_id}")
        
        return {
            "success": True,
            "product_id": new_product.id,
            "product": {
                "id": new_product.id,
                "title": new_product.title,
                "brand": new_product.brand,
                "model": new_product.model,
                "category": new_product.category,
                "description": new_product.description,
                "price": new_product.original_price,
                "rating": new_product.rating,
                "image_url": new_product.image_url,
                "affiliate_link": new_product.affiliate_link,
                "is_active": new_product.is_active,
                "is_featured": new_product.is_featured,
                "created_at": new_product.created_at
            }
        }
        
    except Exception as e:
        logger.error(f"Product creation from analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Product creation failed: {str(e)}")