from playwright.sync_api import Page


class LoginPage:

    URL = "http://127.0.0.1:5002"

    def __init__(self, page: Page):
        self.page = page

    def navigate(self) -> None:
        self.page.goto(f"{self.URL}/login")

    def fill_username(self, user) -> None:
        self.page.get_by_label("Pseudo").fill(user)

    def fill_password(self, password) -> None:
        self.page.get_by_test_id("input-password").fill(password)

    def submit(self):
        self.page.locator("[data-testid='btn-login']").click()

    def login(self, user, password) -> None:
        self.fill_username(user)
        self.fill_password(password)
        self.submit()
