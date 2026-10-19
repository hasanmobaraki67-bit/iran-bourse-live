from datetime import datetime, timezone
import json
import urllib.request
import urllib.error

# این مرحله فقط برای بررسی دسترسی به منبع داده است.
# هنوز هیچ منبعی به عنوان منبع زنده بورس تأیید نشده است.

SOURCES_TO_TEST = [
    {
        "name": "TSETMC",
        "url": "https://www.tsetmc.com/"
    }
]


def test_source(source):
    result = {
        "source": source["name"],
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "reachable": False,
        "http_status": None,
        "error": None,
        "note": (
            "دسترسی به صفحه اصلی به‌تنهایی به معنی دسترسی "
            "به داده زنده تابلو نیست."
        ),
    }

    request = urllib.request.Request(
        source["url"],
        headers={"User-Agent": "IranBourseLive/0.1"}
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result["reachable"] = 200 <= response.status < 400
            result["http_status"] = response.status

    except urllib.error.HTTPError as error:
        result["http_status"] = error.code
        result["error"] = str(error)

    except Exception as error:
        result["error"] = str(error)

    return result


if __name__ == "__main__":
    results = [test_source(source) for source in SOURCES_TO_TEST]
    print(json.dumps(results, ensure_ascii=False, indent=2))


