import sys
import os
import random
from datetime import datetime, timedelta
import pymysql
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal, Category, Product, Inventory, InventoryHistory, Sale

Base.metadata.create_all(bind=engine)

# Sample data
categories = [
    {"name": "Electronics", "description": "Electronic devices and accessories"},
    {"name": "Clothing", "description": "Apparel and fashion items"},
    {"name": "Home & Kitchen", "description": "Items for home and kitchen use"},
]

products = [
    # Electronics
    {"name": "Smartphone X", "description": "Latest smartphone with advanced features", "price": 799.99, "category_id": 1},
    {"name": "Laptop Pro", "description": "High-performance laptop for professionals", "price": 1299.99, "category_id": 1},
    {"name": "Wireless Earbuds", "description": "Noise-cancelling wireless earbuds", "price": 129.99, "category_id": 1},
    {"name": "Smart Watch", "description": "Fitness and health tracking smartwatch", "price": 249.99, "category_id": 1},
    {"name": "Bluetooth Speaker", "description": "Portable Bluetooth speaker with deep bass", "price": 89.99, "category_id": 1},
    
    # Clothing
    {"name": "Men's T-Shirt", "description": "Comfortable cotton t-shirt", "price": 19.99, "category_id": 2},
    {"name": "Women's Jeans", "description": "Stylish and durable jeans", "price": 49.99, "category_id": 2},
    {"name": "Running Shoes", "description": "Lightweight shoes for running and athletics", "price": 79.99, "category_id": 2},
    {"name": "Winter Jacket", "description": "Warm jacket for cold weather", "price": 129.99, "category_id": 2},
    {"name": "Summer Dress", "description": "Flowy dress for summer days", "price": 39.99, "category_id": 2},
    
    # Home & Kitchen
    {"name": "Coffee Maker", "description": "Programmable coffee maker", "price": 69.99, "category_id": 3},
    {"name": "Blender", "description": "High-speed blender for smoothies", "price": 59.99, "category_id": 3},
    {"name": "Toaster", "description": "2-slice toaster with multiple settings", "price": 29.99, "category_id": 3},
    {"name": "Bedding Set", "description": "Soft cotton bedding set", "price": 79.99, "category_id": 3},
    {"name": "Cutting Board", "description": "Durable bamboo cutting board", "price": 24.99, "category_id": 3},
]

# Platforms for sales
platforms = ["Amazon", "Daraz", "Direct Website", "OLX"]

def seed_database():
    db = SessionLocal()
    try:
        existing_categories = db.query(Category).count()
        if existing_categories > 0:
            print("Database already contains data. Skipping seeding.")
            return
        
        print("Seeding database...")
        db_categories = []
        for category_data in categories:
            category = Category(**category_data)
            db.add(category)
            db_categories.append(category)
        db.commit()
        db_products = []
        for product_data in products:
            product = Product(**product_data)
            db.add(product)
            db_products.append(product)
        db.commit()
        for product in db_products:
            inventory = Inventory(
                product_id=product.id,
                quantity=random.randint(5, 100),
                low_stock_threshold=random.randint(5, 20)
            )
            db.add(inventory)
        db.commit()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        current_date = start_date
        
        while current_date <= end_date:
            num_sales = random.randint(0, 15)
            
            for _ in range(num_sales):
                product = random.choice(db_products)
                quantity = random.randint(1, 5)
                platform = random.choice(platforms)
                discount = random.uniform(0.0, 0.2)
                unit_price = product.price * (1 - discount)
                total_price = unit_price * quantity
                sale_hour = random.randint(0, 23)
                sale_minute = random.randint(0, 59)
                sale_second = random.randint(0, 59)
                sale_time = current_date.replace(hour=sale_hour, minute=sale_minute, second=sale_second)
                
                sale = Sale(
                    product_id=product.id,
                    quantity=quantity,
                    total_price=round(total_price, 2),
                    sale_date=sale_time,
                    platform=platform
                )
                db.add(sale)
            
            current_date += timedelta(days=1)
        
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # Try to create the database if it doesn't exist
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS forsit_test")
        connection.commit()
        
        print("Database created or already exists.")
        cursor.close()
        connection.close()
        
        # Populate/seed the database
        seed_database()
        
    except Exception as e:
        print(f"Database setup error: {e}")