import yagmail

class Restore_account:
    def __init__(self, gmail, url):
       self.gmail = gmail
       self.url = url
    
    def restore_password(self):
        password_app = "your password app"
        gmail_app = "your gmail"
        
        yag = yagmail.SMTP(gmail_app, password_app)
        
        yag.send(
        to=f"{self.gmail}",
        subject="Восстановить пароль",
        contents=f"Ссылка что бы востоновить: {self.url}"
        )