import requests
from pathlib import Path
import json
import subprocess
import re
import shutil
from uuid import uuid4
import threading

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Error as PlaywrightError
from playwright._impl._errors import TargetClosedError
from urllib.parse import urljoin, urlparse
from urllib.parse import urljoin
from loguru import logger
import jsbeautifier

from log.log import log_server

LIMIT_BROWSER = threading.Semaphore(2)


# что бы автоматом открывать и зыкрывать бразуер
def browser(func):
    def wrapper(self, *args, **kwargs):
        with sync_playwright() as p:
            with LIMIT_BROWSER:
                try:
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
                        permissions=[
                            "microphone",
                            "camera",
                            "clipboard-read",
                            "clipboard-write",
                        ],
                    )
                    page = context.new_page()
                    result = func(self, page, *args, **kwargs)
                    try:
                        return result
                    finally:
                        browser.close()
                except PlaywrightError as e:
                    return str(e)

    return wrapper


class Instructions_API:

    # парсим код (html, js)
    @browser
    def open_resource(self, page, resource, name):
        users_files = Path(__file__).parent / "users_file" / name
        if users_files.is_dir():
            shutil.rmtree(users_files)
        users_files.mkdir(parents=True, exist_ok=True)
        page.goto(resource, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        prefix = ["/popular-in"]
        links_a = []
        templates = set()
        hrefs = set()

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

            logger.info(f"User: {name}")
            logger.info(f"Full url: {full_url}")
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
                logger.warning(f"Пропускаем {full_url}\n{e}")
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
    def all_links(self, page, resource, name):
        users_files = Path(__file__).parent / "users_file" / name
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

            logger.info(f"User: {name}")
            logger.info(f"Full url: {full_url}")
            templates.add(template)
            links_a.append(full_url)
            hrefs.add(full_url)
            links_full.extend(links_a)

        # обходим все ссылки и собираем внутренние
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
                "img/",
                "mpeg",
                "mp3",
                "mp4",
                "ogg",
                "webm",
                "wav",
                "aac",
                "flac",
                "m3u8",
                "mpegurl",
                "png",
                "ico",
                "jpg",
                "img",
            )

            if not any(mt in content_type for mt in media_types):
                return

            try:
                body = response.body()
            except TargetClosedError:
                return
            except Exception as e:
                logger.error(f"<red>Error</red>: {e}")
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
            elif "img" in content_type:
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

            # имя файла
            name_file = re.sub(
                r"[^0-9a-zA-Z._-]", "_", url.split("?")[0].split("/")[-1]
            )[:150]
            if not name_file.endswith(f".{ext}"):
                name_file += f".{ext}"

            # сохраняем файл
            jsonfile = users_files / name / name_file
            logger.info(f"User: {name}")
            logger.info(f"JSON: {jsonfile}")
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
                        is_video = any(
                            x in m3u8_url
                            for x in ("video", "mp4", "720", "1080", "res", "hlsv")
                        )
                        out_path = jsonfile.with_suffix(".mp4" if is_video else ".mp3")

                        # запускаем ffmpeg для скачивания и конвертации
                        subprocess.run(
                            [
                                "ffmpeg",
                                "-protocol_whitelist",
                                "file,http,https,tcp,tls",
                                "-y",
                                "-i",
                                m3u8_url,
                                "-c",
                                "copy",
                                str(out_path),
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                except Exception as e:
                    pass

            elif flow == "hls" and jsonfile.suffix == ".m3u8":

                # определяем, это видео или аудио
                is_video = any(x in content_type for x in ("video", "mp4", "mpeg"))
                out_path = jsonfile.with_suffix(".mp4" if is_video else ".mp3")

                # запускаем ffmpeg для скачивания и конвертации
                subprocess.run(
                    [
                        "ffmpeg",
                        "-protocol_whitelist",
                        "file,http,https,tcp,tls",
                        "-y",
                        "-i",
                        str(jsonfile),
                        "-c",
                        "copy",
                        str(out_path),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

        # ловим ответы
        page.on("response", on_response)
        page.goto(resource, wait_until="domcontentloaded")
        page.wait_for_timeout(25000)

    # медиа
    @browser
    def open_media(self, page, resource, name):
        users_files = Path(__file__).parent / "users_file" / name
        file_name = uuid4().hex

        page.goto(resource, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        # видео
        videos = page.query_selector_all("video")
        for idx, v in enumerate(videos, 1):
            video_data, video_type = page.evaluate(
                """
            async (video) => {
                const src = video.src || video.querySelector('source')?.src;
                if (!src) return [null, null];
                const blob = await fetch(src).then(r => r.blob());
                const buf = await blob.arrayBuffer();
                return [Array.from(new Uint8Array(buf)), blob.type];
            }
            """,
                v,
            )
            if video_data:
                ext = video_type.split("/")[-1] if video_type else "mp4"
                file_name = f"video_{uuid4().hex}.{ext}"
                with open(users_files / file_name, "wb") as f:
                    f.write(bytes(video_data))
                logger.info(f"User: {name}")
                logger.success(f"Save file: {file_name}")

        # картинки
        imgs = page.query_selector_all("img")
        for idx, img in enumerate(imgs, 1):
            img_data, img_type = page.evaluate(
                """
            async (img) => {
                const src = img.src;
                if (!src) return [null, null];
                const blob = await fetch(src).then(r => r.blob());
                const buf = await blob.arrayBuffer();
                return [Array.from(new Uint8Array(buf)), blob.type];
            }
            """,
                img,
            )
            if img_data:
                ext = img_type.split("/")[-1] if img_type else "png"
                file_name = f"image_{uuid4().hex}.{ext}"
                with open(users_files / file_name, "wb") as f:
                    f.write(bytes(img_data))
                logger.success(f"Save file: {file_name}")

        prefix = ["/popular-in"]
        match = re.search(r"https?://([^/]+)/?", page.url)
        base_domain = match.group(1) if match else ""
        links = page.query_selector_all("a")

        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            blocked = any(re.search(p, href) for p in prefix)
            if blocked:
                continue
            full_url = urljoin(page.url, href)
            if base_domain not in full_url:
                continue

            if any(
                full_url.lower().endswith(ext)
                for ext in (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".webp",
                    ".svg",
                    ".mp4",
                    ".webm",
                    ".mkv",
                    ".ogg",
                    ".mov",
                )
            ):
                logger.info(f"User: {name}")
                try:
                    data = requests.get(full_url).content
                    filename = full_url.split("/")[-1] or f"media_{uuid4().hex}"
                    with open(users_files / filename, "wb") as f:
                        f.write(data)
                    logger.success(f"Save file: {filename}")
                except Exception as e:
                    logger.error(f"<red>Error</red>: {full_url}\n {e}")


# decode files
class Instructions_Code:
    def minified_code(self, name, script):
        file_path = Path(__file__).parent / "users_file" / name / script
        file_name = file_path.name
        file_without_ext = file_path.suffix

        # formattable minified js file
        if file_without_ext == ".js":
            with open(file_path, "r+", encoding="utf-8") as f:
                js_code = f.read()
                beautified = jsbeautifier.beautify(js_code)
                f.seek(0)
                f.write(beautified)
                f.truncate()
        else:
            return None

    def beautifier_code(self, name, script):
        one_file_path = Path(__file__).parent / "users_file" / name / script
        file_name = one_file_path.name
        two_file_name = Path(__file__).parent / "users_file" / name / "webcrack"
        file_without_ext = one_file_path.suffix

        # formattable beautifier js file
        if file_without_ext == ".js":
            with open(one_file_path, "r+", encoding="utf-8") as f:
                result = subprocess.run(
                    [
                        "npx.cmd",
                        "webcrack",
                        str(one_file_path),
                        "-o",
                        str(two_file_name),
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    files_dir = Path(__file__).parent / "users_file" / name

                    for item in two_file_name.rglob("*"):
                        if item.is_file():
                            shutil.move(str(item), str(files_dir / item.name))

                    shutil.rmtree(two_file_name)
        else:
            return None
