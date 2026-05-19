from playwright.sync_api import sync_playwright
import json, sys, time

def fetch_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        time.sleep(1.5)
        html = page.content()
        title = page.title()
        headings = []
        for tag in ['h1','h2','h3']:
            els = page.query_selector_all(tag)
            for e in els:
                headings.append({'tag': tag, 'text': e.inner_text()})
        links = [a.get_attribute('href') for a in page.query_selector_all('a') if a.get_attribute('href')]
        browser.close()
        return {'url': url, 'title': title, 'headings': headings, 'outbound_links': links, 'html_length': len(html)}

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv)>1 else 'https://example.com'
    print(json.dumps(fetch_page(url)))
