from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .. import schemas
from .. database import get_db, Inventory, InventoryHistory, Product

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.InventoryDetail])
def get_inventory(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get current inventory status for all products
    """
    inventory = db.query(Inventory).offset(skip).limit(limit).all()
    return inventory

@router.get("/low-stock", response_model=List[schemas.LowStockProduct])
def get_low_stock(db: Session = Depends(get_db)):
    """
    Get products with inventory below the low stock threshold
    """
    low_stock_items = db.query(
        Inventory.product_id,
        Product.name.label("product_name"),
        Inventory.quantity.label("current_quantity"),
        Inventory.low_stock_threshold.label("threshold")
    ).join(Product).filter(
        Inventory.quantity <= Inventory.low_stock_threshold
    ).all()
    
    return [
        schemas.LowStockProduct(
            product_id=item.product_id,
            product_name=item.product_name,
            current_quantity=item.current_quantity,
            threshold=item.threshold
        ) for item in low_stock_items
    ]

@router.put("/{product_id}", response_model=schemas.Inventory)
def update_inventory(
    product_id: int = Path(..., description="The ID of the product to update"),
    inventory_update: schemas.InventoryUpdate = None,
    db: Session = Depends(get_db)
):
    """
    Update inventory level for a product
    """
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    previous_quantity = inventory.quantity
    if inventory_update.quantity is not None:
        inventory.quantity = inventory_update.quantity
    
    if inventory_update.low_stock_threshold is not None:
        inventory.low_stock_threshold = inventory_update.low_stock_threshold
    if previous_quantity != inventory.quantity:
        history = InventoryHistory(
            inventory_id=inventory.id,
            previous_quantity=previous_quantity,
            new_quantity=inventory.quantity
        )
        db.add(history)
    
    db.commit()
    db.refresh(inventory)
    
    return inventory

@router.get("/history/{product_id}", response_model=List[schemas.InventoryHistory])
def get_inventory_history(
    product_id: int = Path(..., description="The ID of the product"),
    limit: int = Query(10, description="Number of history records to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get inventory change history for a product
    """
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    history = db.query(InventoryHistory).filter(
        InventoryHistory.inventory_id == inventory.id
    ).order_by(InventoryHistory.change_date.desc()).limit(limit).all()
    
    return history