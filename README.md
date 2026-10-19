
import json
import urllib.request
import urllib.parse
import zipfile
import io
from datetime import datetime, timezone

CDN = "https://cdn.tsetmc.com/api"
LEGACY_MARKET_WATCH = "https://old.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0"


def request_bytes(url, timeout=20):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36",
            "Accept": "application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read()


def test_cdn():
    symbol = urllib.parse.quote("فولاد", safe="")
    url = CDN + "/Instrument/GetInstrumentSearch/" + symbol
    status, content_type, body = request_bytes(url, timeout=12)
    data = json.loads(body.decode("utf-8-sig"))
    items = data.get("instrumentSearch", [])
    found = next(
        (x for x in items if x.get("lVal18AFC") == "فولاد" and x.get("insCode")),
        None,
    )
    result = {
        "success": bool(found),
        "http_status": status,
        "content_type": content_type,
        "search_count": len(items),
        "symbol_found": found,
    }
    if found:
        quote_url = CDN + "/ClosingPrice/GetClosingPriceInfo/" + str(found["insCode"])
        quote_status, quote_type, quote_body = request_bytes(quote_url, timeout=12)
        quote = json.loads(quote_body.decode("utf-8-sig"))
        result["quote"] = {
            "success": quote_status == 200 and bool(quote),
            "http_status": quote_status,
            "content_type": quote_type,
            "response_keys": list(quote.keys()),
        }
    return result


def test_legacy_market_watch():
    status, content_type, body = request_bytes(LEGACY_MARKET_WATCH, timeout=25)
    is_xlsx = body[:2] == b"PK" and zipfile.is_zipfile(io.BytesIO(body))
    result = {
        "success": status == 200 and is_xlsx,
        "http_status": status,
        "content_type": content_type,
        "bytes_received": len(body),
        "xlsx_signature_valid": is_xlsx,
    }
    if is_xlsx:
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            names = archive.namelist()
            result["workbook_parts_present"] = (
                "xl/workbook.xml" in names
                and "xl/worksheets/sheet1.xml" in names
            )
    return result


def main():
    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": "A green workflow only means the test script ran. Each source is successful only when its response is validated.",
        "tests": {},
    }

    for name, tester in (
        ("tsetmc_cdn", test_cdn),
        ("tsetmc_legacy_market_watch", test_legacy_market_watch),
    ):
        try:
            result["tests"][name] = tester()
        except Exception as error:
            result["tests"][name] = {
                "success": False,
                "error": str(error),
            }

    result["any_source_validated"] = any(
        item.get("success") for item in result["tests"].values()
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
