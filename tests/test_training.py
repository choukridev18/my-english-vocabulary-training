from playwright.sync_api import Page, expect
from pages.training_page import TrainingPage
from pages.add_page import AddPage


def test_start_training(login_in_page, new_word):
    add_word = AddPage(login_in_page)
    add_word.navigate()
    add_word.fill_english_word(new_word)
    add_word.fill_french_translation("mot_test")
    add_word.submit()
    training = TrainingPage(login_in_page)
    training.navigate()
    training.select_mode("continuous")
    training.select_type("fr-en")
    training.start_training()
    expect(login_in_page.locator("[data-testid='question-word']")).to_be_visible()
