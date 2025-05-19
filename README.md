E-commerce Admin API (For Forsit Test)
This is a back-end API for an e-commerce admin dashboard built with Python and FastAPI. It provides detailed insights into sales, revenue, and inventory status, and allows for product management.

## Features

- **Sales Analytics**: Comprehensive sales analysis with daily, weekly, monthly, and annual reports
- **Inventory Management**: Track inventory levels, get low stock alerts, and view inventory history
- **Product Management**: Full CRUD operations for products with category management

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MySQL server running locally
- pip (Python package installer)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/FaizanMukhtar/Forsit-backend-test
cd Forsit-backend-test
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content to host the database locally:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=forsit_test_smfm
```

5. Initialize the database with demo data:
```bash
python scripts/seed_database.py
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

7. Access the API documentation at: http://localhost:8000/docs

## API Endpoints

### Products API

- `GET /products/`: Get all products (with pagination)
- `GET /products/{product_id}`: Get a specific product
- `POST /products/`: Create a new product
- `PUT /products/{product_id}`: Update product information
- `DELETE /products/{product_id}`: Delete a product
- `GET /products/category/{category_id}`: Get products by category

### Inventory API

- `GET /inventory/`: Get current inventory status for all products
- `GET /inventory/low-stock`: Get products with inventory below threshold
- `PUT /inventory/{product_id}`: Update inventory level
- `GET /inventory/history/{product_id}`: View inventory change history

### Sales API

- `GET /sales/`: Get all sales records (with pagination)
- `GET /sales/daily`: Get daily sales summary (default: last 7 days)
- `GET /sales/weekly`: Get weekly sales summary (default: last 4 weeks)
- `GET /sales/monthly`: Get monthly sales summary (default: last 6 months)
- `GET /sales/annual`: Get annual sales summary (default: last 3 years)
- `GET /sales/comparison`: Compare sales between two time periods
- `GET /sales/filter`: Filter sales by date range, product, category, or platform

## Database Schema

The database consists of the following tables:

### Categories
- `id`: Primary key
- `name`: Category name
- `description`: Category description

### Products
- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `category_id`: Foreign key to categories
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Inventory
- `id`: Primary key
- `product_id`: Foreign key to products
- `quantity`: Current stock quantity
- `low_stock_threshold`: Threshold for low stock alerts
- `last_updated`: Last update timestamp

### Inventory History
- `id`: Primary key
- `inventory_id`: Foreign key to inventory
- `previous_quantity`: Previous stock level
- `new_quantity`: New stock level
- `change_date`: Change timestamp

### Sales
- `id`: Primary key
- `product_id`: Foreign key to products
- `quantity`: Number of units sold
- `total_price`: Total sale amount
- `sale_date`: Sale timestamp
- `platform`: Sales platform (e.g., Amazon, Daraz, Direct Website, OLX)