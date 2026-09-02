from playwright.sync_api import Page, expect
from pages.list_page import ListPage
from pages.add_page import AddPage


def test_search_word(login_in_page, new_word):
    """Rechercher un mot"""
    add_word = AddPage(login_in_page)
    add_word.navigate()
    add_word.fill_english_word(new_word)
    add_word.fill_french_translation("mot_test")
    add_word.submit()
    expect(login_in_page.locator("#add-success")).to_be_visible()
    list_page = ListPage(login_in_page)
    list_page.navigate()
    list_page.search_a_word(new_word)
    expect(
        login_in_page.locator(".word-table-row").filter(has_text=new_word)
    ).to_be_visible()


def test_toggle_mastered(login_in_page, new_word):
    """Cocher un mot comme maitrisé"""
    add_word = AddPage(login_in_page)
    add_word.navigate()
    add_word.fill_english_word(new_word)
    add_word.fill_french_translation("mot_test")
    add_word.submit()
    expect(login_in_page.locator("#add-success")).to_be_visible()
    list_page = ListPage(login_in_page)
    list_page.navigate()
    list_page.toggle_mastered(new_word)
    expect(
        login_in_page.locator(".word-table-row.row-mastered").filter(has_text=new_word)
    ).to_be_visible()


def test_definition_link(login_in_page, new_word):
    """Cliquer sur la definition d'un mot"""
    add_word = AddPage(login_in_page)
    add_word.navigate()
    add_word.fill_english_word(new_word)
    add_word.fill_french_translation("mot_test")
    add_word.submit()
    expect(login_in_page.locator("#add-success")).to_be_visible()
    list_page = ListPage(login_in_page)
    list_page.navigate()
    list_page.click_definition(new_word)
    link = (
        login_in_page.locator(".word-table-row")
        .filter(has_text=new_word)
        .locator(".def-link")
    )
    expect(link).to_have_attribute(
        "href", f"https://www.larousse.fr/dictionnaires/anglais-francais/{new_word}"
    )
