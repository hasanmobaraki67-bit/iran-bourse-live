import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

BASE_URL = "https://cdn.tsetmc.com/api"


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 IranBourseLive/0.2",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP status: {response.status}")

        return json.loads(response.read().decode("utf-8"))


def main():
    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "TSETMC CDN API",
        "tests": {},
    }

    # آزمایش اول: جست‌وجوی نماد فولاد
    try:
        symbol = urllib.parse.quote("فولاد", safe="")
        data = get_json(
            f"{BASE_URL}/Instrument/GetInstrumentSearch/{symbol}"
        )

        items = data.get("instrumentSearch", [])
        result["tests"]["symbol_search"] = {
            "success": True,
            "count": len(items),
            "symbols": [
                {
                    "symbol": item.get("lVal18AFC"),
                    "name": item.get("lVal30"),
                    "insCode": item.get("insCode"),
                }
                for item in items[:5]
            ],
        }

        # آزمایش دوم: دریافت اطلاعات قیمت نماد فولاد
        found = next(
            (
                item for item in items
                if item.get("lVal18AFC") == "فولاد"
                and item.get("insCode")
            ),
            None,
        )

        if found:
            ins_code = found["insCode"]
            quote = get_json(
                f"{BASE_URL}/ClosingPrice/GetClosingPriceInfo/{ins_code}"
            )

            result["tests"]["stock_quote"] = {
                "success": True,
                "insCode": ins_code,
                "data": quote,
            }
        else:
            result["tests"]["stock_quote"] = {
                "success": False,
                "error": "نماد فولاد در پاسخ جست‌وجو پیدا نشد",
            }

    except Exception as error:
        result["tests"]["api_error"] = str(error)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
