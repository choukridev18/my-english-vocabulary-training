from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


def test_connexion(page: Page, app_url):
    """Se connecter avec des identifiants valides"""
    login_page = LoginPage(page)
    login_page.navigate()
    expect(page).to_have_url(f"{app_url}/login")
    login_page.fill_username("testuser")
    login_page.fill_password("test1234!")
    login_page.submit()
    expect(page).to_have_url(f"{app_url}/")


def test_connexion_password_wrong(page: Page, app_url):
    """Se connecter avec un mot de passe invalide"""
    login_page = LoginPage(page)
    login_page.navigate()
    expect(page).to_have_url(f"{app_url}/login")
    login_page.fill_username("testuser")
    login_page.fill_password("mauvais")
    login_page.submit()
    expect(page.locator(".alert.alert-error")).to_be_visible()


def test_register_succes(page: Page, new_user, app_url):
    """S'inscrire avec des informations valides"""
    register_page = RegisterPage(page)
    register_page.navigate()
    expect(page).to_have_url(f"{app_url}/register")
    register_page.fill_pseudo(new_user)
    register_page.fill_email("test@test.fr")
    register_page.fill_password("test1234!")
    register_page.fill_confirm_password("test1234!")
    register_page.submit()
    expect(page).to_have_url(f"{app_url}/")


def test_register_with_wrong_confirm(page: Page, app_url):
    """Inscription échouée avec mauvaise confirmation de mot de passe"""
    register_page = RegisterPage(page)
    register_page.navigate()
    expect(page).to_have_url(f"{app_url}/register")
    register_page.fill_pseudo("user")
    register_page.fill_email("test@test.com")
    register_page.fill_password("test1234!")
    register_page.fill_confirm_password("test1234")
    register_page.submit()
    expect(page.locator(".alert.alert-error")).to_be_visible()
