#Different tools
#symbol lookup 
#stock price 
#stock price history 
#instrument news
#instrument announcement 
#instrument financial data quaterly 
#instrument annual reports filing data 
#Corporate actions
#Board Meetings
#Security Status

from fastmcp import FastMCP
import requests

# Create the MCP server
mcp = FastMCP("NSE Stock MCP")

@mcp.tool
def stock_price(symbol: str) -> dict:
    """
    Fetch live stock quote data from NSE India for a given symbol.
    Example: symbol="INFY"
    """
    url = "https://www.nseindia.com/api/quote-equity"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}",
    }
    params = {"symbol": symbol}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        return {"raw": data}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Run as HTTP MCP server
    mcp.http_app()
