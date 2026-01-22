#!/usr/bin/env python3
"""
GPU Stock Tracker for Montreal, Canada
Tracks ASUS Prime GeForce RTX 5070 Ti 16GB availability at Canadian retailers.
"""

import requests
import json
import time
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional
import re

# Configuration
CONFIG = {
    "gpu_name": "ASUS Prime GeForce RTX 5070 Ti 16GB GDDR7",
    "model_number": "PRIME-RTX5070TI-16G",
    "check_interval_minutes": 5,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Canadian retailers to check
VENDORS = {
    "canada_computers": {
        "name": "Canada Computers",
        "search_url": "https://www.canadacomputers.com/search/results_ajax.php?keywords=PRIME-RTX5070TI-16G",
        "product_url": "https://www.canadacomputers.com/search/product_search.php?keywords=PRIME-RTX5070TI-16G",
        "montreal_stores": ["Montreal Downtown", "Montreal Eaton Centre", "Laval", "Brossard"]
    },
    "memory_express": {
        "name": "Memory Express",
        "search_url": "https://www.memoryexpress.com/Search/Products?Search=PRIME-RTX5070TI-16G",
        "product_url": "https://www.memoryexpress.com/Search/Products?Search=PRIME-RTX5070TI-16G"
    },
    "best_buy": {
        "name": "Best Buy Canada",
        "search_url": "https://www.bestbuy.ca/api/v2/json/search?query=ASUS+PRIME+RTX+5070+Ti",
        "product_url": "https://www.bestbuy.ca/en-ca/search?search=ASUS+PRIME+RTX+5070+Ti"
    },
    "newegg": {
        "name": "Newegg Canada",
        "search_url": "https://www.newegg.ca/p/pl?d=PRIME-RTX5070TI-16G",
        "product_url": "https://www.newegg.ca/p/pl?d=PRIME-RTX5070TI-16G"
    },
    "amazon": {
        "name": "Amazon.ca",
        "search_url": "https://www.amazon.ca/s?k=ASUS+PRIME+RTX+5070+Ti+16GB",
        "product_url": "https://www.amazon.ca/s?k=ASUS+PRIME+RTX+5070+Ti+16GB"
    }
}


def log(message: str):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def check_canada_computers() -> Optional[dict]:
    """Check Canada Computers for stock."""
    try:
        headers = {"User-Agent": CONFIG["user_agent"]}
        response = requests.get(
            VENDORS["canada_computers"]["search_url"],
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            content = response.text.lower()
            model = CONFIG["model_number"].lower()

            if model in content or "5070 ti" in content:
                # Check for stock indicators
                if "in stock" in content or "add to cart" in content:
                    return {
                        "vendor": "Canada Computers",
                        "status": "IN STOCK",
                        "url": VENDORS["canada_computers"]["product_url"]
                    }
                elif "back order" in content:
                    return {
                        "vendor": "Canada Computers",
                        "status": "BACKORDER",
                        "url": VENDORS["canada_computers"]["product_url"]
                    }

        return {"vendor": "Canada Computers", "status": "NOT FOUND", "url": None}

    except Exception as e:
        return {"vendor": "Canada Computers", "status": f"ERROR: {e}", "url": None}


def check_best_buy() -> Optional[dict]:
    """Check Best Buy Canada for stock."""
    try:
        headers = {"User-Agent": CONFIG["user_agent"]}
        response = requests.get(
            VENDORS["best_buy"]["search_url"],
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            try:
                data = response.json()
                products = data.get("products", [])

                for product in products:
                    name = product.get("name", "").lower()
                    if "5070 ti" in name and "asus" in name:
                        availability = product.get("availability", {})
                        if availability.get("onlineAvailability") or availability.get("inStoreAvailability"):
                            return {
                                "vendor": "Best Buy Canada",
                                "status": "IN STOCK",
                                "url": f"https://www.bestbuy.ca{product.get('productUrl', '')}"
                            }
            except json.JSONDecodeError:
                pass

        return {"vendor": "Best Buy Canada", "status": "NOT FOUND", "url": None}

    except Exception as e:
        return {"vendor": "Best Buy Canada", "status": f"ERROR: {e}", "url": None}


def check_newegg() -> Optional[dict]:
    """Check Newegg Canada for stock."""
    try:
        headers = {"User-Agent": CONFIG["user_agent"]}
        response = requests.get(
            VENDORS["newegg"]["search_url"],
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            content = response.text.lower()
            model = CONFIG["model_number"].lower()

            if model in content or ("5070 ti" in content and "asus" in content):
                if "add to cart" in content and "out of stock" not in content:
                    return {
                        "vendor": "Newegg Canada",
                        "status": "IN STOCK",
                        "url": VENDORS["newegg"]["product_url"]
                    }

        return {"vendor": "Newegg Canada", "status": "NOT FOUND", "url": None}

    except Exception as e:
        return {"vendor": "Newegg Canada", "status": f"ERROR: {e}", "url": None}


def check_memory_express() -> Optional[dict]:
    """Check Memory Express for stock."""
    try:
        headers = {"User-Agent": CONFIG["user_agent"]}
        response = requests.get(
            VENDORS["memory_express"]["search_url"],
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            content = response.text.lower()
            model = CONFIG["model_number"].lower()

            if model in content or ("5070 ti" in content and "asus" in content):
                if "add to cart" in content or "in stock" in content:
                    return {
                        "vendor": "Memory Express",
                        "status": "IN STOCK",
                        "url": VENDORS["memory_express"]["product_url"]
                    }

        return {"vendor": "Memory Express", "status": "NOT FOUND", "url": None}

    except Exception as e:
        return {"vendor": "Memory Express", "status": f"ERROR: {e}", "url": None}


def check_amazon() -> Optional[dict]:
    """Check Amazon.ca for stock."""
    try:
        headers = {"User-Agent": CONFIG["user_agent"]}
        response = requests.get(
            VENDORS["amazon"]["search_url"],
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            content = response.text.lower()

            if "5070 ti" in content and "asus" in content:
                if "add to cart" in content and "currently unavailable" not in content:
                    return {
                        "vendor": "Amazon.ca",
                        "status": "POSSIBLY IN STOCK",
                        "url": VENDORS["amazon"]["product_url"]
                    }

        return {"vendor": "Amazon.ca", "status": "NOT FOUND", "url": None}

    except Exception as e:
        return {"vendor": "Amazon.ca", "status": f"ERROR: {e}", "url": None}


def send_email_notification(results: list):
    """Send email notification when stock is found."""
    # Load email settings from environment variables
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    email_user = os.environ.get("EMAIL_USER")
    email_pass = os.environ.get("EMAIL_PASS")
    notify_email = os.environ.get("NOTIFY_EMAIL")

    if not all([email_user, email_pass, notify_email]):
        log("Email notification skipped - credentials not configured")
        return

    in_stock = [r for r in results if "IN STOCK" in r["status"]]
    if not in_stock:
        return

    body = f"GPU Stock Alert!\n\n{CONFIG['gpu_name']}\n\n"
    for result in in_stock:
        body += f"- {result['vendor']}: {result['status']}\n"
        if result['url']:
            body += f"  URL: {result['url']}\n"

    msg = MIMEText(body)
    msg["Subject"] = f"GPU IN STOCK: {CONFIG['gpu_name']}"
    msg["From"] = email_user
    msg["To"] = notify_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
        log("Email notification sent!")
    except Exception as e:
        log(f"Failed to send email: {e}")


def play_sound_alert():
    """Play a sound alert (cross-platform)."""
    try:
        # Try different methods for sound alert
        import subprocess
        import sys

        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
        elif sys.platform == "linux":
            subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], check=False)
        elif sys.platform == "win32":
            import winsound
            winsound.Beep(1000, 500)
    except:
        print("\a")  # Terminal bell


def check_all_vendors() -> list:
    """Check all vendors for stock."""
    log(f"Checking stock for: {CONFIG['gpu_name']}")
    log("-" * 60)

    results = []

    # Check each vendor
    checkers = [
        check_canada_computers,
        check_best_buy,
        check_newegg,
        check_memory_express,
        check_amazon
    ]

    for checker in checkers:
        result = checker()
        results.append(result)

        status_icon = "✓" if "IN STOCK" in result["status"] else "✗"
        log(f"{status_icon} {result['vendor']}: {result['status']}")

        if result["url"]:
            log(f"  → {result['url']}")

        time.sleep(1)  # Be polite to servers

    return results


def run_tracker():
    """Main tracking loop."""
    print("=" * 60)
    print(f"GPU Stock Tracker - Montreal, Canada")
    print(f"Tracking: {CONFIG['gpu_name']}")
    print(f"Model: {CONFIG['model_number']}")
    print(f"Check interval: {CONFIG['check_interval_minutes']} minutes")
    print("=" * 60)
    print()

    while True:
        try:
            results = check_all_vendors()

            # Check if any are in stock
            in_stock = [r for r in results if "IN STOCK" in r["status"]]

            if in_stock:
                log("*** STOCK FOUND! ***")
                play_sound_alert()
                send_email_notification(results)

            log(f"Next check in {CONFIG['check_interval_minutes']} minutes...")
            print()

            time.sleep(CONFIG["check_interval_minutes"] * 60)

        except KeyboardInterrupt:
            log("Tracker stopped by user")
            break
        except Exception as e:
            log(f"Error during check: {e}")
            time.sleep(60)  # Wait a minute before retrying


def check_once():
    """Run a single check (useful for testing or cron jobs)."""
    results = check_all_vendors()

    in_stock = [r for r in results if "IN STOCK" in r["status"]]
    if in_stock:
        send_email_notification(results)
        return True
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Single check mode
        check_once()
    else:
        # Continuous monitoring mode
        run_tracker()
