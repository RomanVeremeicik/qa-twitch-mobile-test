# pages/twitch_home_page.py
import time
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

class TwitchHomePage:
    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- LOCATORS ----------
    COOKIES_ACCEPT = (By.XPATH, "//button[contains(., 'Accept') or contains(., 'Accept All') or contains(., 'Принять')]")
    APP_MODAL = (By.CSS_SELECTOR, "[data-test-selector='open-app-modal'], .open-app-modal, .app-modal, .open-app")
    APP_MODAL_CLOSE_BUTTON = (By.XPATH, "//button[contains(., 'No thanks') or contains(., 'Continue to website') or contains(., 'Continue') or @aria-label='Close']")
    SEARCH_ICON = (By.CSS_SELECTOR, "button[aria-label*='Search'], button[data-a-target*='search'], button[data-test-selector*='search']")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search'], input[data-a-target='search-input'], input[data-a-target='tw-input'], input[placeholder*='Search']")
    # fallback selectors for stream cards / results
    STREAM_LIST_ITEMS = [
        (By.CSS_SELECTOR, "a[data-test-selector='preview-card-title-link']"),
        (By.CSS_SELECTOR, "a[data-test-selector='search-result-link']"),
        (By.CSS_SELECTOR, "a[href*='/videos/']"),
        (By.CSS_SELECTOR, "a[href*='/channel/']"),
        (By.CSS_SELECTOR, "a[href^='/']")
    ]

    # ---------- STEPS ----------
    def go_to_twitch(self, url="https://www.twitch.tv/"):
        """A. Open Twitch homepage."""
        self.driver.get(url)
        try:
            self.wait.until(lambda d: d.execute_script("return document.readyState") in ("interactive", "complete"))
        except TimeoutException:
            pass
        time.sleep(0.8)

    def handle_cookies(self):
        """B. Close cookies modal (Accept)."""
        try:
            btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(self.COOKIES_ACCEPT))
            try:
                btn.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.3)
            return True
        except TimeoutException:
            return False
        except Exception:
            return False

    def handle_app_modal(self):
        """C. Close 'Download app' modal — try buttons, cross, then JS remove as last resort."""
        try:
            # if not present quickly — return
            try:
                WebDriverWait(self.driver, 1).until(EC.invisibility_of_element_located(self.APP_MODAL))
                return False
            except TimeoutException:
                pass

            # try explicit button
            try:
                btn = WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable(self.APP_MODAL_CLOSE_BUTTON))
                try:
                    btn.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.3)
                return True
            except TimeoutException:
                pass

            # try generic close X
            try:
                close = self.driver.find_element(By.CSS_SELECTOR, ".open-app-modal .close, .app-modal .close, button[aria-label='Close']")
                try:
                    close.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", close)
                time.sleep(0.2)
                return True
            except Exception:
                pass

            # last resort: remove via JS
            self.driver.execute_script("""
            var s = document.querySelector('[data-test-selector="open-app-modal"]') ||
                    document.querySelector('.open-app-modal') ||
                    document.querySelector('.app-modal') ||
                    document.querySelector('.open-app');
            if (s) { s.remove(); }
            """)
            time.sleep(0.25)
            return True
        except Exception:
            # dump for debugging
            try:
                self.driver.save_screenshot("debug_app_modal_failed.png")
                with open("debug_page_source_app_modal.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except Exception:
                pass
            return False

    def search_for_game(self, query: str):
        """D. Click search icon and input query; fallback to direct search URL."""
        try:
            icon = WebDriverWait(self.driver, 6).until(EC.element_to_be_clickable(self.SEARCH_ICON))
            try:
                icon.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", icon)
        except TimeoutException:
            return self._direct_search_url(query)

        # wait for input
        try:
            input_el = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.SEARCH_INPUT))
            input_el.clear()
            input_el.send_keys(query)
            input_el.send_keys("\n")
            time.sleep(1.0)
            return True
        except TimeoutException:
            return self._direct_search_url(query)
        except Exception:
            return self._direct_search_url(query)

    def _direct_search_url(self, query: str):
        q = urllib.parse.quote_plus(query)
        url = f"https://www.twitch.tv/search?term={q}"
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 6).until(lambda d: "search" in d.current_url.lower() or d.execute_script("return document.readyState") == "complete")
        except Exception:
            pass
        time.sleep(1)
        return True

    def scroll_down(self, times: int = 2, pause: float = 1.0):
        """E. Scroll page down `times` times to load more streams."""
        for i in range(times):
            try:
                self.driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
            except Exception:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)

    def click_first_streamer(self):
        """F. Click first streamer from results (tries multiple candidate selectors)."""
        for locator in self.STREAM_LIST_ITEMS:
            try:
                elems = self.driver.find_elements(*locator)
                if elems:
                    for el in elems:
                        try:
                            if el.is_displayed():
                                try:
                                    el.click()
                                except Exception:
                                    self.driver.execute_script("arguments[0].click();", el)
                                time.sleep(1)
                                return True
                        except Exception:
                            continue
            except Exception:
                continue

        # if failed, dump for debugging
        try:
            self.driver.save_screenshot("debug_click_first_streamer_failed.png")
            with open("debug_page_source_click_first.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception:
            pass
        return False

