import pandas as pd
import numpy as np
import json
import os

CITIES_FILE = os.path.join(os.path.dirname(__file__), 'cities.json')

DEFAULT_CITIES = {
    'Сочи':        {'beach': True,  'child_ok': True,  'car_needed': False, 'comfort': 0.7, 'transport': 'plane', 'base_price': 0},
    'Анталья':     {'beach': True,  'child_ok': True,  'car_needed': False, 'comfort': 0.8, 'transport': 'plane', 'base_price': 0},
    'Пхукет':      {'beach': True,  'child_ok': True,  'car_needed': False, 'comfort': 0.8, 'transport': 'plane', 'base_price': 0},
    'Дубай':       {'beach': True,  'child_ok': True,  'car_needed': False, 'comfort': 1.0, 'transport': 'plane', 'base_price': 0},
    'Владивосток': {'beach': True,  'child_ok': True,  'car_needed': False, 'comfort': 0.5, 'transport': 'plane', 'base_price': 0},
    'Барнаул':     {'beach': False, 'child_ok': False, 'car_needed': True,  'comfort': 0.4, 'transport': 'plane', 'base_price': 0},
    'Махачкала':   {'beach': False, 'child_ok': False, 'car_needed': True,  'comfort': 0.4, 'transport': 'plane', 'base_price': 0},
    'Москва':      {'beach': False, 'child_ok': True,  'car_needed': False, 'comfort': 0.7, 'transport': 'plane', 'base_price': 0},
    'Анапа':       {'beach': True,  'child_ok': True,  'car_needed': False, 'comfort': 0.5, 'transport': 'train', 'base_price': 6500},
    'Выборг':      {'beach': False, 'child_ok': True,  'car_needed': False, 'comfort': 0.5, 'transport': 'train', 'base_price': 1000}
}

def load_cities():
    if not os.path.exists(CITIES_FILE):
        save_cities(DEFAULT_CITIES)
        return DEFAULT_CITIES
    with open(CITIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cities(cities):
    with open(CITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cities, f, ensure_ascii=False, indent=4)

def generate_synthetic_data(filename='flight_prices.csv'):
    if os.path.exists(filename):
        return

    config = {
        'Сочи':        {'base': 6000,  'summer_mult': 2.0, 'ny_peak': 3.0, 'jan_feb_mult': 1.6},
        'Анталья':     {'base': 11000, 'summer_mult': 1.8, 'ny_peak': 2.7, 'jan_feb_mult': 1.0},
        'Пхукет':      {'base': 30000, 'summer_mult': 0.7, 'ny_peak': 1.6, 'jan_feb_mult': 1.15},
        'Дубай':       {'base': 15000, 'summer_mult': 0.8, 'ny_peak': 2.6, 'jan_feb_mult': 1.2},
        'Владивосток': {'base': 26000, 'summer_mult': 1.0, 'ny_peak': 1.15,'jan_feb_mult': 1.0},
        'Москва':      {'base': 3500,  'summer_mult': 1.1, 'ny_peak': 1.4, 'jan_feb_mult': 0.9},
        'Барнаул':     {'base': 10000, 'summer_mult': 1.0, 'ny_peak': 2.0, 'jan_feb_mult': 1.0},
        'Махачкала':   {'base': 5000,  'summer_mult': 1.2, 'ny_peak': 3.0, 'jan_feb_mult': 1.0}
    }

    dates = pd.date_range(start='2026-01-01', end='2026-12-31')
    data = []
    np.random.seed(42)

    for date in dates:
        month = date.month
        day = date.day
        day_of_week = date.dayofweek
        weekend_mult = 1.15 if day_of_week >= 4 else 1.0
        
        for dest, c in config.items():
            price = c['base']
            if month in [11, 12]:
                price *= 1.0
            if (month == 12 and day >= 17) or (month == 1 and day <= 10):
                price *= c['ny_peak']
            elif month in [1, 2]:
                price *= c['jan_feb_mult']
            elif month in [6, 7, 8]:
                price *= c['summer_mult']
                
            urgency = np.random.choice([0.9, 1.0, 1.2], p=[0.2, 0.6, 0.2])
            noise = np.random.normal(1, 0.05)
            
            data.append({
                'date': date,
                'destination': dest,
                'month': month,
                'day_of_week': day_of_week,
                'is_weekend': 1 if day_of_week >= 5 else 0,
                'price': int(price * weekend_mult * urgency * noise)
            })

    pd.DataFrame(data).to_csv(filename, index=False)