from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

# Product schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ProductDetail(Product):
    category: Category
    
    class Config:
        orm_mode = True

# Inventory schemas
class InventoryBase(BaseModel):
    product_id: int
    quantity: int
    low_stock_threshold: int = 10

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None

class Inventory(InventoryBase):
    id: int
    last_updated: datetime
    
    class Config:
        orm_mode = True

class InventoryDetail(Inventory):
    product: Product
    
    class Config:
        orm_mode = True

class InventoryHistoryBase(BaseModel):
    inventory_id: int
    previous_quantity: int
    new_quantity: int

class InventoryHistory(InventoryHistoryBase):
    id: int
    change_date: datetime
    
    class Config:
        orm_mode = True

# Sale schemas
class SaleBase(BaseModel):
    product_id: int
    quantity: int
    total_price: float
    platform: Optional[str] = None

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    sale_date: datetime
    
    class Config:
        orm_mode = True

class SaleDetail(Sale):
    product: Product
    
    class Config:
        orm_mode = True

# Analysis schemas
class DateRange(BaseModel):
    start_date: date
    end_date: date

class SaleSummary(BaseModel):
    period: str
    total_sales: int
    total_revenue: float
    products_sold: int

class SalesComparison(BaseModel):
    period1: SaleSummary
    period2: SaleSummary
    change_percentage: float

class LowStockProduct(BaseModel):
    product_id: int
    product_name: str
    current_quantity: int
    threshold: int
    
    class Config:
        orm_mode = True
