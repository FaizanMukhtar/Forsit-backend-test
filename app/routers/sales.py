from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime, timedelta

from .. import schemas
from .. database import get_db, Sale, Product, Category
from sqlalchemy.sql import text

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.SaleDetail])
def get_sales(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get all sales records with pagination
    """
    sales = db.query(Sale).offset(skip).limit(limit).all()
    return sales

@router.get("/daily", response_model=List[schemas.SaleSummary])
def get_daily_sales(
    days: int = Query(7, description="Number of days to analyze"), 
    db: Session = Depends(get_db)
):
    """
    Get daily sales summary for the last specified number of days
    """
    results = []
    today = datetime.utcnow().date()
    
    for i in range(days):
        target_date = today - timedelta(days=i)
        next_date = target_date + timedelta(days=1)
        day_sales = db.query(Sale).filter(
            Sale.sale_date >= target_date,
            Sale.sale_date < next_date
        ).all()

        total_sales = len(day_sales)
        total_revenue = sum(sale.total_price for sale in day_sales)
        products_sold = sum(sale.quantity for sale in day_sales)
        
        results.append(
            schemas.SaleSummary(
                period=target_date.strftime("%Y-%m-%d"),
                total_sales=total_sales,
                total_revenue=total_revenue,
                products_sold=products_sold
            )
        )
    
    return results

@router.get("/weekly", response_model=List[schemas.SaleSummary])
def get_weekly_sales(
    weeks: int = Query(4, description="Number of weeks to analyze"), 
    db: Session = Depends(get_db)
):
    """
    Get weekly sales summary for the last specified number of weeks
    """
    results = []
    today = datetime.utcnow().date()
    
    for i in range(weeks):
        end_date = today - timedelta(days=i*7)
        start_date = end_date - timedelta(days=7)
        
        week_sales = db.query(Sale).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date < end_date
        ).all()

        total_sales = len(week_sales)
        total_revenue = sum(sale.total_price for sale in week_sales)
        products_sold = sum(sale.quantity for sale in week_sales)
        
        results.append(
            schemas.SaleSummary(
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                total_sales=total_sales,
                total_revenue=total_revenue,
                products_sold=products_sold
            )
        )
    
    return results

@router.get("/monthly", response_model=List[schemas.SaleSummary])
def get_monthly_sales(
    months: int = Query(6, description="Number of months to analyze"), 
    db: Session = Depends(get_db)
):
    """
    Get monthly sales summary for the last specified number of months
    """
    results = []
    today = datetime.utcnow().date()
    current_month = today.month
    current_year = today.year
    
    for i in range(months):
        target_month = current_month - i
        target_year = current_year
        
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        
        month_sales = db.query(Sale).filter(
            extract('year', Sale.sale_date) == target_year,
            extract('month', Sale.sale_date) == target_month
        ).all()

        total_sales = len(month_sales)
        total_revenue = sum(sale.total_price for sale in month_sales)
        products_sold = sum(sale.quantity for sale in month_sales)
        
        results.append(
            schemas.SaleSummary(
                period=f"{target_year}-{target_month:02d}",
                total_sales=total_sales,
                total_revenue=total_revenue,
                products_sold=products_sold
            )
        )
    
    return results

@router.get("/annual", response_model=List[schemas.SaleSummary])
def get_annual_sales(
    years: int = Query(3, description="Number of years to analyze"), 
    db: Session = Depends(get_db)
):
    """
    Get annual sales summary for the last specified number of years
    """
    results = []
    current_year = datetime.utcnow().year
    
    for i in range(years):
        target_year = current_year - i
        
        year_sales = db.query(Sale).filter(
            extract('year', Sale.sale_date) == target_year
        ).all()

        total_sales = len(year_sales)
        total_revenue = sum(sale.total_price for sale in year_sales)
        products_sold = sum(sale.quantity for sale in year_sales)
        
        results.append(
            schemas.SaleSummary(
                period=str(target_year),
                total_sales=total_sales,
                total_revenue=total_revenue,
                products_sold=products_sold
            )
        )
    
    return results

@router.get("/comparison", response_model=schemas.SalesComparison)
def compare_sales_periods(
    period1_start: datetime = Query(..., description="Start date of first period"),
    period1_end: datetime = Query(..., description="End date of first period"),
    period2_start: datetime = Query(..., description="Start date of second period"),
    period2_end: datetime = Query(..., description="End date of second period"),
    db: Session = Depends(get_db)
):
    """
    Compare sales between two time periods
    """

    period1_sales = db.query(Sale).filter(
        Sale.sale_date >= period1_start,
        Sale.sale_date <= period1_end
    ).all()
    
    period2_sales = db.query(Sale).filter(
        Sale.sale_date >= period2_start,
        Sale.sale_date <= period2_end
    ).all()
    
    period1_total_sales = len(period1_sales)
    period1_total_revenue = sum(sale.total_price for sale in period1_sales)
    period1_products_sold = sum(sale.quantity for sale in period1_sales)

    period2_total_sales = len(period2_sales)
    period2_total_revenue = sum(sale.total_price for sale in period2_sales)
    period2_products_sold = sum(sale.quantity for sale in period2_sales)
    
    change_percentage = 0
    if period1_total_revenue > 0:
        change_percentage = ((period2_total_revenue - period1_total_revenue) / period1_total_revenue) * 100
    
    return schemas.SalesComparison(
        period1=schemas.SaleSummary(
            period=f"{period1_start.strftime('%Y-%m-%d')} to {period1_end.strftime('%Y-%m-%d')}",
            total_sales=period1_total_sales,
            total_revenue=period1_total_revenue,
            products_sold=period1_products_sold
        ),
        period2=schemas.SaleSummary(
            period=f"{period2_start.strftime('%Y-%m-%d')} to {period2_end.strftime('%Y-%m-%d')}",
            total_sales=period2_total_sales,
            total_revenue=period2_total_revenue,
            products_sold=period2_products_sold
        ),
        change_percentage=change_percentage
    )

@router.get("/filter", response_model=List[schemas.SaleDetail])
def filter_sales(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    platform: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Filter sales by date range, product, category, or platform
    """
    query = db.query(Sale)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    
    if category_id:
        query = query.join(Product).filter(Product.category_id == category_id)
    
    if platform:
        query = query.filter(Sale.platform == platform)
    
    sales = query.offset(skip).limit(limit).all()
    return sales