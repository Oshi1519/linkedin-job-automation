from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import csv

def login_linkedin():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get("https://www.linkedin.com/login")
    time.sleep(3)
    print("Opening LinkedIn Login Page...")
    print("Please sign in with your Google account.")
    print("You have 60 seconds to complete the login.")
    time.sleep(60)
    print("Login successful.")
    time.sleep(3)
    driver.get("https://www.linkedin.com/feed")
    time.sleep(3)
    print("Navigating to search page...")
    return driver

if __name__ == "__main__":
    print("=" * 50)
    print("  LinkedIn Job Search Automation")
    print("  Keywords: Web Developer")
    print("=" * 50)
    input("\nClose all Chrome windows then press ENTER...")

    driver = login_linkedin()

    search_url = "https://www.linkedin.com/search/results/content/?keywords=Web%20Developer&datePosted=past-24h"
    driver.get(search_url)
    time.sleep(6)
    print("Search page loaded.")

    try:
        for i in range(10):
            driver.execute_script(f"window.scrollTo(0, {i * 600});")
            time.sleep(1)
    except:
        print("Scrolling skipped.")

    recruiters = []

    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
    except:
        print("Could not read page. Please try again.")
        driver.quit()
        exit()

    chunks = body_text.split("Like\nComment\nRepost\nSend")

    skip_words = [
        "notification", "Home", "Jobs", "Messaging", "LinkedIn",
        "Feed post", "About", "Accessibility", "Are these results",
        "Only connections", "Privacy", "Help Center", "Sign in",
        "Ad Choices", "Advertising", "Follow", "Like", "Comment",
        "Business Services", "You are on the messaging",
        "My Network", "Notifications", "For Business",
        "Your feedback", "Compose message", "Try Premium",
        "Sort by", "Past 24", "Content type", "From me",
        "• 3rd+", "• 2nd", "• 1st", "All filters", "Posts",
        "Reset", "More", "N/A"
    ]

    for chunk in chunks:
        lines = [l.strip() for l in chunk.strip().split('\n') if l.strip()]
        if len(lines) < 3:
            continue

        name = "N/A"
        title = "N/A"
        content = "N/A"

        for i, line in enumerate(lines):
            if any(skip.lower() in line.lower() for skip in skip_words):
                continue
            if name == "N/A" and len(line) > 3:
                name = line
            elif title == "N/A" and len(line) > 3:
                title = line
            elif content == "N/A" and len(line) > 10:
                content = " ".join(lines[i:])[:300]
                break

        if name == "N/A":
            continue

        if any(skip.lower() in name.lower() for skip in skip_words):
            continue

        email_found = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', chunk)
        email = email_found[0] if email_found else "Not provided"

        phone_found = re.findall(r'[6-9]\d{9}', chunk)
        phone = phone_found[0] if phone_found else "Not provided"

        recruiters.append({
            "Name": name,
            "Title": title,
            "Email": email,
            "Phone": phone,
            "Post": content
        })

    
    seen = set()
    unique = []
    for r in recruiters:
        if r['Name'] not in seen and len(r['Name']) > 3:
            seen.add(r['Name'])
            unique.append(r)


    with open("recruiters_output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Name","Title","Email","Phone","Post"])
        writer.writeheader()
        writer.writerows(unique)

    print(f"\nFound {len(unique)} recruiters!")
    print("Saved to recruiters_output.csv\n")

    for r in unique:
        print(f"  Name  : {r['Name']}")
        print(f"  Title : {r['Title']}")
        print(f"  Email : {r['Email']}")
        print(f"  Phone : {r['Phone']}")
        print(f"  Post  : {r['Post'][:80]}...")
        print()

    print("=" * 50)
    print("  Process Completed Successfully.")
    print("=" * 50)
    input("\nPress ENTER to close browser...")
    driver.quit()