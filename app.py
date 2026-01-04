"""
Flask backend for Retail Insights Assistant.
Provides chat interface and data summary endpoints.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from pathlib import Path
from data_cleaning import load_data, clean_data, generate_summary_statistics
from gemini_service import get_gemini_service
from prompts import PromptEngine

app = Flask(__name__)

# Global variables for data
df_clean = None
data_summary = None
gemini_service = None


def initialize_data():
    """Load and clean data on startup."""
    global df_clean, data_summary, gemini_service
    
    try:
        # Get paths
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        data_file = project_root / 'data' / 'May-2022.csv'
        
        # Load and clean data
        print("Loading data...")
        df = load_data(str(data_file))
        df_clean = clean_data(df)
        
        # Generate summary
        print("Generating summary statistics...")
        data_summary = generate_summary_statistics(df_clean)
        
        # Initialize Gemini service
        print("Initializing Gemini service...")
        gemini_service = get_gemini_service()
        
        print("Initialization complete!")
        
    except Exception as e:
        print(f"Error initializing data: {e}")
        raise


def get_relevant_products(question: str, limit: int = 5) -> list:
    """
    Extract relevant products based on question keywords.
    Simple keyword matching for now - could be enhanced with semantic search.
    """
    if df_clean is None:
        return []
    
    question_lower = question.lower()
    relevant = []
    
    # Check for category mentions
    if 'kurta' in question_lower:
        relevant_df = df_clean[df_clean['Category'].str.lower() == 'kurta']
    elif 'catalog' in question_lower or 'moments' in question_lower:
        if 'moments' in question_lower:
            relevant_df = df_clean[df_clean['Catalog'].str.lower() == 'moments']
        else:
            relevant_df = df_clean
    else:
        relevant_df = df_clean
    
    # Check for style ID mentions
    style_keywords = [word for word in question.split() if '_' in word and word[0].isupper()]
    if style_keywords:
        for style in style_keywords:
            style_matches = relevant_df[relevant_df['Style Id'].str.contains(style, case=False, na=False)]
            if len(style_matches) > 0:
                relevant_df = style_matches
                break
    
    # Get top products by price variation (more interesting for comparison)
    if len(relevant_df) > 0:
        top_products = relevant_df.nlargest(limit, 'price_range') if 'price_range' in relevant_df.columns else relevant_df.head(limit)
        
        for _, row in top_products.iterrows():
            product_dict = {
                'sku': row.get('Sku', 'N/A'),
                'style_id': row.get('Style Id', 'N/A'),
                'catalog': row.get('Catalog', 'N/A'),
                'category': row.get('Category', 'N/A'),
                'size': row.get('Size', 'N/A'),
                'min_price': float(row.get('min_price', 0)),
                'max_price': float(row.get('max_price', 0)),
                'cheapest_platform': row.get('cheapest_platform', 'N/A')
            }
            relevant.append(product_dict)
    
    return relevant


@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat questions from the frontend."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if gemini_service is None or df_clean is None:
            return jsonify({'error': 'Service not initialized'}), 500
        
        # Get relevant products for context
        relevant_products = get_relevant_products(question)
        
        # Build context data string
        context_data = f"""
        Dataset Overview:
        - Total Products: {data_summary.get('total_products', 'N/A')}
        - Categories: {', '.join(list(data_summary.get('categories', {}).keys())[:5])}
        - Price Range: ₹{data_summary.get('price_statistics', {}).get('min_price_overall', 'N/A')} - ₹{data_summary.get('price_statistics', {}).get('max_price_overall', 'N/A')}
        """
        
        # Build prompt
        prompt = PromptEngine.build_question_prompt(
            user_question=question,
            context_data=context_data,
            relevant_products=relevant_products
        )
        
        # Generate response
        response = gemini_service.generate_content(prompt)
        
        return jsonify({
            'answer': response,
            'relevant_products_count': len(relevant_products)
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary', methods=['GET'])
def summary():
    """Get AI-generated summary of the dataset."""
    try:
        if gemini_service is None or data_summary is None:
            return jsonify({'error': 'Service not initialized'}), 500
        
        # Build summary prompt
        prompt = PromptEngine.build_summary_prompt(data_summary)
        
        # Generate summary
        summary_text = gemini_service.generate_content(prompt)
        
        return jsonify({
            'summary': summary_text,
            'statistics': data_summary
        })
    
    except Exception as e:
        print(f"Error in summary endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get raw statistics (no AI processing)."""
    try:
        if data_summary is None:
            return jsonify({'error': 'Data not loaded'}), 500
        
        return jsonify(data_summary)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Initializing Retail Insights Assistant...")
    initialize_data()
    print("\nStarting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

