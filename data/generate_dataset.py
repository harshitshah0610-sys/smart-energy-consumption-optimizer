"""
Smart Energy Consumption Optimizer — Synthetic Dataset Generator
Generates realistic Indian household energy consumption data for ML training.
"""

import pandas as pd
import numpy as np
import os

def generate_dataset(num_samples=2000, output_path=None):
    """
    Generate synthetic energy consumption dataset.
    
    Features:
        - rooms: Number of rooms (1-8)
        - occupants: Number of occupants (1-10) 
        - num_appliances: Total number of appliances (2-15)
        - total_usage_hours: Sum of daily usage hours across appliances
        - avg_temperature: Average temperature in °C (15-45)
        - has_ac: Whether AC is used (0/1)
        - has_heavy_appliances: Whether heavy appliances like geyser/washing machine exist (0/1)
        - energy_kwh: Target — total daily energy consumption in kWh
    """
    np.random.seed(42)
    
    # --- Generate features ---
    rooms = np.random.randint(1, 9, size=num_samples)
    
    # Occupants correlate loosely with rooms
    occupants = np.clip(
        rooms + np.random.randint(-1, 3, size=num_samples), 1, 10
    )
    
    # Number of appliances correlates with rooms and occupants
    num_appliances = np.clip(
        rooms * 2 + np.random.randint(-2, 4, size=num_samples), 2, 15
    )
    
    # Total usage hours: more appliances & occupants → more usage
    total_usage_hours = np.clip(
        num_appliances * np.random.uniform(1.5, 4.0, size=num_samples)
        + occupants * np.random.uniform(0.5, 2.0, size=num_samples),
        2, 80
    )
    
    # Temperature (Indian climate range)
    avg_temperature = np.round(
        np.random.uniform(15, 45, size=num_samples), 1
    )
    
    # AC usage — more likely when temperature is high
    has_ac = ((avg_temperature > 30) & (np.random.random(num_samples) > 0.3)).astype(int)
    
    # Heavy appliances (geyser, washing machine, etc.)
    has_heavy_appliances = (np.random.random(num_samples) > 0.4).astype(int)
    
    # --- Calculate target: daily energy consumption (kWh) ---
    # Base consumption from appliances and usage
    energy_kwh = (
        total_usage_hours * 0.15                          # Base: ~150W avg per appliance-hour
        + rooms * 0.3                                      # Lighting per room
        + occupants * 0.5                                  # Per-person misc usage
        + has_ac * np.where(
            avg_temperature > 35, 
            np.random.uniform(4, 8, num_samples),          # Heavy AC usage in extreme heat
            np.random.uniform(2, 5, num_samples)           # Moderate AC usage
        )
        + has_heavy_appliances * np.random.uniform(1, 3, num_samples)  # Geyser/washer
        + (avg_temperature - 25) * 0.1                     # Temperature impact
        + np.random.normal(0, 0.5, num_samples)            # Random noise
    )
    
    # Ensure no negative values
    energy_kwh = np.round(np.clip(energy_kwh, 0.5, 60), 2)
    
    # --- Build DataFrame ---
    df = pd.DataFrame({
        'rooms': rooms,
        'occupants': occupants,
        'num_appliances': num_appliances,
        'total_usage_hours': np.round(total_usage_hours, 1),
        'avg_temperature': avg_temperature,
        'has_ac': has_ac,
        'has_heavy_appliances': has_heavy_appliances,
        'energy_kwh': energy_kwh
    })
    
    # Save to CSV
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), 'energy_data.csv')
    
    df.to_csv(output_path, index=False)
    print(f"[OK] Dataset generated: {len(df)} samples saved to {output_path}")
    print(f"   Energy range: {df['energy_kwh'].min()} - {df['energy_kwh'].max()} kWh")
    print(f"   Mean energy: {df['energy_kwh'].mean():.2f} kWh")
    
    return df


if __name__ == '__main__':
    generate_dataset()
