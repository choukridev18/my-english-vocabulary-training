from playwright.sync_api import Page


class ListPage:

    URL = "http://127.0.0.1:5002"

    def __init__(self, page: Page):
        self.page = page

    def navigate(self) -> None:
        self.page.goto(f"{self.URL}/list")

    def search_a_word(self, word) -> None:
        self.page.locator("#search-input").fill(word)

    def click_stats(self) -> None:
        self.page.locator("[data-testid='btn-brain']").click()

    def toggle_mastered(self, word) -> None:
        self.page.locator(".word-table-row").filter(has_text=word).locator(
            ".master-label"
        ).click()

    def click_definition(self, word) -> None:
        self.page.locator(".word-table-row").filter(has_text=word).locator(
            ".def-link"
        ).click()

    def delete(self, word) -> None:
        self.page.locator(".word-table-row").filter(has_text=word).locator(
            ".btn-delete-list"
        ).click()
