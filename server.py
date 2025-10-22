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
import httpx

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
        with httpx.Client(headers=headers, timeout=15.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            # Optional: extract key info
            info = data.get("info", {})
            price_info = data.get("priceInfo", {})
            return {
                "symbol": info.get("symbol"),
                "companyName": info.get("companyName"),
                "lastPrice": price_info.get("lastPrice"),
                "change": price_info.get("change"),
                "pChange": price_info.get("pChange"),
                "dayHigh": price_info.get("intraDayHighLow", {}).get("max"),
                "dayLow": price_info.get("intraDayHighLow", {}).get("min"),
                "raw": data,
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Run as HTTP MCP server
    mcp.run(transport="http", port=8000)
