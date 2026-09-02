from playwright.sync_api import Page


class TrainingPage:
    URL = "http://127.0.0.1:5002"

    def __init__(self, page: Page):
        self.page = page

    def navigate(self) -> None:
        self.page.goto(f"{self.URL}/training")

    def select_mode(self, mode) -> None:
        self.page.locator(f"[data-testid='mode-{mode}']").click()

    def select_type(self, type) -> None:
        self.page.locator(f"[data-testid='type-{type}']").click()

    def start_training(self) -> None:
        self.page.locator("#btn-start").click()

    def submit_answer(self, answer) -> None:
        self.page.locator("#answer-input").fill(answer)
        self.page.locator("[data-testid='btn-validate']").click()
