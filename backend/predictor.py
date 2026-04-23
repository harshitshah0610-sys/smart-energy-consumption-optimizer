"""
Smart Energy Consumption Optimizer — Prediction Module
Loads the trained ML model and makes energy consumption predictions.
"""

import joblib
import numpy as np
import os


# --- Appliance power ratings (Watts) — Indian standard ---
APPLIANCE_WATTAGE = {
    'fan': 75,
    'ceiling_fan': 75,
    'ac': 1500,
    'air_conditioner': 1500,
    'refrigerator': 150,
    'fridge': 150,
    'led_light': 10,
    'light': 10,
    'tube_light': 40,
    'television': 100,
    'tv': 100,
    'washing_machine': 500,
    'microwave': 1200,
    'water_heater': 2000,
    'geyser': 2000,
    'computer': 200,
    'laptop': 65,
    'iron': 1000,
    'mixer_grinder': 750,
    'water_pump': 750,
    'router': 15,
    'phone_charger': 10,
    'exhaust_fan': 40,
    'cooler': 200,
    'heater': 2000,
    'induction_cooktop': 1800,
}


class EnergyPredictor:
    """Handles loading the trained model and making predictions."""
    
    def __init__(self):
        """Load the trained model on initialization."""
        model_path = os.path.join(
            os.path.dirname(__file__), '..', 'model', 'energy_model.pkl'
        )
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run train_model.py first."
            )
        
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_cols = model_data['feature_cols']
        self.metrics = model_data['metrics']
        self.feature_importance = model_data['feature_importance']
        
        print("[OK] ML model loaded successfully")
    
    def predict(self, rooms, occupants, appliances, temperature=30):
        """
        Predict daily energy consumption.
        
        Args:
            rooms (int): Number of rooms
            occupants (int): Number of occupants
            appliances (list): List of dicts with 'name', 'quantity', 'hours'
            temperature (float): Average temperature in °C
            
        Returns:
            dict: Prediction results with detailed breakdown
        """
        # --- Calculate derived features ---
        num_appliances = sum(a.get('quantity', 1) for a in appliances)
        total_usage_hours = sum(
            a.get('hours', 0) * a.get('quantity', 1) for a in appliances
        )
        
        # Check for AC and heavy appliances
        has_ac = int(any(
            a['name'].lower() in ['ac', 'air_conditioner'] 
            for a in appliances
        ))
        heavy_list = ['washing_machine', 'geyser', 'water_heater', 'iron', 
                      'microwave', 'induction_cooktop']
        has_heavy = int(any(
            a['name'].lower() in heavy_list for a in appliances
        ))
        
        # --- Build feature vector ---
        features = np.array([[
            rooms, occupants, num_appliances,
            total_usage_hours, temperature,
            has_ac, has_heavy
        ]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # --- ML Prediction ---
        ml_prediction = float(self.model.predict(features_scaled)[0])
        
        # --- Physics-based calculation (for breakdown) ---
        appliance_breakdown = []
        physics_total = 0
        
        for app in appliances:
            name = app['name'].lower().replace(' ', '_')
            quantity = app.get('quantity', 1)
            hours = app.get('hours', 0)
            
            # Get wattage (default 100W for unknown appliances)
            wattage = APPLIANCE_WATTAGE.get(name, 100)
            
            # Daily energy in kWh
            daily_kwh = (wattage * hours * quantity) / 1000
            
            appliance_breakdown.append({
                'name': app['name'],
                'quantity': quantity,
                'hours': hours,
                'wattage': wattage,
                'daily_kwh': round(daily_kwh, 2)
            })
            physics_total += daily_kwh
        
        # Use a weighted blend: 60% ML + 40% physics for robustness
        blended_prediction = round(0.6 * ml_prediction + 0.4 * physics_total, 2)
        
        # Ensure prediction is reasonable
        blended_prediction = max(0.5, blended_prediction)
        
        # Monthly projection
        monthly_kwh = round(blended_prediction * 30, 2)
        
        # Cost calculation (Indian electricity tariff slabs)
        monthly_cost = self._calculate_cost(monthly_kwh)
        
        return {
            'daily_kwh': blended_prediction,
            'monthly_kwh': monthly_kwh,
            'monthly_cost': monthly_cost,
            'appliance_breakdown': sorted(
                appliance_breakdown, key=lambda x: x['daily_kwh'], reverse=True
            ),
            'ml_prediction': round(ml_prediction, 2),
            'physics_prediction': round(physics_total, 2),
            'model_accuracy': self.metrics.get('r2', 0),
            'temperature_impact': round((temperature - 25) * 0.15, 2)
        }
    
    def _calculate_cost(self, monthly_kwh):
        """
        Calculate monthly electricity cost using Indian tariff slabs.
        
        Slab rates (approximate, varies by state):
            0-100 kWh:   ₹3.00/kWh
            101-200 kWh:  ₹4.50/kWh
            201-300 kWh:  ₹6.00/kWh
            301-500 kWh:  ₹7.00/kWh
            500+ kWh:     ₹8.00/kWh
        """
        slabs = [
            (100, 3.00),
            (100, 4.50),
            (100, 6.00),
            (200, 7.00),
            (float('inf'), 8.00)
        ]
        
        cost = 0
        remaining = monthly_kwh
        
        for slab_limit, rate in slabs:
            if remaining <= 0:
                break
            units = min(remaining, slab_limit)
            cost += units * rate
            remaining -= units
        
        # Add fixed charges
        cost += 50  # Meter charge
        
        return round(cost, 2)
    
    def get_appliance_list(self):
        """Return the list of supported appliances with wattages."""
        return {
            name: wattage 
            for name, wattage in sorted(APPLIANCE_WATTAGE.items())
        }


if __name__ == '__main__':
    # Quick test
    predictor = EnergyPredictor()
    result = predictor.predict(
        rooms=3,
        occupants=4,
        appliances=[
            {'name': 'fan', 'quantity': 3, 'hours': 8},
            {'name': 'led_light', 'quantity': 6, 'hours': 6},
            {'name': 'refrigerator', 'quantity': 1, 'hours': 24},
            {'name': 'tv', 'quantity': 1, 'hours': 4},
            {'name': 'ac', 'quantity': 1, 'hours': 6},
        ],
        temperature=35
    )
    print(f"\nPrediction: {result['daily_kwh']} kWh/day")
    print(f"Monthly: {result['monthly_kwh']} kWh")
    print(f"Cost: ₹{result['monthly_cost']}")
