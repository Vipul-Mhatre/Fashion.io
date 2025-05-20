from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-flash-2.0')

# Fashion API endpoint (using Fake Store API as example, replace with your chosen fashion API)
FASHION_API_URL = "https://fakestoreapi.com/products/category/clothing"
FASHION_API_KEY = os.getenv('FASHION_API_KEY')

@app.route('/api/search', methods=['POST'])
def search_products():
    data = request.json
    query = data.get('query', '')
    
    try:
        # Fetch products from external API
        response = requests.get(FASHION_API_URL, headers={
            'Authorization': f'Bearer {FASHION_API_KEY}' if FASHION_API_KEY else None
        })
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch products from API'}), 500
            
        products = response.json()
        
        # Use Gemini for semantic search
        prompt = f"""
        I have a list of fashion products and a user query. Please analyze the query: "{query}" 
        and find the most relevant products from this list:
        
        {products}
        
        Return only the IDs of the relevant products, ranked by relevance to the query.
        Format your response as a JSON array with only the product IDs.
        """
        
        result = model.generate_content(prompt)
        relevant_product_ids = eval(result.text)  # Convert the response to a Python list
        
        # Filter and return relevant products
        relevant_products = [product for product in products if product['id'] in relevant_product_ids]
        
        # Transform product data to match frontend expectations
        transformed_products = []
        for product in relevant_products:
            transformed_products.append({
                'id': product['id'],
                'name': product['title'],
                'price': float(product['price']),
                'image': product['image'],
                'description': product['description']
            })
        
        return jsonify({'products': transformed_products})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        response = requests.get(f"https://fakestoreapi.com/products/{product_id}")
        if response.status_code != 200:
            return jsonify({'error': 'Product not found'}), 404
            
        product = response.json()
        transformed_product = {
            'id': product['id'],
            'name': product['title'],
            'price': float(product['price']),
            'image': product['image'],
            'description': product['description'],
            'category': product['category']
        }
        
        return jsonify({'product': transformed_product})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
