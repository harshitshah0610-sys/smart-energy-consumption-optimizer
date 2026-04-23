"""
Smart Energy Consumption Optimizer -- Entry Point
Run this file to set up and start the entire application.

Usage:
    python run.py

This will:
    1. Generate synthetic training data (if not already present)
    2. Train the ML model (if not already trained)
    3. Start the Flask web server
"""

import os
import sys
import io

# Fix Windows console encoding for emoji/unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)


def main():
    print("=" * 60)
    print("[*] Smart Energy Consumption Optimizer (HomeHostel)")
    print("=" * 60)
    
    # --- Step 1: Generate Dataset ---
    data_path = os.path.join(ROOT_DIR, 'data', 'energy_data.csv')
    if not os.path.exists(data_path):
        print("\n[Step 1] Generating synthetic dataset...")
        from data.generate_dataset import generate_dataset
        generate_dataset(output_path=data_path)
    else:
        print("\n[Step 1] Dataset already exists (OK)")
    
    # --- Step 2: Train Model ---
    model_path = os.path.join(ROOT_DIR, 'model', 'energy_model.pkl')
    if not os.path.exists(model_path):
        print("\n[Step 2] Training ML model...")
        from model.train_model import train_model
        train_model(data_path=data_path, model_path=model_path)
    else:
        print("\n[Step 2] Model already trained (OK)")
    
    # --- Step 3: Start Flask Server ---
    print("\n[Step 3] Starting web server...")
    print("-" * 60)
    
    from backend.app import app
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"\n   Open in browser: http://localhost:{port}")
    print(f"   Mode: {'Development' if debug else 'Production'}")
    print(f"   Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
