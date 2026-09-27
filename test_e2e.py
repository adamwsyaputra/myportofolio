import os
import sys
import django
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
USER_PASSWORD = os.getenv("E2E_USER_PASSWORD")
ADMIN_PASSWORD = os.getenv("E2E_ADMIN_PASSWORD")
if not USER_PASSWORD or not ADMIN_PASSWORD:
    sys.exit("E2E_USER_PASSWORD and E2E_ADMIN_PASSWORD are not set in your .env file.")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portofolio.settings")
django.setup()

from django.contrib.auth.models import User

def setup_users():
    user, _ = User.objects.get_or_create(username="burhan_test")
    user.set_password(USER_PASSWORD)
    user.is_superuser = False
    user.is_staff = False
    user.save()

    admin, _ = User.objects.get_or_create(username="admin_test")
    admin.set_password(ADMIN_PASSWORD)
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()

def main():
    setup_users()
    options = webdriver.ChromeOptions()
    if "--headless" in sys.argv:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    base_url = "http://127.0.0.1:8000"
    try:
        # 1. Verify CSRF token on login form
        try:
            driver.get(f"{base_url}/login/")
        except Exception:
            print(f"Server is not running at {base_url}. Run 'python manage.py runserver' first.")
            return

        csrf = wait.until(
            EC.presence_of_element_located((By.NAME, "csrfmiddlewaretoken"))
        )
        assert csrf.get_attribute("value")
        assert driver.get_cookie("csrftoken")
        print("[PASS] CSRF token and cookie verified")

        # 2. Verify regular user login and session cookies
        driver.find_element(By.NAME, "username").send_keys("burhan_test")
        driver.find_element(By.NAME, "password").send_keys(USER_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        wait.until(EC.url_to_be(f"{base_url}/"))
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "nav-user")))
        assert driver.get_cookie("sessionid")
        assert driver.get_cookie("last_login")
        assert "Sesi Terakhir Login" in driver.page_source or "Last Login" in driver.page_source
        print("[PASS] Regular user login and session cookies verified")

        # 3. Verify regular user cannot access add project page
        driver.get(f"{base_url}/projects/add/")
        assert "403" in driver.title or "Forbidden" in driver.page_source
        print("[PASS] Regular user authorization restricted (403)")

        # 4. Verify superuser can access add project page
        driver.get(f"{base_url}/logout/")
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/login/')]")))
        driver.get(f"{base_url}/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("admin_test")
        driver.find_element(By.NAME, "password").send_keys(ADMIN_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        wait.until(EC.url_to_be(f"{base_url}/"))
        wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "nav-user"), "admin_test"))

        driver.get(f"{base_url}/projects/add/")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projectform")))
        print("[PASS] Superuser access to project form verified")

        # 5. Verify logout and cookie cleanup
        driver.get(f"{base_url}/logout/")
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/login/')]")))
        cookie_last_login = driver.get_cookie("last_login")
        assert cookie_last_login is None or cookie_last_login["value"] == ""
        print("[PASS] Logout and cookie cleanup verified")

        print("\nAll E2E tests passed successfully!")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
