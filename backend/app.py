"""
Smart Energy Consumption Optimizer — Flask Backend
Serves the API endpoints and frontend static files.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.predictor import EnergyPredictor
from backend.optimizer import optimize_schedule, simulate_scenario

# --- Initialize Flask app ---
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_url_path=''
)
CORS(app)

# --- Load ML model ---
predictor = None

def get_predictor():
    """Lazy-load the predictor to avoid startup errors."""
    global predictor
    if predictor is None:
        predictor = EnergyPredictor()
    return predictor


# ============================================================
# API ROUTES
# ============================================================

@app.route('/api/predict', methods=['POST'])
def predict_energy():
    """
    Predict energy consumption based on user inputs.
    
    Expected JSON body:
    {
        "rooms": 3,
        "occupants": 4,
        "temperature": 35,
        "appliances": [
            {"name": "fan", "quantity": 3, "hours": 8},
            {"name": "ac", "quantity": 1, "hours": 6}
        ]
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        rooms = data.get('rooms', 2)
        occupants = data.get('occupants', 3)
        temperature = data.get('temperature', 30)
        appliances = data.get('appliances', [])
        
        if not appliances:
            return jsonify({'error': 'At least one appliance is required'}), 400
        
        # Get prediction
        pred = get_predictor()
        result = pred.predict(rooms, occupants, appliances, temperature)
        
        return jsonify({
            'success': True,
            'prediction': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimize', methods=['POST'])
def optimize_energy():
    """
    Generate optimized schedule and savings.
    
    Expected JSON body (same as /api/predict plus prediction results):
    {
        "rooms": 3,
        "occupants": 4,
        "temperature": 35,
        "appliances": [
            {"name": "fan", "quantity": 3, "hours": 8, "daily_kwh": 1.8}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        rooms = data.get('rooms', 2)
        occupants = data.get('occupants', 3)
        temperature = data.get('temperature', 30)
        appliances = data.get('appliances', [])
        
        if not appliances:
            return jsonify({'error': 'At least one appliance is required'}), 400
        
        # Run optimization
        result = optimize_schedule(appliances, rooms, occupants, temperature)
        
        return jsonify({
            'success': True,
            'optimization': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    Simulate different usage scenarios.
    
    Expected JSON body:
    {
        "appliances": [...],
        "scenario": "summer"  // Options: weekend, summer, winter, work_from_home
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        appliances = data.get('appliances', [])
        scenarios = ['weekend', 'summer', 'winter', 'work_from_home']
        
        pred = get_predictor()
        rooms = data.get('rooms', 2)
        occupants = data.get('occupants', 3)
        temperature = data.get('temperature', 30)
        
        results = {}
        
        # Get base prediction
        base_result = pred.predict(rooms, occupants, appliances, temperature)
        results['current'] = {
            'daily_kwh': base_result['daily_kwh'],
            'monthly_kwh': base_result['monthly_kwh'],
            'monthly_cost': base_result['monthly_cost']
        }
        
        # Run each scenario
        scenario_temps = {
            'weekend': temperature,
            'summer': max(temperature, 40),
            'winter': min(temperature, 18),
            'work_from_home': temperature
        }
        
        for scenario in scenarios:
            modified_appliances = simulate_scenario(appliances, scenario)
            sim_temp = scenario_temps[scenario]
            sim_result = pred.predict(rooms, occupants, modified_appliances, sim_temp)
            results[scenario] = {
                'daily_kwh': sim_result['daily_kwh'],
                'monthly_kwh': sim_result['monthly_kwh'],
                'monthly_cost': sim_result['monthly_cost'],
                'appliances': modified_appliances
            }
        
        return jsonify({
            'success': True,
            'simulation': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/appliances', methods=['GET'])
def get_appliances():
    """Return the list of supported appliances with wattages."""
    try:
        pred = get_predictor()
        appliance_list = pred.get_appliance_list()
        
        # Group appliances by category
        categories = {
            'Cooling': ['fan', 'ceiling_fan', 'ac', 'air_conditioner', 'cooler'],
            'Lighting': ['led_light', 'light', 'tube_light'],
            'Kitchen': ['refrigerator', 'fridge', 'microwave', 'mixer_grinder', 'induction_cooktop'],
            'Entertainment': ['television', 'tv', 'computer', 'laptop'],
            'Heating': ['water_heater', 'geyser', 'heater', 'iron'],
            'Other': ['washing_machine', 'water_pump', 'router', 'phone_charger', 'exhaust_fan']
        }
        
        return jsonify({
            'success': True,
            'appliances': appliance_list,
            'categories': categories
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Return model performance metrics."""
    try:
        pred = get_predictor()
        return jsonify({
            'success': True,
            'metrics': pred.metrics,
            'feature_importance': pred.feature_importance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# FRONTEND ROUTES (must be last — catch-all)
# ============================================================

@app.route('/')
def serve_index():
    """Serve the main frontend page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images)."""
    return send_from_directory(app.static_folder, path)


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"\n[*] Smart Energy Optimizer running at http://localhost:{port}")
    print(f"   Mode: {'Development' if debug else 'Production'}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
