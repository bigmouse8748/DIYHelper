"""
Our Picks API Routes
Admin interface for managing curated products
"""
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Form, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import httpx

from ...database import get_db
from ...models.user import User
from ...models.product import Product, ProductAnalysis, ProductCategory, Retailer
from ...core.auth import get_current_user, require_admin
from ...agents.product_info_agent import product_info_agent
from pydantic import BaseModel

router = APIRouter(prefix="/our-picks", tags=["our-picks"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ProductAnalysisRequest(BaseModel):
    product_url: str

class ProductAnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    extracted_data: Dict[str, Any]
    error: Optional[str] = None

class ProductCreateRequest(BaseModel):
    analysis_id: str
    title: Optional[str] = None
    brand: Optional[str] = None
    category: str
    affiliate_link: str
    admin_notes: Optional[str] = None

class ProductListResponse(BaseModel):
    products: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    filters_applied: Dict[str, Any]

class ProductFilterParams(BaseModel):
    category: Optional[str] = None
    retailer: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    project_type: Optional[str] = None
    is_featured: Optional[bool] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"


@router.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product_url(
    product_url: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> ProductAnalysisResponse:
    """
    Admin endpoint: Analyze a product URL and extract information
    """
    try:
        logger.info(f"Admin {current_user.email} analyzing product URL: {product_url}")
        
        # Check if this URL has been analyzed recently
        existing_analysis = await db.execute(
            select(ProductAnalysis).where(
                and_(
                    ProductAnalysis.source_url == product_url,
                    ProductAnalysis.analysis_date > datetime.utcnow() - timedelta(hours=24)
                )
            )
        )
        existing = existing_analysis.scalar_one_or_none()
        
        if existing:
            logger.info(f"Found recent analysis for {product_url}, returning cached result")
            return ProductAnalysisResponse(
                success=True,
                analysis_id=existing.id,
                extracted_data={
                    "title": existing.extracted_title,
                    "brand": existing.extracted_brand,
                    "price": existing.extracted_price,
                    "description": existing.extracted_description,
                    "features": json.loads(existing.extracted_features or "[]"),
                    "images": json.loads(existing.extracted_images or "[]"),
                    "rating": existing.extracted_rating,
                    "review_count": existing.extracted_reviews,
                    "category_prediction": existing.category_prediction,
                    "project_suitability": json.loads(existing.project_suitability or "[]"),
                    "quality_assessment": existing.quality_assessment
                }
            )
        
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
        
        return ProductAnalysisResponse(
            success=True,
            analysis_id=analysis.id,
            extracted_data={
                "title": extracted_data.get("title"),
                "brand": extracted_data.get("brand"),
                "price": extracted_data.get("sale_price") or extracted_data.get("original_price"),
                "original_price": extracted_data.get("original_price"),
                "description": extracted_data.get("description"),
                "features": extracted_data.get("key_features", []),
                "images": [extracted_data.get("image_url")] if extracted_data.get("image_url") else [],
                "rating": extracted_data.get("rating"),
                "review_count": extracted_data.get("rating_count"),
                "category_prediction": extracted_data.get("category"),
                "project_suitability": extracted_data.get("project_types", []),
                "merchant": extracted_data.get("merchant"),
                "extraction_method": extracted_data.get("extraction_method"),
                "specifications": extracted_data.get("specifications")
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing product URL {product_url}: {str(e)}")
        return ProductAnalysisResponse(
            success=False,
            analysis_id="",
            extracted_data={},
            error=str(e)
        )


@router.post("/create")
async def create_product_from_analysis(
    request: ProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Admin endpoint: Create a product from analyzed data
    """
    try:
        # Get the analysis record
        result = await db.execute(
            select(ProductAnalysis).where(ProductAnalysis.id == request.analysis_id)
        )
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis record not found")
        
        # Check if product already exists for this analysis
        if analysis.product_id:
            raise HTTPException(status_code=400, detail="Product already created from this analysis")
        
        # Create product using analysis data and admin overrides
        product = Product(
            title=request.title or analysis.extracted_title,
            brand=request.brand or analysis.extracted_brand or "Unknown",
            category=request.category,
            description=analysis.extracted_description or "Product description not available",
            features=analysis.extracted_features,
            price=analysis.extracted_price or 0.0,
            original_price=None,  # Will be set if different from price
            retailer=json.loads(analysis.analysis_metadata or "{}").get("merchant", "other"),
            affiliate_link=request.affiliate_link,
            product_url=analysis.source_url,
            image_url=json.loads(analysis.extracted_images or "[]")[0] if json.loads(analysis.extracted_images or "[]") else None,
            additional_images=analysis.extracted_images,
            rating=analysis.extracted_rating or 0.0,
            review_count=analysis.extracted_reviews or 0,
            suitable_projects=analysis.project_suitability,
            admin_notes=request.admin_notes,
            is_active=True,
            quality_score=4.0  # Default quality score, admin can adjust later
        )
        
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        # Update analysis record to link to created product
        analysis.product_id = product.id
        analysis.approved = True
        analysis.approved_by = current_user.id
        analysis.approval_date = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Admin {current_user.email} created product {product.id} from analysis {analysis.id}")
        
        return {
            "success": True,
            "product_id": product.id,
            "message": "Product created successfully",
            "product": product.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error creating product from analysis {request.analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/products", response_model=ProductListResponse)
async def get_admin_products(
    category: Optional[str] = Query(None),
    retailer: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> ProductListResponse:
    """
    Admin endpoint: Get products with filtering and pagination
    """
    try:
        # Build query with filters
        query = select(Product).where(Product.is_active == True)
        count_query = select(func.count(Product.id)).where(Product.is_active == True)
        
        # Apply filters
        filters_applied = {}
        
        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)
            filters_applied["category"] = category
        
        if retailer:
            query = query.where(Product.retailer == retailer)
            count_query = count_query.where(Product.retailer == retailer)
            filters_applied["retailer"] = retailer
        
        if search:
            search_filter = or_(
                Product.title.ilike(f"%{search}%"),
                Product.brand.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
            filters_applied["search"] = search
        
        # Apply sorting
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute queries
        result = await db.execute(query)
        products = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Convert to dict format
        products_data = [product.to_dict() for product in products]
        
        return ProductListResponse(
            products=products_data,
            total_count=total_count,
            page=page,
            page_size=page_size,
            filters_applied=filters_applied
        )
        
    except Exception as e:
        logger.error(f"Error getting admin products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/public/products")
async def get_public_products(
    category: Optional[str] = Query(None),
    retailer: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_rating: Optional[float] = Query(None),
    project_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    sort_by: str = Query("rating"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Public endpoint: Get curated products for users with filtering
    """
    try:
        # Build query - only active products
        query = select(Product).where(
            and_(Product.is_active == True, Product.in_stock == True)
        )
        count_query = select(func.count(Product.id)).where(
            and_(Product.is_active == True, Product.in_stock == True)
        )
        
        # Apply filters
        filters_applied = {}
        
        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)
            filters_applied["category"] = category
        
        if retailer:
            query = query.where(Product.retailer == retailer)
            count_query = count_query.where(Product.retailer == retailer)
            filters_applied["retailer"] = retailer
        
        if min_price is not None:
            query = query.where(Product.price >= min_price)
            count_query = count_query.where(Product.price >= min_price)
            filters_applied["min_price"] = min_price
        
        if max_price is not None:
            query = query.where(Product.price <= max_price)
            count_query = count_query.where(Product.price <= max_price)
            filters_applied["max_price"] = max_price
        
        if min_rating is not None:
            query = query.where(Product.rating >= min_rating)
            count_query = count_query.where(Product.rating >= min_rating)
            filters_applied["min_rating"] = min_rating
        
        if project_type:
            # Search in JSON field for project type
            query = query.where(Product.suitable_projects.like(f'%"{project_type}"%'))
            count_query = count_query.where(Product.suitable_projects.like(f'%"{project_type}"%'))
            filters_applied["project_type"] = project_type
        
        if is_featured is not None:
            query = query.where(Product.is_featured == is_featured)
            count_query = count_query.where(Product.is_featured == is_featured)
            filters_applied["is_featured"] = is_featured
        
        if search:
            search_filter = or_(
                Product.title.ilike(f"%{search}%"),
                Product.brand.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
            filters_applied["search"] = search
        
        # Apply sorting
        valid_sort_columns = ["price", "rating", "created_at", "title", "brand"]
        if sort_by not in valid_sort_columns:
            sort_by = "rating"
        
        sort_column = getattr(Product, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute queries
        result = await db.execute(query)
        products = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Convert to public dict format (excluding admin fields)
        products_data = []
        for product in products:
            product_dict = product.to_dict()
            # Remove admin-only fields for public API
            public_product = {k: v for k, v in product_dict.items() 
                            if k not in ['admin_notes', 'click_count', 'conversion_count', 'affiliate_commission_rate']}
            products_data.append(public_product)
        
        return {
            "success": True,
            "products": products_data,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "filters_applied": filters_applied,
            "available_filters": {
                "categories": [e.value for e in ProductCategory],
                "retailers": [e.value for e in Retailer],
                "project_types": ["woodworking", "electronics", "automotive", "home_improvement", "gardening", "crafts", "plumbing", "electrical", "general"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting public products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/analyses")
async def get_pending_analyses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Admin endpoint: Get pending product analyses awaiting approval
    """
    try:
        result = await db.execute(
            select(ProductAnalysis)
            .where(ProductAnalysis.approved == False)
            .order_by(ProductAnalysis.analysis_date.desc())
            .limit(50)
        )
        analyses = result.scalars().all()
        
        analyses_data = []
        for analysis in analyses:
            analyses_data.append({
                "id": analysis.id,
                "source_url": analysis.source_url,
                "analysis_date": analysis.analysis_date.isoformat(),
                "extracted_title": analysis.extracted_title,
                "extracted_brand": analysis.extracted_brand,
                "extracted_price": analysis.extracted_price,
                "category_prediction": analysis.category_prediction,
                "quality_assessment": analysis.quality_assessment,
                "has_product": analysis.product_id is not None
            })
        
        return {
            "success": True,
            "pending_analyses": analyses_data,
            "count": len(analyses_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting pending analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track-click/{product_id}")
async def track_affiliate_click(
    product_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Track affiliate link clicks (public endpoint)
    """
    try:
        # Get product to verify it exists
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Increment click count
        product.click_count += 1
        await db.commit()
        
        return {
            "success": True,
            "affiliate_link": product.affiliate_link,
            "message": "Click tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Error tracking click for product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/products/{product_id}")
async def get_product_details(
    product_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information for a specific product (admin only)
    """
    try:
        logger.info(f"Looking for product with ID: {product_id}")
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        logger.info(f"Query result: {product}")
        
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "success": True,
            "product": {
                "id": str(product.id),
                "title": product.title,
                "description": product.description,
                "brand": product.brand,
                "model": product.model,
                "category": str(product.category) if product.category else "other",
                "retailer": str(product.retailer) if product.retailer else "other",
                "price": float(product.price) if product.price else None,
                "original_price": float(product.original_price) if product.original_price else None,
                "rating": float(product.rating) if product.rating else None,
                "review_count": product.review_count,
                "image_url": product.image_url,
                "affiliate_link": product.affiliate_link,
                "suitable_projects": product.suitable_projects,
                "is_featured": product.is_featured,
                "in_stock": product.in_stock,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/products/{product_id}")
async def update_product(
    product_id: str,
    title: str = Form(...),
    description: str = Form(...),
    brand: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    category: str = Form(...),
    retailer: str = Form(...),
    price: Optional[float] = Form(None),
    original_price: Optional[float] = Form(None),
    rating: Optional[float] = Form(None),
    review_count: Optional[int] = Form(None),
    image_url: Optional[str] = Form(None),
    affiliate_link: str = Form(...),
    suitable_projects: str = Form(default='["general"]'),
    is_featured: bool = Form(default=False),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update a product (admin only)
    """
    try:
        # Get existing product
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Validate and parse suitable_projects
        try:
            projects_list = json.loads(suitable_projects) if suitable_projects else ["general"]
            if not isinstance(projects_list, list):
                projects_list = ["general"]
        except:
            projects_list = ["general"]
        
        # Update product fields
        product.title = title
        product.description = description
        if brand is not None:
            product.brand = brand
        if model is not None:
            product.model = model
        
        # Handle enum fields
        try:
            product.category = ProductCategory(category)
        except ValueError:
            product.category = ProductCategory.other
            
        try:
            product.retailer = Retailer(retailer)
        except ValueError:
            product.retailer = Retailer.other
        
        if price is not None:
            product.price = price
        product.original_price = original_price
        product.rating = rating if rating is not None and 0 <= rating <= 5 else None
        product.review_count = review_count if review_count is not None and review_count >= 0 else None
        if image_url is not None:
            product.image_url = image_url
        product.affiliate_link = affiliate_link
        product.suitable_projects = json.dumps(projects_list)
        product.is_featured = is_featured
        product.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(product)
        
        logger.info(f"Product {product_id} updated by admin {current_user.username}")
        
        return {
            "success": True,
            "message": "Product updated successfully",
            "product_id": str(product.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")


@router.delete("/admin/products/{product_id}")
async def delete_product(
    product_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete a product (admin only)
    """
    try:
        # Get product to verify it exists
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_title = product.title
        
        # Delete the product (this will cascade to related records if configured)
        await db.delete(product)
        await db.commit()
        
        logger.info(f"Product '{product_title}' ({product_id}) deleted by admin {current_user.username}")
        
        return {
            "success": True,
            "message": f"Product '{product_title}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")


@router.post("/manual-create")
async def create_product_manually(
    title: str = Form(...),
    description: str = Form(...),
    brand: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    category: str = Form(...),
    retailer: str = Form(...),
    price: Optional[float] = Form(None),
    original_price: Optional[float] = Form(None),
    rating: Optional[float] = Form(None),
    review_count: Optional[int] = Form(None),
    image_url: Optional[str] = Form(None),
    affiliate_link: str = Form(...),
    suitable_projects: str = Form(default='["general"]'),
    is_featured: bool = Form(default=False),
    admin_notes: Optional[str] = Form(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Admin endpoint: Create a product manually without analysis
    """
    try:
        logger.info(f"Admin {current_user.email} creating product manually: {title}")
        
        # Validate and parse suitable_projects
        try:
            projects_list = json.loads(suitable_projects) if suitable_projects else ["general"]
            if not isinstance(projects_list, list):
                projects_list = ["general"]
        except:
            projects_list = ["general"]
        
        # Create product directly
        product = Product(
            title=title,
            brand=brand or "Unknown",
            model=model,
            category=category,
            description=description,
            price=price or 0.0,
            original_price=original_price,
            retailer=retailer,
            affiliate_link=affiliate_link,
            image_url=image_url,
            rating=rating if rating is not None and 0 <= rating <= 5 else None,
            review_count=review_count if review_count is not None and review_count >= 0 else None,
            suitable_projects=json.dumps(projects_list),
            admin_notes=admin_notes,
            is_featured=is_featured,
            is_active=True,
            in_stock=True,
            quality_score=4.0  # Default quality score
        )
        
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        logger.info(f"Admin {current_user.email} created product {product.id} manually")
        
        return {
            "success": True,
            "product_id": product.id,
            "message": "Product created successfully",
            "product": product.to_dict()
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating product manually: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.get("/image-proxy")
async def proxy_product_image(url: str):
    """
    Proxy images to avoid CORS issues and provide fallback for broken images
    """
    logger.info(f"Image proxy requested for URL: {url}")
    
    # Just redirect to the URL for now - test the endpoint works
    return Response(
        content="",
        status_code=302,
        headers={"Location": url}
    )