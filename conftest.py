import pytest
import sqlite3
from playwright.sync_api import Page


BASE_URL = "http://127.0.0.1:5002"


@pytest.fixture
def app_url():
    return BASE_URL


@pytest.fixture
def login_in_page(page: Page, app_url):
    page.goto(f"{app_url}/login")
    page.locator("#username").fill("testuser")
    page.locator("#password").fill("test1234!")
    page.get_by_role("button", name="🔑 Se connecter").click()
    return page


@pytest.fixture
def new_user():
    username = "test_register"
    yield username
    conn = sqlite3.connect("app/vocabulary.db")
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()


@pytest.fixture
def new_word():
    word = "testword"
    yield word
    conn = sqlite3.connect("app/vocabulary.db")
    conn.execute("DELETE FROM words WHERE english = ?", (word,))
    conn.commit()
    conn.close()
