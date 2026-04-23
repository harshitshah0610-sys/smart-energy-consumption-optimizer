"""
Smart Energy Consumption Optimizer — Optimization Engine
Generates optimized schedules and calculates energy savings.
"""

import random


# --- Peak/off-peak hour definitions ---
PEAK_HOURS = list(range(6, 10)) + list(range(18, 23))       # 6-10 AM, 6-11 PM
OFF_PEAK_HOURS = list(range(0, 6)) + list(range(10, 18)) + [23]  # Night + midday

# Appliances that CAN be shifted to off-peak
SHIFTABLE_APPLIANCES = {
    'washing_machine', 'iron', 'water_heater', 'geyser',
    'microwave', 'water_pump', 'induction_cooktop', 'mixer_grinder'
}

# Appliances that can have usage reduced
REDUCIBLE_APPLIANCES = {
    'ac': {'max_reduction': 0.30, 'tip': 'Set AC to 24°C and use timer mode'},
    'air_conditioner': {'max_reduction': 0.30, 'tip': 'Set AC to 24°C and use timer mode'},
    'fan': {'max_reduction': 0.15, 'tip': 'Turn off fans in unoccupied rooms'},
    'ceiling_fan': {'max_reduction': 0.15, 'tip': 'Turn off fans in unoccupied rooms'},
    'television': {'max_reduction': 0.20, 'tip': 'Reduce standby time, use sleep timer'},
    'tv': {'max_reduction': 0.20, 'tip': 'Reduce standby time, use sleep timer'},
    'light': {'max_reduction': 0.25, 'tip': 'Use natural light during daytime'},
    'led_light': {'max_reduction': 0.25, 'tip': 'Turn off lights in empty rooms'},
    'tube_light': {'max_reduction': 0.30, 'tip': 'Replace with LED lights (70% less energy)'},
    'computer': {'max_reduction': 0.20, 'tip': 'Enable power saving mode'},
    'laptop': {'max_reduction': 0.15, 'tip': 'Unplug charger when battery is full'},
    'cooler': {'max_reduction': 0.20, 'tip': 'Use in well-ventilated rooms for better efficiency'},
    'heater': {'max_reduction': 0.25, 'tip': 'Use room heater with thermostat control'},
}


def optimize_schedule(appliances, rooms, occupants, temperature=30):
    """
    Generate an optimized energy schedule with recommendations.
    
    Args:
        appliances: List of dicts with 'name', 'quantity', 'hours', 'daily_kwh'
        rooms: Number of rooms
        occupants: Number of occupants
        temperature: Average temperature
        
    Returns:
        dict: Optimization results with schedule and savings
    """
    recommendations = []
    optimized_appliances = []
    total_original_kwh = 0
    total_optimized_kwh = 0
    
    for app in appliances:
        name = app['name'].lower().replace(' ', '_')
        original_kwh = app.get('daily_kwh', 0)
        total_original_kwh += original_kwh
        
        optimized_kwh = original_kwh
        app_recommendations = []
        
        # --- Strategy 1: Shift to off-peak hours ---
        if name in SHIFTABLE_APPLIANCES:
            # Off-peak shifting saves ~10-15% due to better grid efficiency
            saving = round(original_kwh * 0.12, 3)
            optimized_kwh -= saving
            app_recommendations.append({
                'type': 'shift',
                'message': f"Shift {app['name']} usage to off-peak hours (10 AM–6 PM or after 11 PM)",
                'saving_kwh': saving,
                'priority': 'high'
            })
        
        # --- Strategy 2: Reduce usage duration ---
        if name in REDUCIBLE_APPLIANCES:
            info = REDUCIBLE_APPLIANCES[name]
            reduction = info['max_reduction']
            
            # Adjust reduction based on context
            if name in ['ac', 'air_conditioner'] and temperature > 40:
                reduction *= 0.5  # Don't reduce AC much in extreme heat
            
            saving = round(original_kwh * reduction, 3)
            optimized_kwh -= saving
            app_recommendations.append({
                'type': 'reduce',
                'message': info['tip'],
                'saving_kwh': saving,
                'priority': 'medium'
            })
        
        # --- Strategy 3: Occupancy-based optimization ---
        if name in ['fan', 'ceiling_fan', 'light', 'led_light', 'tube_light', 'ac', 'air_conditioner']:
            if app.get('quantity', 1) > occupants:
                excess = app['quantity'] - occupants
                saving = round((original_kwh / app['quantity']) * excess * 0.4, 3)
                optimized_kwh -= saving
                app_recommendations.append({
                    'type': 'occupancy',
                    'message': f"You have {app['quantity']} {app['name']}(s) for {occupants} occupants. "
                              f"Turn off {excess} unit(s) when rooms are empty.",
                    'saving_kwh': saving,
                    'priority': 'high'
                })
        
        # --- Strategy 4: Temperature-based optimization ---
        if name in ['ac', 'air_conditioner'] and temperature < 28:
            saving = round(original_kwh * 0.5, 3)
            optimized_kwh -= saving
            app_recommendations.append({
                'type': 'weather',
                'message': f"Temperature is {temperature}°C — consider using a fan instead of AC",
                'saving_kwh': saving,
                'priority': 'high'
            })
        elif name in ['heater'] and temperature > 20:
            saving = round(original_kwh * 0.4, 3)
            optimized_kwh -= saving
            app_recommendations.append({
                'type': 'weather',
                'message': f"Temperature is {temperature}°C — heater may not be needed",
                'saving_kwh': saving,
                'priority': 'medium'
            })
        
        # Ensure optimized doesn't go below 20% of original (unrealistic otherwise)
        optimized_kwh = max(optimized_kwh, original_kwh * 0.2)
        
        optimized_appliances.append({
            'name': app['name'],
            'original_kwh': round(original_kwh, 2),
            'optimized_kwh': round(optimized_kwh, 2),
            'saving_kwh': round(original_kwh - optimized_kwh, 2),
            'recommendations': app_recommendations
        })
        
        total_optimized_kwh += optimized_kwh
        recommendations.extend(app_recommendations)
    
    # --- General recommendations ---
    general_tips = _get_general_tips(rooms, occupants, temperature, appliances)
    
    # --- Calculate savings ---
    daily_saving = round(total_original_kwh - total_optimized_kwh, 2)
    monthly_saving_kwh = round(daily_saving * 30, 2)
    percentage_reduction = round(
        (daily_saving / total_original_kwh * 100) if total_original_kwh > 0 else 0, 1
    )
    
    # Cost savings
    original_monthly_cost = _calculate_cost(total_original_kwh * 30)
    optimized_monthly_cost = _calculate_cost(total_optimized_kwh * 30)
    monthly_cost_saving = round(original_monthly_cost - optimized_monthly_cost, 2)
    
    # Efficiency rating
    efficiency_rating = _calculate_efficiency_rating(percentage_reduction, len(recommendations))
    
    # Generate optimized schedule
    schedule = _generate_schedule(appliances, optimized_appliances)
    
    return {
        'original_daily_kwh': round(total_original_kwh, 2),
        'optimized_daily_kwh': round(total_optimized_kwh, 2),
        'daily_saving_kwh': daily_saving,
        'monthly_saving_kwh': monthly_saving_kwh,
        'percentage_reduction': percentage_reduction,
        'original_monthly_cost': original_monthly_cost,
        'optimized_monthly_cost': optimized_monthly_cost,
        'monthly_cost_saving': monthly_cost_saving,
        'yearly_cost_saving': round(monthly_cost_saving * 12, 2),
        'efficiency_rating': efficiency_rating,
        'optimized_appliances': optimized_appliances,
        'recommendations': sorted(
            recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']]
        ),
        'general_tips': general_tips,
        'schedule': schedule
    }


def _get_general_tips(rooms, occupants, temperature, appliances):
    """Generate contextual general energy-saving tips."""
    tips = []
    
    tips.append({
        'icon': '💡',
        'tip': 'Replace CFL/incandescent bulbs with LED lights to save up to 75% on lighting costs'
    })
    
    if temperature > 35:
        tips.append({
            'icon': '❄️',
            'tip': f'At {temperature}°C, set AC to 24°C (each degree lower adds ~6% to your bill)'
        })
    
    if any(a['name'].lower() in ['refrigerator', 'fridge'] for a in appliances):
        tips.append({
            'icon': '🧊',
            'tip': 'Keep refrigerator away from heat sources and maintain proper door sealing'
        })
    
    if rooms > 3:
        tips.append({
            'icon': '🏠',
            'tip': f'With {rooms} rooms, install occupancy sensors for automated light control'
        })
    
    tips.append({
        'icon': '🔌',
        'tip': 'Unplug devices when not in use — standby power can account for 5-10% of your bill'
    })
    
    tips.append({
        'icon': '⭐',
        'tip': 'When buying new appliances, choose BEE 5-star rated products for maximum efficiency'
    })
    
    return tips


def _calculate_efficiency_rating(percentage_reduction, num_recommendations):
    """Calculate an efficiency rating based on potential savings."""
    if percentage_reduction >= 30:
        return {'grade': 'A+', 'label': 'Excellent', 'color': '#10b981', 'score': 95}
    elif percentage_reduction >= 25:
        return {'grade': 'A', 'label': 'Very Good', 'color': '#22c55e', 'score': 85}
    elif percentage_reduction >= 20:
        return {'grade': 'B+', 'label': 'Good', 'color': '#84cc16', 'score': 75}
    elif percentage_reduction >= 15:
        return {'grade': 'B', 'label': 'Above Average', 'color': '#eab308', 'score': 65}
    elif percentage_reduction >= 10:
        return {'grade': 'C', 'label': 'Average', 'color': '#f97316', 'score': 50}
    else:
        return {'grade': 'D', 'label': 'Needs Improvement', 'color': '#ef4444', 'score': 35}


def _generate_schedule(original_appliances, optimized_appliances):
    """Generate an optimized daily schedule."""
    schedule = {
        'early_morning': {'time': '5:00 AM – 8:00 AM', 'appliances': []},
        'morning': {'time': '8:00 AM – 12:00 PM', 'appliances': []},
        'afternoon': {'time': '12:00 PM – 4:00 PM', 'appliances': []},
        'evening': {'time': '4:00 PM – 8:00 PM', 'appliances': []},
        'night': {'time': '8:00 PM – 11:00 PM', 'appliances': []},
        'late_night': {'time': '11:00 PM – 5:00 AM', 'appliances': []},
    }
    
    for app in original_appliances:
        name = app['name'].lower().replace(' ', '_')
        
        if name in ['refrigerator', 'fridge', 'router']:
            # Always-on appliances
            for slot in schedule.values():
                slot['appliances'].append({'name': app['name'], 'status': 'always_on'})
        elif name in SHIFTABLE_APPLIANCES:
            # Shift to off-peak
            schedule['morning']['appliances'].append({'name': app['name'], 'status': 'recommended'})
            schedule['late_night']['appliances'].append({'name': app['name'], 'status': 'recommended'})
        elif name in ['ac', 'air_conditioner']:
            schedule['afternoon']['appliances'].append({'name': app['name'], 'status': 'limited'})
            schedule['night']['appliances'].append({'name': app['name'], 'status': 'limited'})
        elif name in ['fan', 'ceiling_fan', 'cooler']:
            schedule['morning']['appliances'].append({'name': app['name'], 'status': 'as_needed'})
            schedule['afternoon']['appliances'].append({'name': app['name'], 'status': 'recommended'})
            schedule['evening']['appliances'].append({'name': app['name'], 'status': 'as_needed'})
        elif name in ['light', 'led_light', 'tube_light']:
            schedule['evening']['appliances'].append({'name': app['name'], 'status': 'recommended'})
            schedule['night']['appliances'].append({'name': app['name'], 'status': 'recommended'})
        else:
            schedule['morning']['appliances'].append({'name': app['name'], 'status': 'as_needed'})
    
    return schedule


def _calculate_cost(monthly_kwh):
    """Calculate monthly electricity cost using Indian tariff slabs."""
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
    
    cost += 50  # Fixed meter charge
    return round(cost, 2)


def simulate_scenario(base_appliances, scenario_type='weekend'):
    """
    Simulate different usage scenarios for comparison.
    
    Args:
        base_appliances: Base appliance list
        scenario_type: 'weekend', 'summer', 'winter', 'work_from_home'
    
    Returns:
        list: Modified appliance list for the scenario
    """
    import copy
    modified = copy.deepcopy(base_appliances)
    
    multipliers = {
        'weekend': {
            'tv': 1.5, 'television': 1.5,
            'ac': 1.3, 'air_conditioner': 1.3,
            'computer': 1.4, 'laptop': 1.4,
            'washing_machine': 1.5, 'microwave': 1.3,
        },
        'summer': {
            'ac': 2.0, 'air_conditioner': 2.0,
            'fan': 1.5, 'ceiling_fan': 1.5,
            'cooler': 1.8, 'refrigerator': 1.2, 'fridge': 1.2,
        },
        'winter': {
            'heater': 2.0, 'geyser': 1.8, 'water_heater': 1.8,
            'ac': 0.0, 'air_conditioner': 0.0,
            'fan': 0.3, 'ceiling_fan': 0.3, 'cooler': 0.0,
        },
        'work_from_home': {
            'computer': 2.0, 'laptop': 2.0,
            'light': 1.3, 'led_light': 1.3,
            'fan': 1.3, 'ceiling_fan': 1.3,
            'ac': 1.4, 'air_conditioner': 1.4,
            'router': 1.0,
        }
    }
    
    mults = multipliers.get(scenario_type, {})
    
    for app in modified:
        name = app['name'].lower().replace(' ', '_')
        if name in mults:
            app['hours'] = round(app['hours'] * mults[name], 1)
            app['hours'] = min(app['hours'], 24)  # Cap at 24 hours
    
    return modified
