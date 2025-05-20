<template>
  <div id="app">
    <header>
      <h1>Fashion Recommendation</h1>
    </header>
    
    <div class="search-container">
      <input 
        v-model="searchQuery" 
        @keyup.enter="searchProducts" 
        placeholder="Describe what you're looking for..."
        class="search-input"
      />
      <button @click="searchProducts" class="search-button">Search</button>
    </div>
    
    <div class="loading" v-if="loading">Searching for products...</div>
    
    <div class="products-container" v-if="products.length > 0">
      <div v-for="product in products" :key="product.id" class="product-card">
        <img :src="product.image" :alt="product.name" class="product-image">
        <div class="product-info">
          <h3>{{ product.name }}</h3>
          <p class="price">${{ product.price.toFixed(2) }}</p>
          <p class="description">{{ product.description }}</p>
          <button class="view-button">View Details</button>
        </div>
      </div>
    </div>

    <div class="no-results" v-if="!loading && searchPerformed && products.length === 0">
      No products found matching your search.
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      searchQuery: '',
      products: [],
      loading: false,
      searchPerformed: false
    };
  },
  methods: {
    async searchProducts() {
      if (!this.searchQuery.trim()) return;
      
      this.loading = true;
      this.searchPerformed = true;
      
      try {
        const response = await axios.post('http://localhost:5000/api/search', {
          query: this.searchQuery
        });
        
        this.products = response.data.products;
      } catch (error) {
        console.error('Error searching products:', error);
        this.products = [];
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 40px;
}

.search-container {
  display: flex;
  margin-bottom: 30px;
  justify-content: center;
}

.search-input {
  width: 70%;
  padding: 12px 15px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
}

.search-button {
  padding: 12px 25px;
  background-color: #4CAF50;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 0 4px 4px 0;
}

.loading {
  text-align: center;
  font-size: 18px;
  margin: 30px 0;
}

.products-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.product-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.product-image {
  width: 100%;
  height: 250px;
  object-fit: cover;
}

.product-info {
  padding: 15px;
}

.price {
  font-weight: bold;
  color: #4CAF50;
}

.view-button {
  background-color: #2c3e50;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.no-results {
  text-align: center;
  font-size: 18px;
  margin: 50px 0;
  color: #666;
}
</style>
