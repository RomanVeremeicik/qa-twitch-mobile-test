# pages/twitch_streamer_page.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TwitchStreamerPage:
    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    STREAMER_NAME = (By.CSS_SELECTOR, "h1, [data-a-target='stream-title'], .channel-info__username")
    STREAM_PLAYER = (By.CSS_SELECTOR, "video, .video-player__container, [data-a-player-state]")

    def wait_for_stream(self, timeout=12):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(self.STREAM_PLAYER))
            time.sleep(1)
            return True
        except Exception:
            return False

    def get_streamer_name(self):
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.STREAMER_NAME))
            return el.text.strip()
        except Exception:
            try:
                return self.driver.title or ""
            except Exception:
                return ""
