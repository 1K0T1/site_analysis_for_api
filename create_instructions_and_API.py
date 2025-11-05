from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import TargetClosedError
import requests
from urllib.parse import urljoin
from pathlib import Path
import json
import subprocess
import re
import shutil
from urllib.parse import urljoin, urlparse


# что бы автоматом открывать и зыкрывать бразуер
def browser(func):
    def wrapper(self, *args, **kwargs):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-infobars",
                ],
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
                permissions=["microphone", "camera", "clipboard-read", "clipboard-write"],
                )
            page = context.new_page()
            result = func(self, page, *args, **kwargs)
            try:
                return result
            finally:
                browser.close()

    return wrapper


class Instructions_API:
    # парсим код
    @browser
    def open_resource(self, page, resource, filename):
        users_files = Path(__file__).parent / "users_file" / filename
        if users_files.is_dir():
            shutil.rmtree(users_files)
        users_files.mkdir(parents=True, exist_ok=True)
        page.goto(resource, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        prefix = ["/popular-in"]
        links_a = []
        templates = set()  # что бы не повторялись страницы
        hrefs = set()  # что бы не повторялись страницы

        # все ссылки
        match = re.search(r"https?://([^/]+)/?", page.url)
        base_domain = match.group(1) if match else ""
        links = page.query_selector_all("a")

        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            blocked = False
            for domens in prefix:
                if re.search(domens, href):
                    blocked = True
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
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                html_con = page.content()
                filehtml = users_files / f"{i}.html"
                filehtml.write_text(html_con, encoding="utf-8")
            except PlaywrightTimeoutError:
                return f"Ссылка не загрузилась: {url}"

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
                    name = re.split(r"[?&]", name)[0]
                name = name[:150]
                name = re.sub(r'[<>:"/\\|?*]=&', "_", name)
                filejs = users_files / f"{name}"
                filejs.write_text(r.text, encoding="utf-8")
            except:
                return None

    # сохраняем в txt все ссылки
    @browser
    def all_links(self, page, resource, filename):
        users_files = Path(__file__).parent / "users_file" / filename
        users_files.mkdir(parents=True, exist_ok=True)
        page.goto(resource, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(9000)

        prefix = ["/popular-in"]
        links_a = []
        links_full = []
        templates = set()  # что бы не повторялись страницы
        hrefs = set()  # что бы не повторялись страницы

        # все ссылки
        match = re.search(r"https?://([^/]+)/?", page.url)
        base_domain = match.group(1) if match else ""
        links = page.query_selector_all("a")

        for link in links:
            href = link.get_attribute("href")

            if not href:
                continue
            blocked = False

            for domens in prefix:
                if re.search(domens, href):
                    blocked = True
                    break
            if blocked:
                continue

            full_url = urljoin(page.url, href)

            if base_domain not in full_url:
                continue

            # создаем шаблоны
            parsed = urlparse(full_url)
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) >= 1:
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
            try:
                page.goto(urls, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(9000)
                a_tags = page.query_selector_all("a[href]")
                link_tags = page.query_selector_all("link[href]")

                content_hrefs = [
                    urljoin(page.url, tag.get_attribute("href"))
                    for tag in a_tags + link_tags
                    if tag.get_attribute("href")
                ]
                
                links_full.extend(content_hrefs)
            except PlaywrightTimeoutError:
                links_full.append(f"Ссылка не загрузилась: {urls}")
                continue
                
        links_full = list(dict.fromkeys(links_full))
        return links_full
    
    # ловим поток
    @browser
    def flow_download(self, page, resource, name):
        users_files = Path(__file__).parent / "users_file"
        users_files.mkdir(parents=True, exist_ok=True)

        def on_response(response):
            content_type = (response.headers.get("content-type") or "").lower()
            url = response.url.lower()
            
            # фильтруем по типу контента
            media_types = (
                "application/json",
                "audio/",
                "video/",
                "mpeg",
                "mp3",
                "mp4",
                "ogg",
                "webm",
                "wav",
                "aac",
                "flac",
                "m3u8",
                "mpegurl"
            )
            
            #
            if not any(mt in content_type for mt in media_types):
                return

            try:
                body = response.body()
            except TargetClosedError:
                return
            except Exception as e:
                print("ошибка")
                return

            # определяем расширение файла
            if "json" in content_type:
                ext = "json"
            elif "m3u8" in url or "mpegurl" in content_type:
                ext = "m3u8"
            elif "audio" in content_type:
                ext = content_type.split("/")[-1].split(";")[0]
            elif "video" in content_type:
                ext = content_type.split("/")[-1].split(";")[0]
            else:
                ext = "bin"

            # потоковые фрагементы
            if (
                ".m3u8" in url
                or "application/x-mpegurl" in content_type
                or "application/vnd.apple.mpegurl" in content_type
                or "video/mp2t" in content_type
                or url.endswith(".ts")
                ):
                flow = "hls"
            else:
                flow = "progressiv"

            #имя файла
            name_file = re.sub(r"[^0-9a-zA-Z._-]", "_", url.split("?")[0].split("/")[-1])[:150]
            if not name_file.endswith(f".{ext}"):
                name_file += f".{ext}"

            # сохраняем файл
            jsonfile = users_files / name / name_file
            print(jsonfile)
            with open(jsonfile, "wb") as f:
                f.write(body)
                
            if ext == "json":
                try:
                    data = json.loads(body.decode("utf-8"))
                    # пытаемся найти url на m3u8 где угодно
                    text = json.dumps(data)
                    match = re.search(r"https?://[^\s\"']+\.m3u8", text)
                    if match:
                        m3u8_url = match.group(0)
                        out_path = jsonfile.with_suffix(".mp3")

                        # определяем, видео это или аудио
                        is_video = any(x in m3u8_url for x in ("video", "mp4", "720", "1080", "res", "hlsv"))
                        out_path = jsonfile.with_suffix(".mp4" if is_video else ".mp3")

                        # запускаем ffmpeg для скачивания и конвертации
                        subprocess.run([
                            "ffmpeg",
                            "-protocol_whitelist", "file,http,https,tcp,tls",
                            "-y",
                            "-i", m3u8_url,
                            "-c", "copy",
                            str(out_path)
                        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception as e:
                    pass
                    
            elif flow == "hls" and jsonfile.suffix == ".m3u8":

                # определяем, это видео или аудио
                is_video = any(x in content_type for x in ("video", "mp4", "mpeg"))
                out_path = jsonfile.with_suffix(".mp4" if is_video else ".mp3")

                # запускаем ffmpeg для скачивания и конвертации
                subprocess.run([
                    "ffmpeg",
                    "-protocol_whitelist", "file,http,https,tcp,tls",
                    "-y",
                    "-i", str(jsonfile),
                    "-c", "copy",
                    str(out_path)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # ловим ответы
        page.on("response", on_response)
        page.goto(resource, wait_until="domcontentloaded")
        page.wait_for_timeout(25000)
