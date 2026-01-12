# Price Comparison Chatbot

A generic AI chatbot with a dedicated Price Comparison module that scrapes data from the web.

## About
This project aims to provide a seamless experience for users to chat with an AI assistant and simultaneously compare product prices across different regions (US/India) with real and simulated data.

## Features
- **General AI Chat**: Chat with a Google Gemini-powered assistant.
- **Price Comparison**: Search for products and compare prices from multiple sources (eBay and simulated competitors).
- **Web Scraping**: Uses Python `BeautifulSoup` to scrape live data (with fallback mock data for reliability).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server**:
    ```bash
    python -m uvicorn backend.main:app --reload
    ```

3.  **Access the App**:
    Open [http://localhost:8000](http://localhost:8000) in your browser.

4.  **API Key**:
    Enter your Google Gemini API Key in the sidebar settings to enable AI features.

## Usage
- **General Chat**: Ask general questions.
- **Price Comparison**: Switch tab, type a product name (e.g. "iPhone 15"), and view comparative prices.

## Project Structure
- `backend/`: Python FastAPI backend, scraper, and AI agent.
- `frontend/`: HTML, CSS, JS for the user interface.

## Troubleshooting

- **Server fails to start**: Ensure you have installed all requirements using `pip install -r requirements.txt`.
- **API Key Errors**: Make sure you have set the `GEMINI_API_KEY` environment variable or entered it in the UI.
