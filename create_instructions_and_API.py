from playwright.sync_api import sync_playwright
import requests
from urllib.parse import urljoin
from pathlib import Path
import re
import shutil
from urllib.parse import urljoin, urlparse

#что бы автоматом открывать и зыкрывать бразуер
def browser(func):
    def wrapper(self, *args, **kwargs):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-infobars"
            ])
            context = browser.new_context()
            page = context.new_page()
            result = func(self, page, *args, **kwargs)
            try:
                return result
            finally:
                browser.close()
    return wrapper

class Instructions_API():
    #парсим код
    @browser
    def open_resource(self, page, resource, filename):
        users_files = Path(__file__).parent / "users_file" / filename
        if users_files.is_dir():
            shutil.rmtree(users_files)
        users_files.mkdir(parents=True, exist_ok=True)
        page.goto(resource, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        
        prefix= ["/popular-in"]
        links_a = []
        links_full = []
        templates = set() #что бы не повторялись страницы
        hrefs = set() #что бы не повторялись страницы
        
        # все ссылки
        match = re.search(r"https?://([^/]+)/?", page.url)
        base_domain = match.group(1) if match else ""
        links = page.query_selector_all("a")
        
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            blocked= False
            for domens in prefix:
                if re.search(domens, href):
                    blocked= True
                    break
                
            if blocked:
                continue
            full_url = urljoin(page.url, href)
            
            if base_domain not in full_url:
                continue
            
            # создаем шаблоны
            parsed = urlparse(full_url)
            path_parts = parsed.path.strip("/").split("/")
            
            if len(path_parts) >= 2:
                template = f"{parsed.netloc}/{path_parts[0]}"
            else:
                template = f"{parsed.netloc}/"

            if template in templates:
                continue
            
            print(full_url)
            templates.add(template)
            prefix.append(full_url)
            links_a.append(full_url)
            hrefs.add(full_url)

        # все html
        html = page.content()
        filehtml = users_files / "index.html"
        filehtml.write_text(html, encoding="utf-8")
        
        for i, htmls in enumerate(hrefs, start=1):
            if htmls.startswith("http") or htmls.startswith("https"):
                url = htmls 
            else:
                url = page.url.rstrip("/") + "/" + htmls.lstrip("/")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            html_con = page.content()
            filehtml = users_files / f"{i}.html"
            filehtml.write_text(html_con, encoding="utf-8")

        # все js файлы
        scripts = page.query_selector_all("script[src]")
        
        for script in scripts:
            src = script.get_attribute("src")
            full_url = urljoin(page.url, src)
            try:
                r = requests.get(full_url, timeout=15)
            except Exception as e:
                print(f"Пропускаем { full_url}\n{e}")
            name = Path(src).name

            try:
                if ".js" in name:
                    name = name.split(".js")[0] + ".js"
                else:
                    name = re.split(r'[?&]', name)[0]
                name = name[:150]
                name = re.sub(r'[<>:"/\\|?*]=&', "_", name)
                filejs = users_files / f"{name}"
                filejs.write_text(r.text, encoding="utf-8")
            except:
                return None
        
    #сохраняем в txt все ссылки
    @browser
    def all_links(self, page, resource, filename):
        users_files = Path(__file__).parent / "users_file" / filename
        users_files.mkdir(parents=True, exist_ok=True)
        page.goto(resource, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        
        prefix= ["/popular-in"]
        links_a = []
        links_full = []
        templates = set() #что бы не повторялись страницы
        hrefs = set() #что бы не повторялись страницы
        
        # все ссылки
        match = re.search(r"https?://([^/]+)/?", page.url)
        base_domain = match.group(1) if match else ""
        links = page.query_selector_all("a")
        
        for link in links:
            href = link.get_attribute("href")
            
            if not href:
                continue
            blocked= False
            
            for domens in prefix:
                if re.search(domens, href):
                    blocked= True
                    break
            if blocked:
                continue
            
            full_url = urljoin(page.url, href)
            
            if base_domain not in full_url:
                continue
            
            # создаем шаблоны
            parsed = urlparse(full_url)
            path_parts = parsed.path.strip("/").split("/")
            
            if len(path_parts) >= 2:
                template = f"{parsed.netloc}/{path_parts[0]}"
            else:
                template = f"{parsed.netloc}/"

            if template in templates:
                continue
            
            print(full_url)
            templates.add(template)
            links_a.append(full_url)
            hrefs.add(full_url)
            links_full.extend(links_a)
        
        for urls in links_a:
            page.goto(urls, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(6000)
            a_tags = page.query_selector_all("a[href]")
            link_tags = page.query_selector_all("link[href]")
            
            hrefs = [
                urljoin(page.url, tag.get_attribute("href"))
                for tag in a_tags + link_tags
                if tag.get_attribute("href")
                ]
            links_full.extend(hrefs)
            
        return links_full