from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from .. import schemas
from .. database import get_db, Product, Category, Inventory

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Product])
def get_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=schemas.ProductDetail)
def get_product(
    product_id: int = Path(..., description="The ID of the product to get"),
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product
    """
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db_inventory = Inventory(
        product_id=db_product.id,
        quantity=0,
        low_stock_threshold=10
    )
    db.add(db_inventory)
    db.commit()
    
    return db_product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update product information
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_update.name is not None:
        db_product.name = product_update.name
    
    if product_update.description is not None:
        db_product.description = product_update.description
    
    if product_update.price is not None:
        db_product.price = product_update.price
    
    if product_update.category_id is not None:
        category = db.query(Category).filter(Category.id == product_update.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_product.category_id = product_update.category_id
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    
    return db_product

@router.get("/category/{category_id}", response_model=List[schemas.Product])
def get_products_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get products by category
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    products = db.query(Product).filter(
        Product.category_id == category_id
    ).offset(skip).limit(limit).all()
    
    return products