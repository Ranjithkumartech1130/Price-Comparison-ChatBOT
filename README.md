# 🤖 Price Comparison Chatbot

![Banner](assets/banner.png)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://aistudio.google.com/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4B8BBE?style=for-the-badge&logo=python&logoColor=white)](https://www.crummy.com/software/BeautifulSoup/)

An advanced AI-powered shopping assistant that helps you find the best deals across the globe. Seamlessly chat with AI and compare product prices in real-time.

---

## ✨ Key Features

- **🧠 Multi-Model AI Chat**: Powered by Google Gemini with a smart fallback mechanism (automatically cycles through Flash and Pro models to avoid quota limits).
- **🌍 Global Price Comparison**: Search for products and get instant price data for **USA** and **India**.
- **🔍 Smart Web Scraping**: Live scraping from eBay for real-time accuracy, with intelligent mock data fallbacks for competitors.
- **⚡ Fast & Responsive**: Built with FastAPI for a high-performance backend and a sleek, modern Vanilla JS frontend.
- **🎨 Premium UI/UX**: Features a glassmorphic design, smooth animations, and a user-friendly sidebar for configuration.

---

## 🛠️ How It Works

### 1. Price Comparison Engine
The engine uses `BeautifulSoup` to scrape live listings from eBay. It then intelligently simulates competitor prices (Amazon, Best Buy, Walmart for US; Flipkart, Amazon India, Croma for IN) to provide a comparative landscape.
- **Location Awareness**: Detects and converts prices based on the selected region (USD for US, INR for India).
- **Fallback Logic**: If scraping fails, the system generates hyper-realistic simulated data based on market trends to ensure a smooth user experience.

### 2. AI Interaction
The chatbot acts as a shopping consultant. Users can ask for recommendations, product specs, or general advice.
- **Resilience**: If the Google Gemini API hits a rate limit, the backend automatically tries alternative model versions (`gemini-2.0-flash`, `gemini-1.5-flash`, etc.) to get a response.

---

## 🚀 Getting Started

Follow these steps to get your local development environment up and running.

### 📋 Prerequisites

- **Python 3.9+** (Ensure Python is added to your PATH)
- **Git** (To clone the repository)
- **Google Gemini API Key**: [Get your free key here](https://aistudio.google.com/app/apikey)

### ⚙️ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Ranjithkumartech1130/Price-Comparison-ChatBOT.git
   cd Price-Comparison-ChatBOT
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   *(Note: You can also enter the API key directly in the web UI sidebar.)*

---

## 🏃 Running the Application

### 1. Start the Backend Server
Run the FastAPI server using Uvicorn. The server will automatically serve the frontend files.
```bash
python -m uvicorn backend.main:app --reload
```
- **Local URL**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Running Tests (Optional)
To verify the scraper functionality independently:
```bash
python test_scrape.py
```

To run the full suite of automated tests:
```bash
pytest
```

---

## 📁 Project Structure

```text
├── backend/            # FastAPI backend logic
│   ├── ai_agent.py     # Gemini AI integration and fallback logic
│   ├── main.py         # API endpoints and server config
│   └── scraper.py      # BeautifulSoup scraping and price logic
├── frontend/           # Web interface
│   ├── index.html      # Main UI structure
│   ├── script.js       # App logic and API calls
│   └── style.css       # Premium styling and animations
├── assets/             # Images and design assets
├── requirements.txt    # Project dependencies
└── README.md           # You are here!
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ for Smart Shoppers</p>
