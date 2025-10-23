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

headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8,en-GB;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
def nsefetch(payload):

        try:
            s = requests.Session()
            s.get("https://www.nseindia.com", headers=headers, timeout=10)
            s.get("https://www.nseindia.com/option-chain", headers=headers, timeout=10)
            output = s.get(payload, headers=headers, timeout=10).json()
        except ValueError:
            output = {}
        return output


@mcp.tool
def stock_price(symbol: str) -> dict:
    """
    Fetch live stock quote data from NSE India for a given symbol.
    Example: symbol="INFY"
    """
    
    try:
            base = "https://www.nseindia.com"
            data = nsefetch(f"{base}/api/quote-equity?symbol={symbol.upper()}")
            trade_info_data = nsefetch(f"{base}/api/quote-equity?symbol={symbol.upper()}&section=trade_info")
            price_info = data.get("priceInfo") or {}
            metadata = data.get("metadata") or {}
            info = data.get("info") or {}
            marketDeptOrderBook = trade_info_data.get("marketDeptOrderBook") or {}
            
            result = {
                "symbol": metadata.get("symbol", symbol.upper()),
                "companyName": info.get("companyName"),
                "lastPrice": price_info.get("lastPrice"),
                "change": price_info.get("change"),
                "percentage_Change": price_info.get("pChange"),
                "volume_Weighted_Average_Price": price_info.get("vwap"),
                "fifty_two_weekHighLow" : price_info.get("weekHighLow") or {},
                "Adjusted-Price-to-Earnings-Ratio": price_info.get("adjPE"),
                "tradeInfo": marketDeptOrderBook.get("tradeInfo") or {},
                "raw": data,
                "trade_raw": trade_info_data
            }
            return result
    except Exception as e:
        return {"error": str(e)}
    
mcp.http_app()

if __name__ == "__main__":
    # Run as HTTP MCP server
   import uvicorn
