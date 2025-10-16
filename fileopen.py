from pathlib import Path
import zipfile

from create_instructions_and_API import Instructions_API

class Open_List():
    def list_file(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        files = []
        for file in users_files.iterdir():
            if file.is_file():
                file_name = file.name
                files.append(file_name)
        return files

class Open_File():
    def view_file(self, name, name_file):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        full_path = users_files / name_file
        file_view = full_path.read_text(encoding = "utf-8", errors = "raplace")
        return file_view

# создание zip 
class Download_File():
    
    # создание zip html
    def html_download(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        zip_folder = users_files / "dfile"
        zip_folder.mkdir(parents=True, exist_ok=True)
        zip_path = zip_folder / "html.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in users_files.glob("*.html"):
                zipf.write(file, arcname=file.name)
        print(f"Архив создан {zip_path}")
        return zip_path
    
    # создание zip js
    def js_download(self, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        zip_folder = users_files / "dfile"
        zip_folder.mkdir(parents=True, exist_ok=True)
        zip_path = zip_folder / "js.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in users_files.glob("*.js"):
                zipf.write(file, arcname=file.name)
        print(f"Архив создан {zip_path}")
        return zip_path
    
    # создание txt links
    def link_download(self, link, name):
        users_files = Path(__file__).parent / "users_file" / name
        users_files.mkdir(parents=True, exist_ok=True)
        txt_folder = users_files / "dfile"
        txt_folder.mkdir(parents=True, exist_ok=True)
        txt_path = txt_folder / "links.txt"
        links = Instructions_API().all_links(link, name)
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write("\n".join(links) + "\n")
        return txt_path