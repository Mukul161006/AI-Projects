from playwright.sync_api import sync_playwright
import time, json, sys

def fetch_serp(keyword, limit=10):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f'https://www.google.com/search?q={keyword}&hl=en')
        time.sleep(1.5)
        results = []
        els = page.query_selector_all('div.g')
        for el in els:
            try:
                title_el = el.query_selector('h3')
                title = title_el.inner_text() if title_el else ''
                a = el.query_selector('a')
                link = a.get_attribute('href') if a else ''
                snippet_el = el.query_selector('.VwiC3b')
                snippet = snippet_el.inner_text() if snippet_el else ''
                results.append({'title': title, 'url': link, 'snippet': snippet})
            except Exception as e:
                continue
            if len(results) >= limit:
                break
        browser.close()
        return results

if __name__ == '__main__':
    kw = sys.argv[1] if len(sys.argv)>1 else 'ai tools for students'
    print(json.dumps(fetch_serp(kw)))
