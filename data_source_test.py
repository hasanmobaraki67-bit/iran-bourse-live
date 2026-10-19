
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

HOSTS = [
    "https://cdn.tsetmc.com/api",
    "https://cdn10.tsetmc.com/api",
    "https://cdn1.tsetmc.com/api",
    "https://cdn2.tsetmc.com/api",
]


def get_json(path):
    errors = []

    for host in HOSTS:
        url = host + path

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                request, timeout=8
            ) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )
                return data, host

        except Exception as error:
            errors.append(
                host + " -> " + str(error)
            )

    raise RuntimeError(
        "همه سرورها ناموفق بودند: "
        + " | ".join(errors)
    )


def main():
    result = {
        "checked_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": "TSETMC API",
        "tests": {},
    }

    try:
        symbol = urllib.parse.quote(
            "فولاد", safe=""
        )

        data, host = get_json(
            "/Instrument/GetInstrumentSearch/"
            + symbol
        )

        items = data.get("instrumentSearch", [])

        result["source_host"] = host
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

            quote, quote_host = get_json(
                "/ClosingPrice/GetClosingPriceInfo/"
                + str(ins_code)
            )

            result["tests"]["stock_quote"] = {
                "success": True,
                "host": quote_host,
                "insCode": ins_code,
                "data": quote,
            }
        else:
            result["tests"]["stock_quote"] = {
                "success": False,
                "error": "نماد فولاد پیدا نشد",
            }

    except Exception as error:
        result["tests"]["api_error"] = str(error)

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
