from google.adk.tools import FunctionTool

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city."""
    print(f"--- Tool: get_weather called for city: {city} ---")
    mock_weather_db = {
        "new york": "sunny with a temperature of 25°C.",
        "london": "cloudy with a temperature of 15°C.",
    }
    report = mock_weather_db.get(city.lower(), "weather data not available for this city.")
    return {"weather_report": report}

def get_stock_price(ticker: str) -> dict:
    """Retrieves the current stock price for a given ticker symbol."""
    print(f"--- Tool: get_stock_price called for ticker: {ticker} ---")
    mock_stock_db = {
        "GOOGL": "175.50 USD",
        "MSFT": "427.80 USD",
    }
    price = mock_stock_db.get(ticker.upper(), "stock price not available for this ticker.")
    return {"stock_price": price}

# Expose tools for the agent to use
weather_tool = FunctionTool(func=get_weather)
stock_tool = FunctionTool(func=get_stock_price)