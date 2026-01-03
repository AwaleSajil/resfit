import requests
import trafilatura
import random

def scrape_job_details(url):
    # 1. Setup headers to look like a real browser
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        # 2. Fetch the HTML manually using requests
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Check for HTTP errors
        
        # 3. Pass the raw HTML to trafilatura for extraction
        # We use 'extract' on the response text directly
        content = trafilatura.extract(
            response.text, 
            include_formatting=True,
            include_links=False,
            favor_precision=True
        )

        if not content:
            return "Error: Could not identify the main content of the page."

        return content

    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# # --- Usage ---
# url = "https://careers.qualcomm.com/careers/job/446715275527?hl=en-US&domain=qualcomm.com&source=APPLICANT_SOURCE-6-2"
# print(scrape_job_details(url))