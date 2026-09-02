from playwright.sync_api import Page, expect
from pages.add_page import AddPage


def test_add_word(app_url, login_in_page, new_word):
    """Ajouter un mot"""
    add_page = AddPage(login_in_page)
    add_page.navigate()
    add_page.fill_english_word(new_word)
    add_page.fill_french_translation("mot_test")
    add_page.submit()
    expect(login_in_page.locator("#add-success")).to_be_visible()


def test_delete_word(app_url, login_in_page, new_word):
    """supprimer un mot"""
    add_page = AddPage(login_in_page)
    add_page.navigate()
    add_page.fill_english_word(new_word)
    add_page.fill_french_translation("mot_test")
    add_page.submit()
    expect(login_in_page.locator("#add-success")).to_be_visible()
    add_page.delete_word(new_word)
    add_page.confirm_delete()
    expect(login_in_page.locator("#delete-success")).to_be_visible()
