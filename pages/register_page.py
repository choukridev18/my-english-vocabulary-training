from playwright.sync_api import Page


class RegisterPage:
    URL = "http://127.0.0.1:5002"

    def __init__(self, page: Page):
        self.page = page

    def navigate(self) -> None:
        self.page.goto(f"{self.URL}/register")

    def fill_pseudo(self, pseudo) -> None:
        self.page.get_by_label("Pseudo").fill(pseudo)

    def fill_email(self, email) -> None:
        self.page.get_by_label("Adresse email").fill(email)

    def fill_password(self, password) -> None:
        self.page.locator("#password").fill(password)

    def fill_confirm_password(self, confirm) -> None:
        self.page.locator("#confirm").fill(confirm)

    def submit(self):
        self.page.locator("[data-testid='btn-register']").click()

    def register(self, pseudo, email, password, confirm) -> None:
        self.fill_pseudo(pseudo)
        self.fill_email(email)
        self.fill_password(password)
        self.fill_confirm_password(confirm)
        self.submit()
