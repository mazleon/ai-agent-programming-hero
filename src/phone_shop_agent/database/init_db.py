#!/usr/bin/env python3
"""
Initialize SQLite database for phone shop with specifications, prices, and offers.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

def create_database_schema(db_path: str) -> None:
    """Create the database schema for phone shop."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create phones table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            chipset_name TEXT NOT NULL,
            ram_size TEXT NOT NULL,
            storage_size TEXT NOT NULL,
            display_size TEXT NOT NULL,
            battery_capacity TEXT NOT NULL,
            operating_system TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create camera_features table (normalized)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camera_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_id INTEGER NOT NULL,
            feature TEXT NOT NULL,
            FOREIGN KEY (phone_id) REFERENCES phones (id) ON DELETE CASCADE
        )
    ''')
    
    # Create charging_features table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS charging_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_id INTEGER NOT NULL,
            feature TEXT NOT NULL,
            FOREIGN KEY (phone_id) REFERENCES phones (id) ON DELETE CASCADE
        )
    ''')
    
    # Create offers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            discount_percentage REAL,
            discount_amount REAL,
            original_price REAL,
            offer_price REAL,
            start_date DATE,
            end_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (phone_id) REFERENCES phones (id) ON DELETE SET NULL
        )
    ''')
    
    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_id INTEGER NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            reserved_quantity INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (phone_id) REFERENCES phones (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phones_model ON phones(model_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phones_price ON phones(price)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_offers_active ON offers(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_offers_dates ON offers(start_date, end_date)')
    
    conn.commit()
    conn.close()
    print("✅ Database schema created successfully")

def populate_phone_data(db_path: str, json_file_path: str) -> None:
    """Populate the database with phone data from JSON file."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Load JSON data
    with open(json_file_path, 'r') as f:
        phones_data = json.load(f)
    
    for phone_data in phones_data:
        try:
            # Insert phone basic info
            cursor.execute('''
                INSERT OR REPLACE INTO phones 
                (model_name, year, chipset_name, ram_size, storage_size, 
                 display_size, battery_capacity, operating_system, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                phone_data['model_name'],
                phone_data['year'],
                phone_data['chipset_name'],
                phone_data['ram_size'],
                phone_data['storage_size'],
                phone_data['display_size'],
                phone_data['battery_capacity'],
                phone_data['operating_system'],
                phone_data['price']
            ))
            
            phone_id = cursor.lastrowid
            
            # Clear existing features for this phone
            cursor.execute('DELETE FROM camera_features WHERE phone_id = ?', (phone_id,))
            cursor.execute('DELETE FROM charging_features WHERE phone_id = ?', (phone_id,))
            
            # Insert camera features
            for feature in phone_data['camera_features']:
                cursor.execute('''
                    INSERT INTO camera_features (phone_id, feature)
                    VALUES (?, ?)
                ''', (phone_id, feature))
            
            # Insert charging features (split by comma if multiple)
            charging_features = phone_data['charging_features'].split(', ')
            for feature in charging_features:
                cursor.execute('''
                    INSERT INTO charging_features (phone_id, feature)
                    VALUES (?, ?)
                ''', (phone_id, feature.strip()))
            
            # Insert initial inventory
            cursor.execute('''
                INSERT OR REPLACE INTO inventory (phone_id, stock_quantity)
                VALUES (?, ?)
            ''', (phone_id, 50))  # Default stock
            
            print(f"✅ Inserted {phone_data['model_name']}")
            
        except Exception as e:
            print(f"❌ Error inserting {phone_data.get('model_name', 'unknown')}: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Phone data populated successfully")

def create_sample_offers(db_path: str) -> None:
    """Create sample offers for demonstration."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get phone IDs
    cursor.execute('SELECT id, model_name, price FROM phones')
    phones = cursor.fetchall()
    
    sample_offers = [
        {
            'title': 'Black Friday Special',
            'description': 'Limited time discount for Black Friday',
            'discount_percentage': 15.0,
            'start_date': datetime.now().date(),
            'end_date': (datetime.now() + timedelta(days=7)).date()
        },
        {
            'title': 'Student Discount',
            'description': 'Special pricing for students with valid ID',
            'discount_percentage': 10.0,
            'start_date': datetime.now().date(),
            'end_date': (datetime.now() + timedelta(days=30)).date()
        },
        {
            'title': 'Trade-in Bonus',
            'description': 'Extra discount when trading in your old phone',
            'discount_amount': 100.0,
            'start_date': datetime.now().date(),
            'end_date': (datetime.now() + timedelta(days=14)).date()
        }
    ]
    
    for i, phone in enumerate(phones[:3]):  # Apply offers to first 3 phones
        phone_id, model_name, original_price = phone
        offer = sample_offers[i]
        
        if 'discount_percentage' in offer:
            discount_amount = original_price * (offer['discount_percentage'] / 100)
            offer_price = original_price - discount_amount
        else:
            discount_amount = offer['discount_amount']
            offer_price = original_price - discount_amount
        
        cursor.execute('''
            INSERT INTO offers 
            (phone_id, title, description, discount_percentage, discount_amount, 
             original_price, offer_price, start_date, end_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            phone_id,
            offer['title'],
            offer['description'],
            offer.get('discount_percentage'),
            discount_amount,
            original_price,
            offer_price,
            offer['start_date'],
            offer['end_date'],
            1
        ))
        
        print(f"✅ Created offer '{offer['title']}' for {model_name}")
    
    conn.commit()
    conn.close()
    print("✅ Sample offers created successfully")

def main():
    """Initialize the complete database."""
    # Paths
    db_dir = Path(__file__).parent
    db_path = db_dir / "phone_shop.db"
    json_path = db_dir.parent / "data" / "phone_specifications.json"
    
    # Create directory if it doesn't exist
    db_dir.mkdir(exist_ok=True)
    
    print("🚀 Initializing Phone Shop Database...")
    print("=" * 50)
    
    # Create schema
    create_database_schema(str(db_path))
    
    # Populate data
    if json_path.exists():
        populate_phone_data(str(db_path), str(json_path))
    else:
        print(f"❌ JSON file not found: {json_path}")
        return
    
    # Create sample offers
    create_sample_offers(str(db_path))
    
    print("\n" + "=" * 50)
    print("🎉 Database initialization complete!")
    print(f"📍 Database location: {db_path}")
    
    # Show summary
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM phones')
    phone_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM offers WHERE is_active = 1')
    offer_count = cursor.fetchone()[0]
    
    print(f"📱 Total phones: {phone_count}")
    print(f"🎁 Active offers: {offer_count}")
    
    conn.close()

if __name__ == "__main__":
    main()
