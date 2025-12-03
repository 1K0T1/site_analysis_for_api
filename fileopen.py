from pathlib import Path
import zipfile

from create_instructions_and_API import Instructions_API


# показать список файлов у клиента
class Open_List:
    def list_file(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        files = []

        for file in users_files.iterdir():
            if file.is_file():
                file_name = file.name
                files.append(file_name)
        return files


# показать содержимое файла
class Open_File:
    def view_file(self, name, filename):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        full_path = users_files / filename

        text_suffix = [
            ".txt",
            ".py",
            ".json",
            ".js",
            ".mjs",
            ".html",
            ".htm",
            ".css",
            ".csv",
            ".md",
            ".com",
            ".m3u8",
            ".c",
            ".cpp",
            ".php",
            ".jsx",
            ".tsx",
            ".svelte",
            ".vue",
        ]

        media_suffix = [
            ".mpeg",
            ".png",
            ".jpg",
            ".jpeg",
            ".webm",
            ".webp",
            ".mp3",
            ".wav",
            ".ogg",
            ".aac",
            ".mp4",
            ".ico",
            ".gif",
            ".avif",
            ".svg",
            ".bmp",
            ".ogv",
        ]

        if full_path.suffix.lower() in text_suffix:
            file_view = full_path.read_text(encoding="utf-8", errors="replace")
            return file_view
        elif full_path.suffix.lower() in media_suffix:
            return full_path
        else:
            return "Этот файл нельзя прочитать :/"


# создание zip
class Download_File:

    # создание zip html
    def html_download(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        zip_folder = users_files / "dfile"
        zip_folder.mkdir(parents=True, exist_ok=True)
        zip_path = zip_folder / "html.zip"

        if zip_path.is_file():
            return zip_path

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in users_files.glob("*.html"):
                zipf.write(file, arcname=file.name)
        return zip_path

    # создание zip js
    def js_download(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        zip_folder = users_files / "dfile"
        zip_folder.mkdir(parents=True, exist_ok=True)
        zip_path = zip_folder / "js.zip"

        if zip_path.is_file():
            return zip_path

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in users_files.glob("*.js"):
                zipf.write(file, arcname=file.name)
        return zip_path

    # создание txt links
    def link_download(self, link, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        txt_path = users_files / "links.txt"

        if txt_path.is_file():
            return txt_path

        links = Instructions_API().all_links(link, name)
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write("\n".join(links) + "\n")
        return txt_path

    def loading_link(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        txt_path = users_files / "links.txt"

        if txt_path.is_file():
            return txt_path

        return None


class Download_All:

    def download_all_file(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        all_files_folder = users_files / "dfile"
        all_files_folder.mkdir(parents=True, exist_ok=True)
        zip_path = all_files_folder / "all.zip"

        if zip_path.is_file():
            return zip_path

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in users_files.iterdir():
                if file.is_file():
                    zipf.write(file, arcname=file.name)
        return zip_path

    def load_all_files(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        all_files_folder = users_files / "dfile"
        all_files_folder.mkdir(parents=True, exist_ok=True)
        zip_path = all_files_folder / "all.zip"

        if zip_path.is_file():
            return zip_path
        return None


class AiGenerate:

    def sort_links(self, name, links):
        users_files = Path(__file__).parent / "users_file" / name
        uploads = Path(__file__).parent / users_files / "uploads"
        uploads.mkdir(parents=True, exist_ok=True)
        with open(links, "r+", encoding="utf-8") as f:
            lines = f.readlines()

        lines = list(dict.fromkeys(lines))
        return lines
