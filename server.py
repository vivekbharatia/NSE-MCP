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
baseUrl = "https://www.nseindia.com"
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
    Fetch live stock quote data from NSE India for a given symbol. It will also provide price information and trade information.
    Example: symbol="INFY"
    Some of the fields returned are:
    "symbol": "INFY", //symbol ticker
    "companyName": "Infosys Limited", //company name 
    "lastPrice": 1542.1, // last traded price
    "change": 69.69999999999982, // change in price
    "percentage_Change": 4.733767997826665, //% change in price
    "volume_Weighted_Average_Price": 1529.56,
    "fifty_two_weekHighLow": {
        "min": 1307, // 52 week low price
        "minDate": "07-Apr-2025", // date of 52 week low price
        "max": 2006.45, // 52 week high price
        "maxDate": "13-Dec-2024", // date of 52 week high price
        "value": 1542.1
    },
    "metadata": {
            "series": "EQ",
            "symbol": "INFY",
            "isin": "INE009A01021",
            "status": "Listed",
            "listingDate": "08-Feb-1995",
            "industry": "Computers - Software & Consulting",
            "lastUpdateTime": "23-Oct-2025 13:10:07",
            "pdSectorPe": 22.23, // sector PE ratio
            "pdSymbolPe": 22.23, // symbol PE ratio
            "pdSectorInd": "NIFTY 50",
    },
    "securityInfo": {
            "faceValue": 5, //face value of the stock
            "issuedSize": 4154401349 // number of shares issued
        },
        "tradeInfo": {
                "totalTradedVolume": 141.01, //traded volume in lakhs
                "totalTradedValue": 2156.88, // traded value in crores
                "totalMarketCap": 640525.6, // market cap in crores
                "ffmc": 554022.7889547531, // free float market cap in crores
                "impactCost": 0.02, // in percentage
                "cmDailyVolatility": "1.53", 
                "cmAnnualVolatility": "29.23",
                "marketLot": "",
                "activeSeries": "EQ"
            },
    """
    try:
            data = nsefetch(f"{baseUrl}/api/quote-equity?symbol={symbol.upper()}")
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

@mcp.tool 
def stock_historical_price(symbol: str, start_date: str, end_date: str) -> dict:
    """
    Fetch historical stock price data from NSE India for a given symbol between start_date and end_date. This includes open, high, low, close prices and volume for each trading day in the specified date range.
    Example: symbol="INFY", start_date="01-01-2023", end_date="31-12-2023"
    Returns a dictionary with date-wise historical price data including open, high, low, close, and volume.
    """
    try:
        payload = f"{baseUrl}/api/historicalOR/cm/equity?symbol={symbol.upper()}&series=[%22EQ%22]&from={start_date}&to={end_date}"
        data = nsefetch(payload)
        historical_data = data.get("data", [])
        return {"symbol": symbol.upper(), "historical_data": historical_data}
    except Exception as e:
        return {"error": str(e)}    
    
@mcp.tool
def stock_announcement(symbol: str) -> dict:
    """
    Fetch latest stock announcements from NSE India for a given symbol.
    Example: symbol="INFY"
    Returns a list of announcements with details such as title, date, and link.
    """
    try:
        payload = f"{baseUrl}/api/corporate-announcements?symbol={symbol.upper()}"
        data = nsefetch(payload)
        announcements = data.get("data", [])
        return {"symbol": symbol.upper(), "announcements": announcements}
    except Exception as e:
        return {"error": str(e)}    
    
@mcp.tool 
def corporate_financial_statement(symbol:str, type:str, start_date: str, end_date: str) -> dict:
     
    """
    Fetch corporate's financial statement for that year or quater for a given symbol
    Example: symbo="INFY" type: Annual or Quarterly
    Return the list of financial details filled by an organization between that period
    """
    try:
        payload = f"{baseUrl}/api/corporates-financial-results?index=equities&symbol={symbol.upper()}&&from_date={start_date}&to_date={end_date}&period={type}"
        data = nsefetch(payload)
        return {"symbol": symbol.upper(), "financial_statement": data}
    except Exception as e:
        return {"error": str(e)}    
     
mcp.http_app()

if __name__ == "__main__":
    # Run as HTTP MCP server
   import uvicorn
