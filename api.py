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
from typing import Any, Dict, Optional

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

        except Exception as e:
            print(str(e)) 
            output = {}
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
        trade_info_data = nsefetch(f"{baseUrl}/api/quote-equity?symbol={symbol.upper()}&section=trade_info")
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
# -----------------------------
# Utility Helpers
# -----------------------------
def _to_number(x: Any) -> Optional[float]:
    """Safely convert NSE string values into numbers."""
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)

    if isinstance(x, str):
        s = x.strip().replace(",", "")
        if s in {"", "-", "NA", "NaN", "null"}:
            return None
        try:
            return float(s)
        except:
            return None
    return None


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """Safe division wrapper."""
    if a is None or b in (None, 0):
        return None
    return a / b    
# -----------------------------
# Transform Function
# -----------------------------
def transform_nse_financials(input_json: Dict[str, Any]) -> Dict[str, Any]:
    d = input_json.get("resultsData2", {})

    # ---- Direct numeric extraction ----
    net_sales = _to_number(d.get("re_net_sale"))
    other_income = _to_number(d.get("re_oth_inc_new"))
    total_income = _to_number(d.get("re_total_inc"))
    staff_cost = _to_number(d.get("re_staff_cost"))
    other_exp = _to_number(d.get("re_oth_exp"))
    depreciation = _to_number(d.get("re_depr_und_exp"))
    interest_exp = _to_number(d.get("re_int_new"))
    ebit = _to_number(d.get("re_pro_bef_int_n_excep"))
    pbt = _to_number(d.get("re_pro_loss_bef_tax"))
    tax = _to_number(d.get("re_tax"))
    total_exp = _to_number(d.get("re_oth_tot_exp"))

    # ---- PAT may come from multiple fields ----
    pat = (
        _to_number(d.get("re_proloss_ord_act"))
        or _to_number(d.get("dis_opr_aftr_tax_plus_ord_act"))
        or _to_number(d.get("re_con_pro_loss"))
    )

    # ---- EPS fields ----
    basic_eps = (
        _to_number(d.get("re_basic_eps_for_cont_dic_opr"))
        or _to_number(d.get("re_bsc_eps_bfr_exi"))
        or _to_number(d.get("re_basic_eps"))
    )

    diluted_eps = (
        _to_number(d.get("re_dilut_eps_for_cont_dic_opr"))
        or _to_number(d.get("re_dil_eps_bfr_exi"))
        or _to_number(d.get("re_diluted_eps"))
    )

    face_value = _to_number(d.get("re_face_val"))

    # ---- Derived fields ----
    ebitda = ebit + depreciation if (ebit is not None and depreciation is not None) else None
    ebit_margin = _safe_div(ebit, net_sales)
    ebitda_margin = _safe_div(ebitda, net_sales) if ebitda is not None else None
    npm = _safe_div(pat, net_sales)
    tax_rate = _safe_div(tax, pbt)
    interest_cov = _safe_div(ebit, interest_exp)

    # -----------------------------
    # Build Output JSON
    # -----------------------------
    output = {
        "company": input_json.get("longname"),
        "reporting_period": {
            "period_end": input_json.get("periodEndDT"),
            "coverage": input_json.get("finresultDate"),
            "filing_date": input_json.get("filingDate"),
        },
        "income_statement": {
            "Revenue (Net Sales)": net_sales,
            "Other Income": other_income,
            "Total Income": total_income,
            "Staff Cost": staff_cost,
            "Other Operating Expenses": other_exp,
            "Depreciation": depreciation,
            "Interest Expense": interest_exp,
            "EBIT (PBIT)": ebit,
            "EBITDA": ebitda,
            "Profit Before Tax (PBT)": pbt,
            "Tax Expense": tax,
            "Profit After Tax (PAT)": pat,
            "Total Expenses (excl. tax)": total_exp
        },
        "per_share": {
            "Face Value (₹)": face_value,
            "Basic EPS": basic_eps,
            "Diluted EPS": diluted_eps,
        },
        "ratios": {
            "EBIT Margin": ebit_margin,
            "EBITDA Margin": ebitda_margin,
            "Net Profit Margin": npm,
            "Effective Tax Rate": tax_rate,
            "Interest Coverage (x)": interest_cov,
        },
        "source": {
            "result_format": input_json.get("resultFormat"),
            "attachment": input_json.get("attachment_filename"),
            "raw_seqnum": input_json.get("seqnum")
        }
    }

    return output


def corporate_financial_statement(symbol:str, type:str, start_date: str, end_date: str, issuer: str) -> dict:
     
    """
    Fetch corporate's financial statement for that year or quater for a given symbol
    Example: symbo="INFY" type: Annual or Quarterly
    Return the list of financial details filled by an organization between that period
    """
    try:
        payload = f"{baseUrl}/api/corporates-financial-results?index=equities&symbol={symbol.upper()}&issuer={issuer}&period={type}&fo_sec=true"
        data = nsefetch(payload)
        fin_statements = data
        fin_results = []
        # For each fin statement, call the detailed data endpoint and attach the returned 'fin' array as 'fin_data'
        for fin_statement in fin_statements:
            fin_statement = dict(fin_statement) if isinstance(fin_statement, dict) else {"raw": fin_statement}
            fin_statement_params = fin_statement.get('params')
            fin_statement_industry = fin_statement.get('industry', "-") or "-"
            fin_statement_seq_id = fin_statement.get('seqNumber') or fin_statement.get('seq_id')
            # build payload for detailed financial data
            detail_payload = (
                f"{baseUrl}/api/corporates-financial-results-data?index=equities&params={fin_statement_params}"
                f"&seq_id={fin_statement_seq_id}&industry={fin_statement_industry}&frOldNewFlag=N&ind=N&format=New"
            )
            fin_data = nsefetch(detail_payload)
            # many NSE responses include the detailed entries under key 'fin' (or similar).
            # Prefer the 'fin' array when present, otherwise keep an empty list or the full payload.
            if isinstance(fin_data, dict):
                fin_results.append(transform_nse_financials(fin_data)) if isinstance(fin_data, dict) else None
                
           

        # Return a dict (tools expect dict/None). Wrap results under a key.
        return {"symbol": symbol.upper(), "financial_statements": fin_results}
    except Exception as e:
        return {"error": str(e)}    
     
mcp.http_app()
                                                                                                                                                                                                                 
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="NSE Stock API (test via api.py)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/stock/{symbol}", response_class=JSONResponse)
def get_stock(symbol: str):
    result = stock_price(symbol)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result


@app.get("/stock/{symbol}/historical", response_class=JSONResponse)
def get_historical(symbol: str, start_date: str, end_date: str):
    result = stock_historical_price(symbol, start_date, end_date)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result


@app.get("/stock/{symbol}/announcements", response_class=JSONResponse)
def get_announcements(symbol: str):
    result = stock_announcement(symbol)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result


@app.get("/stock/{symbol}/financials", response_class=JSONResponse)
def get_financials(symbol: str, type: str, start_date: str, end_date: str, issuer: str):
    result = corporate_financial_statement(symbol, type, start_date, end_date, issuer)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
