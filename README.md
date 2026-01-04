# Retail Insights Assistant

An AI-powered web application that answers questions about retail pricing data using Google Gemini AI. Provides interactive chat interface and data insights for e-commerce platform pricing analysis.

---

## Overview

A Flask-based web application that uses Google Gemini AI to analyze and answer questions about retail pricing data across multiple e-commerce platforms (Ajio, Amazon, Flipkart, Myntra, etc.).

### Features

- **Interactive Chat Interface**: Ask questions about product pricing, platforms, and categories
- **AI-Powered Insights**: Google Gemini AI generates contextual answers based on the data
- **Data Analysis**: Automatic data cleaning, summary statistics generation
- **API Endpoints**: RESTful API for programmatic access
- **Real-time Query Processing**: Context-aware responses with relevant product information

---

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key ([Get API Key](https://aistudio.google.com/app/apikey))

### Installation

1. **Install Dependencies:**
   ```bash
   pip install Flask pandas numpy google-genai python-dotenv
   ```

2. **Set Environment Variables:**
   
   Create a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Ensure Data File Exists:**
   
   Make sure `../data/May-2022.csv` exists (relative to assignment directory).

### Run Application

```bash
cd assignment1_retail_insights
python app.py
```

The application will:
- Load and clean data from `../data/May-2022.csv`
- Generate summary statistics
- Initialize Gemini AI service
- Start Flask server on `http://0.0.0.0:5000`

Open your browser and navigate to `http://localhost:5000`

---

## API Endpoints

Base URL: `http://localhost:5000`

### 1. Chat Endpoint

**POST** `/api/chat`

Ask questions about the retail pricing data.

**Request:**
```json
{
  "question": "What is the cheapest platform for Kurta products?"
}
```

**Response:**
```json
{
  "answer": "Based on the data, Myntra offers the cheapest prices for Kurta products...",
  "relevant_products_count": 5
}
```

### 2. Summary Endpoint

**GET** `/api/summary`

Get AI-generated summary of the dataset.

**Response:**
```json
{
  "summary": "This dataset contains 1,293 products across 5 categories...",
  "statistics": {
    "total_products": 1293,
    "categories": {...},
    "price_statistics": {...}
  }
}
```

### 3. Statistics Endpoint

**GET** `/api/stats`

Get raw statistics (no AI processing).

**Response:**
```json
{
  "total_products": 1293,
  "categories": {...},
  "price_statistics": {...}
}
```

---

## Project Structure

```
assignment1_retail_insights/
├── app.py                 # Flask application and API endpoints
├── data_cleaning.py       # Data loading, cleaning, and statistics
├── gemini_service.py      # Google Gemini AI service wrapper
├── prompts.py             # Prompt engineering and template management
├── templates/
│   └── index.html         # Chat interface frontend
└── static/
    ├── style.css          # Stylesheet
    └── script.js          # Frontend JavaScript
```

---

## How It Works

1. **Data Loading**: Loads retail pricing data from CSV file
2. **Data Cleaning**: 
   - Handles missing values
   - Standardizes platform names
   - Extracts size from SKU
   - Calculates price metrics (min, max, cheapest platform)
3. **Statistics Generation**: Creates comprehensive summary statistics
4. **AI Integration**: Uses Google Gemini AI to generate contextual answers
5. **Query Processing**: 
   - Extracts relevant products based on keywords
   - Builds context-aware prompts
   - Generates intelligent responses

---

## Example Questions

You can ask questions like:

- "What is the cheapest platform for Kurta products?"
- "Compare prices across platforms for style Os206_3141"
- "What are the price ranges for different categories?"
- "Which platform offers the best prices for Moments catalog?"
- "Show me statistics about product pricing"

---

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Required - Your Google Gemini API key

### Data File

- Default location: `../data/May-2022.csv` (relative to assignment directory)
- Format: CSV with columns: Sku, Style Id, Catalog, Category, Weight, TP, platform MRPs, etc.

---

## Architecture

- **Backend**: Flask (Python)
- **AI Model**: Google Gemini 2.5 Flash
- **Data Processing**: Pandas
- **Frontend**: HTML/CSS/JavaScript
- **API**: RESTful endpoints

---

## Dependencies

- `Flask>=2.3.3` - Web framework
- `pandas>=2.1.0` - Data processing
- `numpy>=1.26.0` - Numerical operations
- `google-genai>=0.2.2` - Gemini AI client
- `python-dotenv>=1.0.0` - Environment variable management

---

## Notes

- The application loads data on startup (may take a few seconds)
- Gemini API requires internet connection
- Rate limiting is implemented to prevent API quota exhaustion
- Data cleaning removes invalid entries (rows with no platform prices, invalid TP values)

