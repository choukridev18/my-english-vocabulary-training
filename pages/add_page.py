from playwright.sync_api import Page


class AddPage:
    URL = "http://127.0.0.1:5002"

    def __init__(self, page: Page):
        self.page = page

    def navigate(self) -> None:
        self.page.goto(f"{self.URL}/add")

    def fill_english_word(self, word) -> None:
        self.page.get_by_label("Mot en anglais").fill(word)

    def fill_french_translation(self, trans) -> None:
        self.page.get_by_label("Traduction en français").fill(trans)

    def submit(self) -> None:
        self.page.locator("[data-testid='btn-add']").click()

    def add(self, word, trans) -> None:
        self.fill_english_word(word)
        self.fill_french_translation(trans)
        self.submit()

    def delete_word(self, word) -> None:
        self.page.locator(".word-row").filter(has_text=word).get_by_role(
            "button"
        ).click()

    def confirm_delete(self) -> None:
        self.page.locator("#modal-confirm").click()

    def cancel_delete(self) -> None:
        self.page.locator("#modal-cancel").click()
