import os
import platform
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchFrameException
import time


class AssessmentUICommon:

    def __init__(self):
        self.delay = 120
        self.os_name = platform.system()
        self.driver = None
        self.wait = None
        print(f"UI Code Version: Latest | OS: {self.os_name}")

    def initiate_browser(self, url):
        chrome_options = Options()

        # Auto allow mic/camera (VET / WebRTC)
        chrome_options.add_argument("--use-fake-ui-for-media-stream")

        # Stability & speed
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_experimental_option("detach", True)

        # 🚀 Selenium Manager handles driver automatically
        self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.get(url)
        self.driver.maximize_window()

        # REQUIRED for your login code
        self.wait = WebDriverWait(self.driver, 10)

        # Safe window handling
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])

        return self.driver

    def ui_login_to_test(self, user_name, password, reload_first=False):
        """
        Login on the assessment login page. If you already opened the URL and entered
        values then reloaded (or want a clean form), pass reload_first=True to refresh
        once before filling — avoids stale Angular state and stubborn prefilled fields.
        """
        if reload_first:
            self.driver.refresh()
            time.sleep(1)

        # Username — wait again after refresh
        user_input = self.wait.until(
            EC.visibility_of_element_located((By.NAME, 'loginUsername'))
        )
        user_input.click()
        user_input.send_keys(Keys.CONTROL + 'a')
        user_input.send_keys(Keys.BACKSPACE)
        user_input.send_keys(user_name)

        # Password — Ctrl+A + Backspace clears better than .clear() on some Angular inputs
        user_pass = self.wait.until(
            EC.visibility_of_element_located((By.NAME, 'loginPassword'))
        )
        user_pass.click()
        user_pass.send_keys(Keys.CONTROL + 'a')
        user_pass.send_keys(Keys.BACKSPACE)
        user_pass.send_keys(password)

        # ✅ WAIT for Angular block UI to disappear (longer — overlay often blocks click)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, "block-ui-overlay")
                )
            )
        except TimeoutException:
            pass  # overlay might not appear every time

        # ✅ WAIT for button to be CLICKABLE — use longer wait; page can be slow after send_keys
        login_wait = WebDriverWait(self.driver, 30)
        try:
            login_btn = login_wait.until(
                EC.element_to_be_clickable((By.NAME, 'btnLogin'))
            )
        except TimeoutException:
            # Fallback: button may exist but stay "not clickable" due to overlay/CSS; try JS click
            try:
                login_btn = self.driver.find_element(By.NAME, 'btnLogin')
            except Exception:
                # Help debug: URL + screenshot
                try:
                    print("Login timeout — current URL:", self.driver.current_url)
                    self.driver.save_screenshot("login_btn_timeout.png")
                except Exception:
                    pass
                raise
        # Extra safety for Chrome 143+
        self.driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
        self.driver.execute_script("arguments[0].click();", login_btn)



        try:
            error_xpath = '//div[contains(@class,"login-error")]'
            error_element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, error_xpath))
            )
            login_status = error_element.text
        except TimeoutException:
            pass
        login_status = "SUCCESS"

        return login_status

    # CRPO authoring helpers (reusable across UI scripts)
    def crpo_ui_login(self, login_url, username, password, timeout=15):
        """Log in to CRPO UI and fail with useful diagnostics if login blocks."""
        self.driver.get(login_url)
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((By.NAME, "loginName")))
        self.driver.find_element(By.NAME, "loginName").clear()
        self.driver.find_element(By.NAME, "loginName").send_keys(username)
        self.driver.find_element(By.XPATH, "//input[@type='password']").clear()
        self.driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
        login_btn = self.driver.find_element(
            By.XPATH, "//*[@class = 'btn btn-default button_style login ng-binding']"
        )
        try:
            login_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", login_btn)

        # Successful path: leave /login/ URL.
        try:
            wait.until(lambda d: "/login/" not in d.current_url)
        except TimeoutException as e:
            # Failed path: stay on login page, usually with .login-error text.
            err_text = ""
            try:
                err = self.driver.find_element(By.CSS_SELECTOR, "div.login-error")
                err_text = (err.text or "").strip()
            except Exception:
                pass
            current = self.driver.current_url
            msg = (
                f"CRPO login timed out. Current URL: {current}. "
                f"Login error: {err_text or 'not visible'}"
            )
            raise TimeoutException(msg) from e
        time.sleep(0.5)

    def wait_for_page_ready(self, timeout=60):
        """Wait for common dw-loading-active overlay to disappear if present."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            if self.driver.find_elements(By.CLASS_NAME, "dw-loading-active"):
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
        except Exception:
            pass

    def open_authoring_section(self):
        """Open Authoring menu from CRPO home (click More if needed)."""
        wait = WebDriverWait(self.driver, 20)
        time.sleep(2)
        self.wait_for_page_ready(40)
        grid_locator = (By.XPATH, "//a[normalize-space()='Authoring']")
        grid_elements = self.driver.find_elements(*grid_locator)
        if grid_elements:
            grid_button = wait.until(EC.element_to_be_clickable(grid_locator))
        else:
            more_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='More']"))
            )
            self.driver.execute_script("arguments[0].click();", more_button)
            time.sleep(1)
            grid_button = wait.until(EC.element_to_be_clickable(grid_locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", grid_button)
        self.driver.execute_script("arguments[0].click();", grid_button)
        time.sleep(1.5)

    def open_authoring_questions_grid(self):
        """Open Questions tab inside Authoring section."""
        self.wait_for_page_ready(40)
        wait = WebDriverWait(self.driver, 20)
        questions = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@title='Questions']"))
        )
        self.driver.execute_script("arguments[0].click();", questions)
        self.wait_for_page_ready(60)

    def click_new_question(self):
        """Click New Question and wait for create page URL."""
        wait = WebDriverWait(self.driver, 30)
        xpath = "//a[contains(@ng-click, 'vm.create') and contains(., 'New Question')]"
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        wait.until(EC.url_contains("questions/create"))

    def select_i_agree(self):
        try:
            # time.sleep(1)
            i_agree_status = WebDriverWait(self.driver, self.delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'chk')))
            is_selected = i_agree_status.is_selected()
            if not is_selected:
                i_agree_status.click()
                is_selected = True
            return is_selected

        except Exception as e:
            print("I agree is not visible")
            print(e)

    # def focus_to_model_window(self):
    #     try:
    #         time.sleep(1)
    #         model_header = WebDriverWait(self.driver, self.delay).until(
    #             EC.presence_of_element_located((By.CLASS_NAME, 'dropdown')))
    #         # self.driver.find_element(By.XPATH, "//*[@class='modal-header']").click()
    #         model_header.click()
    #     except Exception as e:
    #         print("model window is not visible")
    #         print(e)

    def about_online_proctoring(self):
        # Use a local wait object for clarity
        wait = WebDriverWait(self.driver, 15)

        try:
            # 1. Wait for the loading overlay to disappear first
            # This is usually what blocks the 'I Agree' checkbox
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "block-ui-overlay")))

            # 2. Target the LABEL instead of the INPUT
            # In custom CSS, the <input> is often hidden and the <label> handles the click.
            i_agree_label = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(@class, 'custom-checkbox')]")
            ))

            # Use JavaScript click to ensure it bypasses any lingering invisible overlays
            self.driver.execute_script("arguments[0].click();", i_agree_label)

            # 3. Wait for the Next button to be ready
            next_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnProctorNext")))
            next_button.click()

            print("Successfully navigated through Proctoring screen.")

        except Exception as e:
            print(f"Online Proctoring step failed: {e}")
            # Optional: Save a screenshot to see what blocked it
            self.driver.save_screenshot("proctoring_error.png")

    def assessment_terms_and_conditions(self):
        try:
            time.sleep(5)
            i_agree_to_terms_and_conditions = self.driver.find_element(By.XPATH,
                                                                       "//span[text()='I agree to the Assessment Terms & Conditions above.']")
            i_agree_to_terms_and_conditions.click()
            i_fully_understand = self.driver.find_element(By.XPATH,
                                                          "//span[@class='txt-color-red' and contains(text(), 'if I am found to be engaged in any act of fraud')]")
            i_fully_understand.click()
            time.sleep(0.5)
            next_button = self.driver.find_element(By.XPATH, "//button[@name='btnProctorNext']").click()
        except Exception as e:
            print("Terms and conditions I agree is not visible")
            print(e)

    def selfie(self):
        try:
            print("Waiting for camera/selfie button...")
            # Use a long deadline (30s) but it will move instantly when ready
            selfie_btn = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Selfie')]"))
            )
            selfie_btn.click()
            time.sleep(10)

            # Wait for "Proceed" to become clickable (handles image processing time)
            proceed_xpath = "//span[contains(text(), 'Proceed to test')]"
            proceed_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, proceed_xpath)))
            proceed_btn.click()
            print("Selfie captured and proceeding.")
        except Exception as e:
            print(f"Selfie step failed: {e}")

    def remove_disabled_attribute(self):
            try:
                # 1. Use a partial class/text match to find the button safely
                # Most "Proceed" or "Next" buttons have these common classes
                button_xpath = "//button[contains(@class, 'btn-primary') and contains(@class, 'center-block')]"

                # 2. Wait until it's present in the DOM
                button = self.wait.until(EC.presence_of_element_located((By.XPATH, button_xpath)))

                # 3. Force remove the attribute and trigger a state change
                # Adding 'button.disabled = false' helps in frameworks like Angular
                self.driver.execute_script("""
                    arguments[0].removeAttribute('disabled');
                    arguments[0].disabled = false;
                    arguments[0].classList.remove('disabled');
                """, button)

                # 4. Verification
                is_disabled = button.get_attribute("disabled")
                print(f"Button enabled successfully. Disabled attribute is now: {is_disabled}")

            except Exception as e:
                print(f"Failed to enable button: {e}")

    def select_answer_for_the_question(self, answer):
        # This XPATH looks for a radio button with value 'A' OR
        # a label containing the text 'A' next to a radio button.
        xpath = f"//input[@name='answerOptions' and (@value='{answer}' or ..//text()='{answer}')]"

        try:
            # Increase timeout slightly for the first question (e.g., 10s)
            ans_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            if not ans_el.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ans_el)
                self.driver.execute_script("arguments[0].click();", ans_el)

        except Exception as e:
            print(f"TIMEOUT: Answer '{answer}' not found. Taking debug screenshot...")
            self.driver.save_screenshot(f"error_ans_{answer}.png")
            raise e
    #
    # def select_answer_for_fib_question(self, answer):
    #     if answer:
    #         value = "//input[@placeholder = 'Blank']"
    #         elem = self.driver.find_element(By.XPATH, value)
    #         self.driver.implicitly_wait(10)
    #         ActionChains(self.driver).move_to_element(elem).send_keys_to_element(elem, answer).perform()
    #     else:
    #         pass
    #     # time.sleep(1)
    #     # value = "//input[@placeholder = 'Blank']"
    #     # answered = self.driver.find_element(By.XPATH, value)
    #     # answered.send_keys(answer)
    #
    # def select_answer_for_mca_question(self, answer):
    #     # If user wants to select one or more options then If condition will work other wise else will pass the stmt.
    #     if answer:
    #         # user can choose n number of options, options be passed as string and comma separated
    #         # below split will split the string by using comma and will make a list.
    #         answer_choices = answer.split(',')
    #         for options in answer_choices:
    #             # strip is necessary to remove the leading and trailing space of each option.
    #             options = options.strip()
    #             # elem = self.driver.find_element_by_xpath('//*[@id="option2"]')
    #             value = '//*[@id="%s"]' % options
    #             # elem = self.driver.find_element_by_xpath(value)
    #             elem = self.driver.find_element(By.XPATH, value)
    #             self.driver.implicitly_wait(10)
    #             ActionChains(self.driver).move_to_element(elem).click(elem).perform()
    #     else:
    #         # User does not want to select any option, so pass the stmt.
    #         pass
    def select_answer_for_fib_question(self, answer):
        if not answer:
            return

        xpath = "//input[@placeholder='Blank']"
        try:
            # Wait up to 5s for the specific blank to be interactable
            elem = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            # Clear existing text first to avoid appending to default values
            elem.clear()
            elem.send_keys(answer)
        except Exception as e:
            print(f"FIB Error: Could not find or fill the blank. {e}")

    def select_answer_for_mca_question_old(self, answer):
        if not answer:
            return

        # Split and clean choices
        answer_choices = [opt.strip() for opt in answer.split(',')]

        for option_id in answer_choices:
            try:
                # Dynamically wait for EACH option in the list
                xpath = f"//*[@id='{option_id}']"
                elem = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )

                # Check if already selected (for MCA, clicking twice might unselect)
                if not elem.is_selected():
                    # ActionChains is useful here if the ID is on a hidden input
                    # but we need to click the styled overlay.
                    ActionChains(self.driver).move_to_element(elem).click().perform()

            except Exception as e:
                print(f"MCA Error: Option '{option_id}' not found or clickable. {e}")

    def select_answer_for_mca_question(self, answer):
        if not answer:
            return

        answer_choices = [ opt.strip() for opt in answer.split(',') ]

        for option_id in answer_choices:
            try:
                # Target LABEL (most stable)
                xpath = f"//input[@id='{option_id}']/ancestor::label"

                elem = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, xpath)))

                # Wait until Angular finishes rendering
                WebDriverWait(self.driver, 10).until(lambda d:elem.is_displayed() and elem.is_enabled())

                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)

                # Click via JS (bypasses overlay issues)
                self.driver.execute_script("arguments[0].click();", elem)

            except Exception as e:
                print(f"MCA Error: Option '{option_id}' failed. {e}")

    def check_answered_status(self, previous_answer):
        try:
            # Use a short 2-second timeout for status checks
            xpath = f"//input[@name='answerOptions' and @value='{previous_answer}']"
            element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            # .is_selected() tells you if the radio button is filled
            # .is_enabled() only tells you if it's not greyed out
            return element.is_selected()
        except Exception:
            return False

    # def next_question(self, question_index):
    #     button_name = f"btnQuestionIndex{question_index}"
    #     try:
    #         # This will proceed in 0.05s if the button is ready, or wait up to 5s if slow.
    #         btn = self.wait.until(EC.element_to_be_clickable((By.NAME, button_name)))
    #         btn.click()
    #     except Exception as e:
    #         print(f"Could not jump to question {question_index}: {e}")
    def next_question(self, question_index):
        button_name = f"btnQuestionIndex{question_index}"
        try:
            # We use a 5-second 'Micro-Wait' here instead of the global 15s.
            # This keeps the test suite 'snappy'.
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.NAME, button_name))
            )
            btn.click()

        except Exception as e:
            print(f"Could not jump to question {question_index} within 5s: {e}")


    def wait_for_question_to_load(self, expected_index, timeout=5):
        """
        Waits for the UI to visually confirm the question has changed.
        """
        try:
            # EXPERT TIP: Use an XPath that looks for the number anywhere
            # inside a header or a specific container to make it flexible.
            # This looks for any element containing the text "Question X"
            locator = (By.XPATH, f"//*[contains(text(), 'Question {expected_index}')]")

            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            # Fixed the missing parenthesis from your previous snippet
            print(f"Warning: UI did not confirm loading of question {expected_index}")
            return False

    # def start_test_button_status(self):
    #     try:
    #         # Use a short wait to ensure the button is at least in the DOM
    #         btn = self.wait.until(EC.presence_of_element_located((By.NAME, 'btnStartTest')))
    #
    #         # is_enabled() is the correct check for buttons
    #         if btn.is_enabled():
    #             return 'Enabled'
    #         return 'Disabled'
    #     except Exception:
    #         # If the button doesn't appear at all within the timeout
    #         return 'Not Found'
    def start_test_button_status(self):
        try:
            # We override the default wait with a 'fast' 2-second timeout
            btn = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.NAME, 'btnStartTest'))
            )

            # Optimization: Check both 'enabled' attribute and property
            if btn.is_enabled() and "disabled" not in (btn.get_attribute("class") or ""):
                return 'Enabled'
            return 'Disabled'
        except:
            return 'Not Found'

    # def start_test(self):
    #     try:
    #         # 1. Wait until the button is actually clickable (visible + enabled)
    #         start_btn = self.wait.until(EC.element_to_be_clickable((By.NAME, 'btnStartTest')))
    #         start_btn.click()
    #         print("Start Test clicked.")
    #
    #         # 2. INSTEAD OF SLEEP(5): Wait for a unique element on the NEXT page
    #         # This makes the script move the INSTANT the test loads.
    #         # Replace 'question-container' with an ID or Class found in the actual test.
    #         self.wait.until(EC.presence_of_element_located((By.ID, 'question-container')))
    #
    #     except Exception as e:
    #         print(f"Failed to start test or test page did not load: {e}
    def start_test(self):
        try:
            # 1. Capture the current URL or the button itself to track transition
            old_url = self.driver.current_url
            start_btn = self.wait.until(EC.element_to_be_clickable((By.NAME, 'btnStartTest')))

            # 2. Click the button
            start_btn.click()
            print("Start Test clicked, waiting for transition...")

            # 3. RELIABILITY BOOST: Wait until the URL actually changes
            # This ensures we have definitely left the 'Start' page.
            self.wait.until(EC.url_changes(old_url))

            # 4. SPEED BOOST: Wait for the key element on the new page
            self.wait.until(EC.presence_of_element_located((By.ID, 'question-container')))
            print("Test page loaded successfully.")

            return True

        except Exception as e:
            print(f"Error during start_test: {e}")
            return False

    # def check_security_key_model_window_availability(self):
    #     status = 'Success'
    #     try:
    #         if self.driver.find_element(By.NAME, 'securityKey').is_displayed():
    #             print("Security page is displayed")
    #             status = "Success"
    #     except Exception as e:
    #         print(e)
    #         status = 'Failed'
    #     return status
    #
    # def validate_security_key(self, secure_password):
    #     self.driver.find_element(By.NAME, 'securityKey').send_keys(secure_password)
    #     self.driver.find_element(By.XPATH, '//button[text()="Verify"]').click()
    #     time.sleep(3)
    def check_security_key_model_window_availability(self):
        try:
            # Use a short, specific wait (5s) for the security field to appear
            # This is better than find_element because it accounts for animation time
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.NAME, 'securityKey'))
            )
            print("Security modal is visible.")
            return 'Success'
        except Exception:
            print("Security modal not detected (might not be required for this test).")
            return 'Failed'

    def validate_security_key(self, secure_password):
        try:
            # 1. Find the input field
            key_input = self.wait.until(EC.element_to_be_clickable((By.NAME, 'securityKey')))
            key_input.clear()
            key_input.send_keys(secure_password)

            # 2. Click Verify - Using a more flexible XPATH to handle case sensitivity or extra spaces
            verify_xpath = "//button[contains(translate(text(), 'VERIFY', 'verify'), 'verify')]"
            self.driver.find_element(By.XPATH, verify_xpath).click()

            # 3. Instead of sleep(3), wait for the modal to DISAPPEAR
            # This confirms the key was accepted and the test is proceeding
            self.wait.until(EC.invisibility_of_element_located((By.NAME, 'securityKey')))
            print("Security key validated and modal closed.")

        except Exception as e:
            print(f"Error validating security key: {e}")
            raise e

    def end_test(self):
        # 1. Wait for the 'End Test' button using a partial class match (safer)
        # We look for the 'btn-danger' class which usually signifies the 'End' action
        end_btn_xpath = "//button[contains(@class, 'btn-danger') and contains(., 'End')]"

        try:
            end_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, end_btn_xpath)))
            end_btn.click()
            print("Initial 'End Test' clicked.")
        except Exception as e:
            print(f"Could not click initial End Test button: {e}")

    def end_test_confirmation(self):
        try:
            # 2. Instead of sleep(5), wait up to 10s for the confirmation button to be clickable
            # This will proceed the INSTANT the button appears
            confirm_btn = self.wait.until(EC.element_to_be_clickable((By.NAME, 'btnCloseTest')))
            confirm_btn.click()
            print("Test ended successfully and confirmation submitted.")

            # 3. Optional: Wait for the window to actually close or redirect
            # to ensure the next part of your script doesn't start too early
            self.wait.until(EC.staleness_of(confirm_btn))
            time.sleep(2)

        except Exception as e:
            print(f"Confirmation button 'btnCloseTest' not found: {e}")

    # def unanswer_question(self):
    #     self.driver.find_element(By.XPATH, "//button[@class='btn btn-default btnUnanswer ng-scope ng-isolate-scope']").click()
    #     time.sleep(0.3)
    #     print("Un Answer Succeded")
    #
    # def find_question_string(self):
    #     question_string = self.driver.find_element(By.NAME, 'questionHtmlString').text
    #     print(question_string)
    #     return question_string
    #
    # def find_question_string_v2(self):
    #     question_string = self.driver.find_element(By.NAME, 'questionHtmlString').text
    #     groupname = self.driver.find_element(By.NAME, 'groupName').text
    #     section_name = self.driver.find_element(By.NAME, 'sectionName').text
    #     return question_string, groupname, section_name
    #
    # def find_question_string_for_rtc(self):
    #     parent_question_string = self.driver.find_element(By.NAME, 'questionParentHtmlString').text
    #     child_question_string = self.driver.find_element(By.NAME, 'questionHtmlString').text
    #     groupname = self.driver.find_element(By.NAME, 'groupName').text
    #     section_name = self.driver.find_element(By.NAME, 'sectionName').text
    #     return parent_question_string, child_question_string, groupname, section_name

    def unanswer_question(self):
        try:
            # Use a more stable XPATH looking for the specific functional class
            xpath = "//button[contains(@class, 'btnUnanswer')]"
            unanswer_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            unanswer_btn.click()

            # Instead of sleep(0.3), wait for the radio buttons to actually clear
            # This is a 'fluent' way to ensure the action finished
            WebDriverWait(self.driver, 5).until(
                lambda d: not any(opt.is_selected() for opt in d.find_elements(By.NAME, 'answerOptions'))
            )
            print("Question un-answered successfully.")
        except Exception as e:
            print(f"Failed to un-answer: {e}")

    # def _get_safe_text(self, name_attribute):
    #     """Helper to ensure text is present and not empty before returning"""
    #     try:
    #         element = self.wait.until(EC.visibility_of_element_located((By.NAME, name_attribute)))
    #         return element.text.strip()
    #     except:
    #         return "NOT_FOUND"
    def _get_safe_text(self, name_attribute, timeout=3):
        """
        Helper with a shorter default timeout.
        If it's not visible in 3 seconds, it's likely not there.
        """
        try:
            # We override the global wait with a 'fast' local wait
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.NAME, name_attribute))
            )
            text = element.text.strip()

            # Expert Tip: Sometimes .text is empty if the element is an input
            if not text:
                text = element.get_attribute("value") or ""

            return text.strip()
        except:
            return "NOT_FOUND"

    def find_question_string(self):
        return self._get_safe_text('questionHtmlString')

    def find_question_string_v2(self):
        q_str = self._get_safe_text('questionHtmlString')
        group = self._get_safe_text('groupName')
        section = self._get_safe_text('sectionName')
        return q_str, group, section

    def find_question_string_for_rtc(self):
        # RTC (Reading Comprehension) often has a parent passage
        parent = self._get_safe_text('questionParentHtmlString')
        child = self._get_safe_text('questionHtmlString')
        group = self._get_safe_text('groupName')
        section = self._get_safe_text('sectionName')
        return parent, child, group, section

    def rejection_page(self):
        print("Checking Rejection Page...")
        # Default 'empty' data structure
        data = {
            'is_next_test_available': 'Not Available', 'is_shortlisted': 'Rejected',
            'message': 'EMPTY', 'consent_yes': 'EMPTY', 'consent_no': 'EMPTY',
            'consent_paragraph': 'EMPTY', 'next_test_page_message': 'EMPTY',
            'retest_required': False
        }

        try:
            # Use a short timeout to see if the message exists
            msg_el = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.NAME, 'nextTestMsg'))
            )
            data['message'] = msg_el.text

            # Avoid generic ng-scope; look for the main container or body
            data['next_test_page_message'] = self.driver.find_element(By.TAG_NAME, 'body').text

        except Exception as e:
            print(f"Rejection element not found: {e}")
            data['is_next_test_available'] = 'EXCEPTION'

        return data

    def shortlisting_page(self):
        print("Processing Shortlisting/Chaining Logic...")
        data = {}

        try:
            # 1. Wait for the primary button to determine the state
            # Using a 10s wait instead of implicit wait saves time
            btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'btnStartNextTest'))
            )

            btn_text = btn.text.strip()
            overall_msg = self.driver.find_element(By.TAG_NAME, "body").text

            # 2. Extract common message element if it exists
            try:
                next_test_msg = self.driver.find_element(By.NAME, 'nextTestMsg').text
            except:
                next_test_msg = "EMPTY"

            # 3. Decision Logic based on Button Text
            if btn_text == 'Yes, Request for Retest':
                data = self._create_data_dict(available='Not Available', status='Retest Case',
                                              msg='RETEST', overall=overall_msg, retest=True)

            elif btn_text == 'Yes, Take me to the next test':
                # This is a Consent Case
                consent_para = self.driver.find_element(By.CLASS_NAME, "next-msg").text
                c_yes = self.driver.find_element(By.CLASS_NAME, "btn-yes").text
                c_no = self.driver.find_element(By.CLASS_NAME, "red-button").text

                data = self._create_data_dict(available='Available', status='Shortlisted with Consent',
                                              msg=next_test_msg, overall=overall_msg,
                                              yes=c_yes, no=c_no, para=consent_para)

            else:
                # Autotest or Standard Shortlist logic
                status = "Shortlisted"
                if "another test lined up" in next_test_msg:
                    status = "Autotest"

                data = self._create_data_dict(available='Available', status=status,
                                              msg=next_test_msg, overall=overall_msg)

        except Exception as e:
            print(f"Shortlisting detection failed: {e}")
            data = self._create_data_dict(available='EXCEPTION', status='EXCEPTION', msg=str(e))

        return data

    def _create_data_dict(self, available='EMPTY', status='EMPTY', msg='EMPTY',
                          yes='EMPTY', no='EMPTY', para='EMPTY', overall='EMPTY', retest=False):
        """Helper to maintain a consistent dictionary structure"""
        return {
            'is_next_test_available': available,
            'is_shortlisted': status,
            'message': msg,
            'consent_yes': yes,
            'consent_no': no,
            'consent_paragraph': para,
            'next_test_page_message': overall,
            'retest_required': retest
        }

    def start_next_test(self):
        old_handles = self.driver.window_handles


        # 3. Wait for the new window handle to appear (up to 10 seconds)
        # This replaces time.sleep(3) and is much faster/safer
        try:
            start_btn = self.wait.until(EC.element_to_be_clickable((By.NAME, 'btnStartNextTest')))
            start_btn.click()
            window_wait = WebDriverWait(self.driver, 20)
            try:
                window_wait.until(lambda d: len(d.window_handles) > len(old_handles))
            except:
                print("Standard click might have failed. Retrying with JavaScript click...")
                self.driver.execute_script("arguments[0].click();", start_btn)
                window_wait.until(lambda d: len(d.window_handles) > len(old_handles))
            new_handles = self.driver.window_handles
            self.driver.switch_to.window(new_handles[-1])
            # 5. Important: Give the new window a moment to 'exist' before the next command
            self.wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

            print(f"Successfully switched to window. Total windows: {len(new_handles)}")
        except Exception as e:
            print("CRITICAL: The next test window failed to open.")
            # Optional: Take a screenshot to see if an error popup appeared on screen
            self.driver.save_screenshot("chaining_error.png")
            raise e

    # def consent_no(self):
    #     self.driver.find_element(By.XPATH, "//*[@class='btn btn-default red-button']").click()
    #     time.sleep(3)
    #     self.driver.switch_to.window(self.driver.window_handles[2])
    def consent_no(self):
        try:
            # 1. Capture current handles before clicking
            existing_handles = self.driver.window_handles

            # 2. Find and click the 'No' button using a safer XPATH
            no_btn_xpath = "//button[contains(@class, 'red-button') or contains(., 'No')]"
            no_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, no_btn_xpath)))
            no_btn.click()
            print("Clicked 'No' for consent.")

            # 3. Wait for a NEW window to appear (up to 10 seconds)
            # This is much safer than sleep(3)
            self.wait.until(lambda d: len(d.window_handles) > len(existing_handles))

            # 4. Switch to the newest window (the last one in the list)
            new_handles = self.driver.window_handles
            self.driver.switch_to.window(new_handles[-1])

            print(f"Switched to new window. Title: {self.driver.title}")

        except Exception as e:
            print(f"Failed during consent_no window switch: {e}")
            # Optional: If the switch fails, you might want to stay on the current handle
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[-1])

    def vet_handle_cookie_banner(self):
        selectors = [
            (By.ID, "onetrust-accept-btn-handler"),
            (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept all')]"),
            (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]"),
            (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reject all')]"),
            (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'save choices')]"),
        ]

        # Try in both contexts: top page and VET iframe.
        contexts = [None, (By.ID, "thirdPartyIframe")]
        for frame_locator in contexts:
            try:
                self.driver.switch_to.default_content()
                if frame_locator:
                    WebDriverWait(self.driver, 5).until(
                        EC.frame_to_be_available_and_switch_to_it(frame_locator)
                    )

                for by, value in selectors:
                    try:
                        btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((by, value))
                        )
                        self.driver.execute_script("arguments[0].click();", btn)
                        print("Cookie/privacy banner handled.")
                        return
                    except Exception:
                        continue
            except Exception:
                continue
            finally:
                self.driver.switch_to.default_content()

        print("Cookie banner not found, proceeding...")

    def vet_start_test(self):
        # Default return values
        vet_test_started = "Failed"
        is_element_successful = False

        try:
            # 1. Use an explicit wait for the frame instead of time.sleep(5)
            wait = WebDriverWait(self.driver, 10)

            # This switches to the frame as soon as it's available
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'thirdPartyIframe')))
            self.vet_handle_cookie_banner()

            # 2. Find and click the button using the high-precision XPath
            # We wait for clickability to ensure the element is both present and visible

            selector = "//button[@data-testid='cade-base-button'][.//span[text()='Start']]"
            element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            element.click()
            # 3. Update status on success
            vet_test_started = "Successful"
            is_element_successful = True
            print("VET Test started successfully.")

        except (TimeoutException, NoSuchFrameException) as e:
            print(f"VET Start test failed: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            # Optional: Switch back to the main content if needed for subsequent steps
            # self.driver.switch_to.default_content()
            pass

        return vet_test_started, is_element_successful

    def vet_agreement(self):
        # Initialize return states
        vet_agreement_status = "Failed"
        is_element_successful = False

        try:
            # Clear OneTrust overlay if it appears before readiness actions.
           
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, 'thirdPartyIframe'))
            )

            # 1. Use an explicit wait (assumes we are already inside the correct iframe)
            wait = WebDriverWait(self.driver, 10)

            # 2. Target the checkbox via data-testid
            # Note: Checkboxes can sometimes be tricky; JS click is often more reliable for hidden inputs
            checkbox_selector = "input[data-testid='cade-checkbox']"
            checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, checkbox_selector)))

            # Select the checkbox if it's not already selected
            if not checkbox.is_selected():
                self.driver.execute_script("arguments[0].click();", checkbox)

            # 3. Target the "Next" button
            # We use the text-based XPath to ensure we hit the correct button label
            next_btn_selector = "//button[.//span[text()='Next'] and @data-testid='cade-base-button']"
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, next_btn_selector)))
            next_button.click()

            # 4. Success State
            vet_agreement_status = "Successful"
            is_element_successful = True
            print("Agreement accepted and 'Next' clicked successfully.")

        except TimeoutException:
            print("Timeout: Agreement checkbox or Next button not found/clickable.")
        except Exception as e:
            print(f"Error in vet_agreement: {e}")

        return vet_agreement_status, is_element_successful

    def vet_system_check(self):
        system_check_status = "Failed"
        is_successful = False

        try:
            # 1. Define the waiter (20-second timeout as requested)
            wait = WebDriverWait(self.driver, 20)

            # 2. Strategy: Wait specifically for the 'Next' button to be clickable.
            # This button only renders/becomes active once the DOM updates with 'ok' statuses.
            next_btn_selector = (By.ID, "cade-next-button")

            print("Waiting for system checks to complete...")
            next_button = wait.until(EC.element_to_be_clickable(next_btn_selector))

            # 3. Optional: Verify all 4 checks are 'ok' before clicking
            # This ensures we don't click a 'Next' button that might be present but disabled
            checks = self.driver.find_elements(By.CSS_SELECTOR, ".system-check-bar.ok")
            if len(checks) == 4:
                next_button.click()
                system_check_status = "Successful"
                is_successful = True
                print("System checks passed. Proceeding to next step.")
            else:
                print(f"Only {len(checks)}/4 checks passed.")

        except TimeoutException:
            print("System checks did not turn green within 20 seconds.")
        except Exception as e:
            print(f"Error during system check: {e}")

        return system_check_status, is_successful

    def vet_bandwidth_check(self):
        bandwidth_check_status = "Failed"
        is_successful = False

        try:
            # 1. Wait for the success message to appear in the status role
            # This confirms the backend check actually finished successfully.
            wait = WebDriverWait(self.driver, 30)  # Bandwidth checks can sometimes take longer
            success_msg_xpath = "//span[@role='text' and contains(text(), 'Bandwidth check is complete')]"

            print("Waiting for bandwidth check to complete...")
            wait.until(EC.visibility_of_element_located((By.XPATH, success_msg_xpath)))

            # 2. Click the 'Next' button
            # Using the ID is fastest, but we verify it's the one inside the success panel
            next_button = wait.until(EC.element_to_be_clickable((By.ID, "cade-next-button")))

            next_button.click()

            bandwidth_check_status = "Successful"
            is_successful = True
            print("Bandwidth check passed. Moving to Step 3.")

        except TimeoutException:
            print("Bandwidth check did not complete or 'Next' button did not appear.")
        except Exception as e:
            print(f"Error during bandwidth check: {e}")

        return bandwidth_check_status, is_successful

    def vet_mic_check(self):
        mic_status = "Failed"
        is_successful = False

        try:
            wait = WebDriverWait(self.driver, 15)

            # 1. Click 'Allow'
            allow_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Allow']")))
            allow_btn.click()
            print("Clicked Allow.")

            # 2. Click 'Record' (using the specific data-testid you provided)
            record_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='recording-button']")))
            record_btn.click()
            print("Clicked Record. Fake audio stream started...")

            # 3. Simulate the 'reading' time
            assess_ui_common_obj.play_audio()
            # Since the browser is feeding the fake audio/file, we just wait for the process to finish
            time.sleep(12)  # Buffer for counting 1 to 10

            mic_status = "Successful"
            is_successful = True

        except Exception as e:
            print(f"Mic check failed: {e}")

        return mic_status, is_successful

    def vet_mic_completion(self, wait_seconds=20):
        mic_complete_status = "Failed"
        is_successful = False

        try:
            # 1. Wait for the 'Success' text to confirm the recording was processed
            # We look for the text visible in your screenshot
            wait = WebDriverWait(self.driver, wait_seconds)
            success_text_xpath = "//*[contains(text(), 'Microphone check is complete')]"

            print("Waiting for microphone processing to complete...")
            wait.until(EC.visibility_of_element_located((By.XPATH, success_text_xpath)))

            # 2. Click the 'Next' button
            # Using the ID is high-speed and reliable here
            next_button = wait.until(EC.element_to_be_clickable((By.ID, "cade-next-button")))
            next_button.click()

            mic_complete_status = "Successful"
            is_successful = True
            print("Microphone check finished successfully.")

        except Exception as e:
            print(f"Mic completion failed: {e}")

        return mic_complete_status, is_successful


    def vet_welcome_page(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.ID, 'welcome_next_link').click()
            print("Welcome Page")
            vet_welcome_page = "Successful"
            is_element_successful = True
        except Exception as e:
            print(e)
            print("Failed in Welcome Page")
            is_element_successful = False
            vet_welcome_page = "Failed"

        return vet_welcome_page, is_element_successful

    def vet_quiet_please(self):
        time.sleep(10)
        try:
            self.driver.find_element(By.ID, 'distraction_next_link').click()
            print("Quiet Please Page")
            vet_quiet_please_page = "Successful"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Welcome Page successful")
            vet_quiet_please_page = "Failed"
            is_element_successful = False

        return vet_quiet_please_page, is_element_successful

    def vet_ready_check_box(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.ID, 'ready_checkbox').click()
            print("Ready Check Box successfull")
            vet_ready_check_box = "Successful"
            is_element_successful = True
        except Exception as e:
            print(e)
            print("Ready Check Box Failed")
            vet_ready_check_box = "Failed"
            is_element_successful = False

        return vet_ready_check_box, is_element_successful

    def vet_ready_start_link(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.ID, 'ready_start_link').click()
            print("Ready Start Successful")
            vet_ready_check_box = "Successful"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("vet_ready_start_link Failed")
            vet_ready_check_box = "Failed"
            is_element_successful = False
        return vet_ready_check_box, is_element_successful

    def vet_proceed_test(self):
        time.sleep(30)
        try:
            self.driver.find_element(By.XPATH, "//*[@class = 'proceed wizardButton greenBackground']").click()
            print("Proceed Test Successful")
            time.sleep(25)
            # os.system("F:\\my_test.mp3")
            vet_proceed_test = "Successful"
            is_element_successful = True
            time.sleep(5)
        except Exception as e:
            print(e)
            print("vet_ready_start_link Failed")
            vet_proceed_test = "Failed"
            is_element_successful = False
        return vet_proceed_test, is_element_successful

    def vet_speaking_tips(self):
        try:
            time.sleep(120)
            self.driver.find_element(By.XPATH, "//*[@class='testInstructionItem testInstructionNext']").click()
            print("Speaking Tips Successful")
            vet_speaking_tips = "Successful"
            is_element_successful = False

        except Exception as e:
            print(e)
            print("vet_speaking_tips Failed")
            vet_speaking_tips = "Failed"
            is_element_successful = False

        return vet_speaking_tips, is_element_successful

    def vet_overview(self):
        try:
            time.sleep(10)
            self.driver.find_element(By.XPATH, "//*[@class='wdtContextualItem  wdtContextNext']").click()
            print("Overview Page Success")
            vet_overview = "Successful"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("vet_speaking_tips Failed")
            vet_overview = "Failed"
            is_element_successful = False

        return vet_overview, is_element_successful

    def vet_instruction(self):
        time.sleep(10)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='wdtContextualItem wdtContextNext']").click()
            print("VET Instructions Page Success")
            vet_instruction = "Successful"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("VET Instructions Failed")
            vet_instruction = "Failed"
            is_element_successful = False

        return vet_instruction, is_element_successful

    def play_audio(self):
        os.system("F:\\my_test.mp3")

    def survey_submit(self):
        time.sleep(60)
        try:
            if self.driver.find_element(By.XPATH,
                                        "//*[@class = 'wdtContextualItem  wdtContextNext']").is_displayed():
                self.driver.find_element(By.XPATH, "//*[@class = 'wdtContextualItem  wdtContextNext']").click()
                print("survey Question Success")
            survey_submit = "Successful"
            is_element_successful = True
        except Exception as e:
            print(e)
            print("survey Question  Failed")
            survey_submit = "Failed"
            is_element_successful = False
        return survey_submit, is_element_successful

    def vet_retest(self, retest_consent):
        time.sleep(60)
        try:
            if retest_consent == 'Yes, Request for Retest':
                self.driver.find_element(By.XPATH, "//*[@class='btn btn-success']").click()
            else:
                self.driver.find_element(By.XPATH, "//*[@class='btn btn-default']").click()
                print("VET Retest Success")
            vet_retest = "Retest Consent Success"
            is_element_successful = True
        except Exception as e:
            print(e)
            print("VET Retest Failed")
            vet_retest = "Retest Consent Failed"
            is_element_successful = False
        return vet_retest, is_element_successful

    def cocubes_disclaimer(self):
        time.sleep(5)
        try:
            self.driver.switch_to.frame('thirdPartyIframe')
            self.driver.find_element(By.XPATH, "//*[@class='btn-primary mid-size accept']").click()
            print("Cocubes disclaimer is Accepted")
            cocubes_disclaimer = "Disclaimer Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Cocubes Disclaimer is failed")
            is_element_successful = False
            cocubes_disclaimer = "Disclaimer Failed"
        return cocubes_disclaimer, is_element_successful

    def cocubes_start_test(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='start-test btn-primary']").click()
            print("Cocubes Test is Started")
            cocubes_start_test = "Start test Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Cocubes test is not Started")
            is_element_successful = False
            cocubes_start_test = "Start test Failed"
        return cocubes_start_test, is_element_successful

    def cocubes_group_names(self, title):
        time.sleep(5)
        title = "//*[@title='%s']" % title
        try:
            cocubes_group_names = self.driver.find_element(By.XPATH, title).text
            print("Group name is Succeded")
            # cocubes_group_names = "Agreed"
            print(cocubes_group_names)
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Group name is Failed")
            is_element_successful = False
            cocubes_group_names = "Failed"
        return cocubes_group_names, is_element_successful

    def cocubes_answer_question(self, position):
        time.sleep(1)
        try:
            element = "//*[@name='%s']" % position
            self.driver.find_element(By.XPATH, element).click()
            print("Answer is Succeded")
            cocubes_question_answer = "Answered Successful"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Answer is Failed")
            is_element_successful = False
            cocubes_question_answer = "Answered Failed"
        return cocubes_question_answer, is_element_successful

    def cocubes_next_group(self):
        time.sleep(1)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='btn-primary next-btn btn-light-blue']").click()
            print("Next group is Succeded")
            cocubes_next_group = "Next group success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Next group is Failed")
            is_element_successful = False
            cocubes_next_group = "Next group failed"
        return cocubes_next_group, is_element_successful

    def cocubes_submit_test(self):
        time.sleep(1)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='btn-primary btn-primary-submit submit-btn']").click()
            print("Test is submitted")
            cocubes_next_group = "Submission Successful"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Test is not submitted")
            is_element_successful = False
            cocubes_next_group = "Submission Failed"
        return cocubes_next_group, is_element_successful

    def cocubes_comfirm_submit_test(self):
        time.sleep(1)
        try:
            self.driver.find_element(By.XPATH, "//*[@id='confirmsubmit']").click()
            print("Test is submitted")
            cocubes_next_group = "Submission Confirmed"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Test is not submitted")
            is_element_successful = False
            cocubes_next_group = "Submission confirmation Failed"
        return cocubes_next_group, is_element_successful

    def mettl_start_test(self):
        time.sleep(10)
        try:
            self.driver.switch_to.frame('thirdPartyIframe')
            self.driver.find_element(By.XPATH,
                                     "//*[@class='btn btn-primary py-2 px-3 btn-lineheight mobile-fixed-btn btn btn-primary']").click()
            print("Mettl Test is Started")
            mettl_start_test = "Start test1 Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl test is not Started")
            is_element_successful = False
            mettl_start_test = "Start test1 Failed"
        return mettl_start_test, is_element_successful

    def mettl_start_test2(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.XPATH,
                                     "//*[@class='py-2 px-4 mobile-btn-block btn btn-primary']").click()
            print("Mettl Test is Started2")
            mettl_start_test2 = "Start test2 Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl test is not Started2")
            is_element_successful = False
            mettl_start_test2 = "Start test2 Failed"
        return mettl_start_test2, is_element_successful

    def mettl_terms_and_conditions(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.NAME, "consentCheckbox").click()
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//*[@class ='px-4 mobile-btn-block btn btn-primary']").click()
            print("Terms and conditions Success")
            mettl_start_test2 = "Terms and conditions Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Terms and conditions Failed")
            is_element_successful = False
            mettl_start_test2 = "Terms and conditions Failed"
        return mettl_start_test2, is_element_successful

    def mettl_start_test3(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.XPATH,
                                     "//*[@class='px-4 text-sky-lighter mobile-fixed-btn  btn btn-primary']").click()
            print("Mettl Test is Started3")
            mettl_start_test3 = "Start test3 Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl test is not Started3")
            is_element_successful = False
            mettl_start_test2 = "Start test3 Failed"
        return mettl_start_test3, is_element_successful

    def mettl_answer_question(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='px-5 py-3 d-block form-check-label']").click()
            print("Mettl Test is Started2")
            mettl_answer_question = "answered_question"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl test is not Started2")
            is_element_successful = False
            mettl_answer_question = "answer failed"
        return mettl_answer_question, is_element_successful

    def mettl_next_section(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH,
                                     "//*[@class='word-break border px-xl-3 px-2 btn btn-success']").click()
            print("Mettl Next section success")
            mettl_next_section = "Next group success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl next section failed")
            is_element_successful = False
            mettl_next_section = "mettl next section failed"
        return mettl_next_section, is_element_successful

    def mettl_finish_test(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH,
                                     "//*[@class=' last-item-btn  btn btn-ft btn-link btn-focus-outline  btn-default-ft border-white']").click()
            print("Mettl Final Submit success")
            mettl_next_section = "Mettl Final Submit success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl Final Submit failed")
            is_element_successful = False
            mettl_next_section = "Mettl Final Submit failed"
        return mettl_next_section, is_element_successful

    def mettl_finish_test_confirmation(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH,
                                     '//*[@class="btn btn-primary py-2 px-3 ft-btn-danger btn-danger btn-focus-outline-end-test btn btn-primary"]').click()
            print("Mettl Final Submit success")
            mettl_next_section = "Mettl Final Submit Confirmation success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl Final Submit failed")
            is_element_successful = False
            mettl_next_section = "Mettl Final Submit Confirmation failed"
        return mettl_next_section, is_element_successful

    def mettl_group_names(self):
        time.sleep(2)
        try:
            value = self.driver.find_element(By.XPATH,
                                             '//*[@class="pr-2 text-truncate"]').text
            print(value)
            print(type(value))
            print(len(value))
            print("Mettl group names success")
            group_names = value
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Mettl group names failed")
            is_element_successful = False
            mettl_next_section = "Mettl Final Submit Confirmation failed"
        return group_names, is_element_successful

    def tl_start_test(self):
        time.sleep(30)
        try:
            self.driver.switch_to.frame('thirdPartyIframe')
            # job title text
            self.driver.find_element(By.XPATH, "//*[@id='textbox_62fa715a-0dcb-498b-bf09-151fa7faad61']").send_keys(
                'QA')
            # recent position type
            self.driver.find_element(By.XPATH,
                                     '//*[@id="dropdown_d7244e75-eb2a-47a9-b23b-70f3412244d1"]/option[3]').click()
            # Recent Industry
            self.driver.find_element(By.XPATH,
                                     '//*[@id="dropdown_a7d5f8e3-1de4-4840-acf2-5a3d5ab7265e"]/option[2]').click()
            # recent occupation
            self.driver.find_element(By.XPATH,
                                     '//*[@id="dropdown_7ed143db-e43f-4759-af35-9f5eebde8a8f"]/option[4]').click()
            # next button
            self.driver.find_element(By.XPATH, '//*[@id="navigateNextBottom').click()

            print("TL Test is Started")
            tl_start_test = "Start test Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("TL test is not Started")
            is_element_successful = False
            tl_start_test = "Start test Failed"
        return tl_start_test, is_element_successful

    def tl_copyright_page(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.XPATH, '//*[@id="navigateNextBottom"]').click()

            print("TL Copywrite success")
            tl_copyright_page = "Copywrite Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("TL Copywrite Failed")
            is_element_successful = False
            tl_copyright_page = "Copywrite Failed"
        return tl_copyright_page, is_element_successful

    def tl_instructions_page1(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.XPATH, '//*[@id="navigateNextBottom"]').click()
            print("TL instructions2 success")
            tl_instructions_page1 = "instructions Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("TL instructions2 failed")
            is_element_successful = False
            tl_instructions_page = "instructions Failed"
        return tl_instructions_page1, is_element_successful

    def tl_instructions_page2(self):
        time.sleep(5)
        try:
            self.driver.find_element(By.XPATH, '//*[@class="btn btn-primary').click()
            print("TL instructions success")
            tl_instructions_page2 = "instructions2 Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("TL instructions failed")
            is_element_successful = False
            tl_instructions_page2 = "instructions2 Failed"
        return tl_instructions_page2, is_element_successful

    def tl_test_directions1(self):
        tl_test_directions1 = "EMPTY"
        is_element_successful = None
        for count in range(0, 9):
            time.sleep(5)
            try:
                self.driver.find_element(By.XPATH, '//*[@id="navigateNextBottom').click()
                print("TL instructions success")
                tl_test_directions1 = "test directions1 Success"
                is_element_successful = True

            except Exception as e:
                print(e)
                print("TL instructions failed")
                is_element_successful = False
                tl_test_directions1 = "test directions1 Failed"

        return tl_test_directions1, is_element_successful

    def wheebox_starttest_checkbox(self):
        time.sleep(5)
        try:
            self.driver.switch_to.frame('thirdPartyIframe')
            self.driver.find_element(By.XPATH, "//*[@class='checkbox state-success']").click()
            print("Wheebox agreement is Accepted")
            wheebox_agreement = "Agreed"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Wheebox agreement is failed")
            is_element_successful = False
            wheebox_agreement = "Not Agreed"
        return wheebox_agreement, is_element_successful

    def wheebox_proceed_test(self):
        time.sleep(30)
        try:
            self.driver.find_element(By.XPATH, "//*[@id='waitingLoungButton']").click()
            print("Wheebox proceed test  is success")
            wheebox_proceed_test = "Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Wheebox proceed test is failed")
            is_element_successful = False
            wheebox_proceed_test = "Failed"
        return wheebox_proceed_test, is_element_successful

    def wheebox_auto_next_qn(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='checkbox green-txt-clr unselectable']").click()
            print("Auto next question is success")
            wheebox_auto_next_qn = "Success"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Auto next question is failed")
            is_element_successful = False
            wheebox_auto_next_qn = "Failed"
        return wheebox_auto_next_qn, is_element_successful

    def wheebox_answer_qn(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='radio state-error']").click()
            print("Question answer is success")
            wheebox_answer_qn = "answered"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Question answer is failed")
            is_element_successful = False
            wheebox_answer_qn = "Not answered"
        return wheebox_answer_qn, is_element_successful

    def wheebox_submit_test(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='pull-right unselectable']").click()
            print("Test is submitted successfully")
            wheebox_submit_test = "submitted"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Test is not submitted successfully")
            is_element_successful = False
            wheebox_submit_test = "Not submitted"
        return wheebox_submit_test, is_element_successful

    def wheebox_confirm_submit(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//*[@class='confirm']").click()
            print("Test is submitted successfully")
            wheebox_confirm_submit = "submitted"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("Test is not submitted successfully")
            is_element_successful = False
            wheebox_confirm_submit = "Not submitted"
        return wheebox_confirm_submit, is_element_successful

    def chaining_shortlisting(self):
        try:
            wait = WebDriverWait(self.driver, 180)
            time.sleep(5)
            print("Page title:", self.driver.title)
            print("URL:", self.driver.current_url)
            print("Current DOM length:", len(self.driver.page_source))
            wait.until(EC.url_contains("/submitSuccess"))
            print("URL:", self.driver.current_url)
            print("Checking DOM after redirect...")
            print("DOM length:", len(self.driver.page_source))

            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(buttons):
                print(f"Button {i}: name={btn.get_attribute('name')}, text='{btn.text}'")
            self.driver.find_element(By.XPATH, "//button[@name='btnStartNextTest' and contains(., 'Take me to next test')]").click()
            is_shortlisted_to_next = 'Success'
            is_element_successful = 'Success'
        except Exception as e:
            print(e)
            is_shortlisted_to_next = 'Failed'
            is_element_successful = 'Failed'
        return is_shortlisted_to_next, is_element_successful

        # next_button = wait.until(EC.element_to_be_clickable((
        #     By.XPATH, "//button[.//span[contains(text(), 'Take me to next test')]]"
        # )))
        # next_button.click()



    def wheebox_q1_ans(self):
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//*[@id='butt1']").click()
            print("started answering from question1")
            wheebox_q1_ans = "answered"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("not started answering")
            is_element_successful = False
            wheebox_q1_ans = "Not answered"
        return wheebox_q1_ans, is_element_successful

    def select_coding_catalog_if_enabled(self, language_text):
        """
        Select coding language/catalog (select name='codingLang') only when the control
        is enabled. If disabled (ng-disabled / single language / executing), do nothing
        and return False — caller should proceed straight to ACE editor.
        """
        if not language_text or not str(language_text).strip():
            return False
        label = str(language_text).strip()
        try:
            sel_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'codingLang'))
            )
        except TimeoutException:
            return False
        # Disabled: no selection — move on to ace_editor
        if sel_el.get_attribute('disabled') is not None or not sel_el.is_enabled():
            return False
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", sel_el
            )
            time.sleep(0.2)
            select = Select(sel_el)
            select.select_by_visible_text(label)
            time.sleep(0.5)
            return True
        except Exception:
            try:
                select = Select(sel_el)
                for opt in select.options:
                    if opt.text and label.lower() == opt.text.strip().lower():
                        select.select_by_visible_text(opt.text)
                        time.sleep(0.5)
                        return True
            except Exception:
                pass
        return False

    def set_ace_editor_value(self, text=None):
        """
        Set the ui-ace / Ace editor content to the given string.
        Clear/empty is not supported here — pass text only. If text is None or '',
        returns without doing anything.
        """
        if not text:
            return

        value = str(text)

        # Ace root: prefer the editor that contains the visible ace_content surface
        try:
            editor = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,'ace_content')]/ancestor::div[contains(@class,'ace_editor')][1]",
            )
        except Exception:
            editor = self.driver.find_element(
                By.XPATH, "//div[contains(@class,'ace_editor')]"
            )

        # session.setValue keeps Ace document and ui-ace onChange in sync better than setValue alone
        self.driver.execute_script(
            """
            var el = arguments[0], val = arguments[1];
            var ed = (el.env && el.env.editor) ? el.env.editor : ace.edit(el);
            if (ed && ed.session) {
                ed.session.setValue(val);
                ed.clearSelection();
                ed.focus();
            }
            """,
            editor,
            value,
        )

    def wait_until_coding_execution_finishes(self, timeout=10):
        """
        After Run Code / Run Tests / Submit, the UI shows 'Executing...' while vm.isExecuting
        is true. Wait until that indicator is no longer visible, or until timeout (default 10s).
        If the session dies (navigation/new window), exits quietly so the caller can handle it.
        """
        deadline = time.time() + timeout
        # Text shown next to spinner while vm.isExecuting is true
        xpath = "//*[contains(normalize-space(),'Executing')]"
        while time.time() < deadline:
            try:
                visible = False
                for el in self.driver.find_elements(By.XPATH, xpath):
                    try:
                        if el.is_displayed():
                            visible = True
                            break
                    except Exception:
                        pass
                if not visible:
                    return
            except WebDriverException:
                # Session invalid / browser closed — don't re-raise; caller may still have quit() pending
                return
            time.sleep(0.25)
        # Timed out — continue anyway so the script does not hang forever

    def validate_run_code_finished(self, timeout=15, require_results_panel=False):
        """
        After **Run Code** completes (Executing... gone), validate the expected screen:
        Run Code button is visible and enabled again, and optionally Test Cases Results
        panel is visible (Sample TC / Pass, etc.).

        Use after click_run_code(), not after click_run_tests().

        Returns:
            (True, None) if validation passes
            (False, str) with reason if not
        """
        try:
            run_code_xpath = (
                "//div[contains(@class,'compile-execute-button-container')]"
                "//button[normalize-space()='Run Code']"
            )
            btn = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, run_code_xpath))
            )
            if btn.get_attribute('disabled') is not None:
                return (False, 'Run Code button has disabled attribute')
            if not btn.is_enabled():
                return (False, 'Run Code button is not enabled')
            classes = (btn.get_attribute('class') or '').lower()
            if 'disabled' in classes:
                return (False, 'Run Code button has disabled class')
            if require_results_panel:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "//h4[contains(.,'Test Cases Results')]")
                        )
                    )
                except TimeoutException:
                    return (False, 'Test Cases Results panel not visible')
            return (True, None)
        except TimeoutException:
            return (False, 'Run Code button not visible within timeout')
        except WebDriverException as e:
            return (False, str(e))

    def validate_run_tests_finished(self, timeout=45, require_results_panel=False, require_pass_message=False):
        """
        After **Run Tests** completes (Executing... gone), validate the expected screen.
        Run Tests can stay disabled while vm.isExecuting is true — we wait until the button
        is clickable (enabled), not just visible, so validation does not run mid-execution.

        Use after click_run_tests(), not after click_run_code().

        Returns:
            (True, None) if validation passes
            (False, str) with reason if not
        """
        try:
            run_tests_xpath = (
                "//div[contains(@class,'compile-execute-button-container')]"
                "//button[normalize-space()='Run Tests']"
            )
            # Wait until enabled — visibility alone fails while UI still executing
            btn = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, run_tests_xpath))
            )
            classes = (btn.get_attribute('class') or '').lower()
            if 'disabled' in classes:
                return (False, 'Run Tests button has disabled class')
            if require_results_panel:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "//h4[contains(.,'Test Cases Results')]")
                        )
                    )
                except TimeoutException:
                    return (False, 'Test Cases Results panel not visible')
            if require_pass_message:
                # After Run Tests: green summary e.g. "Test case passed" or compiler success
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located(
                            (
                                By.XPATH,
                                "//*[contains(.,'Test case passed') or contains(.,'Syntax Checking Successful')]",
                            )
                        )
                    )
                except TimeoutException:
                    return (False, 'Pass / success message not visible after Run Tests')
            return (True, None)
        except TimeoutException:
            return (False, 'Run Tests button not clickable within timeout (still executing or stuck disabled)')
        except WebDriverException as e:
            return (False, str(e))

    def validate_submit_and_continue_finished(self, timeout=15, require_success_banner=True):
        """
        After **Submit & Continue Coding** completes (Executing... gone), validate success.
        The app shows a green banner: "Your answer has been submitted successfully."

        Use after click_submit_and_continue_coding(). If the app navigates away immediately,
        require_success_banner can be False and you can instead check URL or next question.

        Returns:
            (True, None) if validation passes
            (False, str) with reason if not
        """
        try:
            if require_success_banner:
                # Green banner at top after successful submit (HirePro)
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//*[contains(.,'submitted successfully') or contains(.,'Submitted successfully')]",
                        )
                    )
                )
            else:
                # At least Submit button idle again (same page, no navigation)
                submit_xpath = (
                    "//div[contains(@class,'compile-execute-button-container')]"
                    "//button[contains(.,'Submit') and contains(.,'Continue Coding')]"
                )
                btn = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, submit_xpath))
                )
                if btn.get_attribute('disabled') is not None or not btn.is_enabled():
                    return (False, 'Submit & Continue button still disabled after submit')
            return (True, None)
        except TimeoutException:
            if require_success_banner:
                return (False, 'Success banner (submitted successfully) not visible within timeout')
            return (False, 'Submit button not visible within timeout')
        except WebDriverException as e:
            return (False, str(e))

    def click_run_code(self):
        """Click Run Code on the coding execution panel; waits until Executing... disappears (max 10s)."""
        btn = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'compile-execute-button-container')]//button[normalize-space()='Run Code']")
            )
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
            btn,
        )
        self.wait_until_coding_execution_finishes(timeout=10)

    def click_run_tests(self):
        """Click Run Tests; wait for Executing... to finish. Run Tests often runs longer — 45s cap."""
        btn = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'compile-execute-button-container')]//button[normalize-space()='Run Tests']")
            )
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
            btn,
        )
        self.wait_until_coding_execution_finishes(timeout=45)

    def click_submit_and_continue_coding(self):
        """Click Submit & Continue Coding; waits until Executing... disappears (max 10s)."""
        btn = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'compile-execute-button-container')]//button[contains(.,'Submit') and contains(.,'Continue Coding')]",
                )
            )
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
            btn,
        )
        self.wait_until_coding_execution_finishes(timeout=10)

    def coding_editor(self, code):
        self.driver.find_element(By.CLASS_NAME, 'ace_content').click()
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.active_element.send_keys(code)
        self.driver.find_element(By.XPATH, '//button[text()=" Compile & Execute"]').click()
        time.sleep(7)
        action = self.driver.find_element(By.CLASS_NAME, 'ace_content')
        action.click()
        self.driver.switch_to.parent_frame()
        action.send_keys(Keys.CONTROL + 'A')

    # --- Login validation helpers (do not change ui_login_to_test above) ---

    def fill_login_fields_without_submit(self, user_name, password):
        """Clear and fill login username/password only; does not click Login."""
        user_input = self.wait.until(
            EC.visibility_of_element_located((By.NAME, 'loginUsername'))
        )
        user_input.clear()
        if user_name:
            user_input.send_keys(user_name)
        user_pass = self.driver.find_element(By.NAME, 'loginPassword')
        user_pass.clear()
        if password:
            user_pass.send_keys(password)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, "block-ui-overlay")
                )
            )
        except TimeoutException:
            pass

    def is_login_submit_button_enabled(self):
        """True if Login button is enabled (clickable); False if disabled."""
        try:
            login_btn = self.driver.find_element(By.NAME, 'btnLogin')
        except Exception:
            return False
        # disabled attribute present -> not enabled
        if login_btn.get_attribute('disabled') is not None:
            return False
        if not login_btn.is_enabled():
            return False
        # Angular may use class instead of attribute
        classes = (login_btn.get_attribute('class') or '').lower()
        if 'disabled' in classes:
            return False
        return True

    def is_still_on_login_page(self):
        """True if login form is still visible (user has not navigated away)."""
        try:
            self.driver.find_element(By.NAME, 'loginUsername')
            return True
        except Exception:
            return False

    # Failure cases stay on login page; message is in:
    # <div class="text-center login-error ng-binding ng-scope" ng-if="vm.loginInfo.IsException" ...>
    _LOGIN_ERROR_CSS = 'div.login-error'
    _LOGIN_ERROR_XPATH = '//div[contains(@class,"login-error") and contains(@class,"text-center")]'

    def get_login_page_error_message(self):
        """
        Return visible login-error text if present, else None.
        Message lives in div.login-error (ng-if vm.loginInfo.IsException) below the form.
        """
        try:
            # Prefer CSS; multiple matches possible — use first displayed with non-empty text
            for by, locator in (
                (By.CSS_SELECTOR, self._LOGIN_ERROR_CSS),
                (By.XPATH, self._LOGIN_ERROR_XPATH),
            ):
                for el in self.driver.find_elements(by, locator):
                    try:
                        if el.is_displayed():
                            text = (el.text or '').strip()
                            if text:
                                return text
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    def wait_for_login_error_message(self, timeout_seconds=10):
        """
        Wait until the login-error div is visible (failure path — still on login page).
        Returns message text, or None if timeout.
        """
        try:
            error_element = WebDriverWait(self.driver, timeout_seconds).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self._LOGIN_ERROR_CSS))
            )
            text = (error_element.text or '').strip()
            return text if text else None
        except TimeoutException:
            return None

    def validate_login_credentials(self, user_name, password):
        """
        Validate login without using ui_login_to_test.
        - If login id or password is empty: returns ('BUTTON_DISABLED', None) when button
          is correctly disabled, ('BUTTON_ENABLED', None) when it should not be enabled.
        - If both provided: clicks Login when enabled, then returns
          ('ERROR_ON_PAGE', message) if error shown on login page,
          ('NAVIGATED_AWAY', None) if moved past login (no error on login page).
        """
        user_name = user_name if user_name is not None else ''
        password = password if password is not None else ''

        self.fill_login_fields_without_submit(user_name, password)
        time.sleep(0.5)  # allow Angular to update button state

        if not user_name.strip() or not password.strip():
            if self.is_login_submit_button_enabled():
                return 'BUTTON_ENABLED', None
            return 'BUTTON_DISABLED', None

        if not self.is_login_submit_button_enabled():
            return 'BUTTON_DISABLED', None

        login_btn = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'btnLogin'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
        self.driver.execute_script("arguments[0].click();", login_btn)

        # Failure: stay on login page; message appears in div.login-error when vm.loginInfo.IsException
        err = self.wait_for_login_error_message(timeout_seconds=10)
        if err:
            return 'ERROR_ON_PAGE', err

        # No error div yet — either navigating away or slow render; poll briefly
        deadline = time.time() + 5
        while time.time() < deadline:
            if not self.is_still_on_login_page():
                return 'NAVIGATED_AWAY', None
            err = self.get_login_page_error_message()
            if err:
                return 'ERROR_ON_PAGE', err
            time.sleep(0.3)

        # Still on login page but no login-error visible
        if self.is_still_on_login_page():
            err = self.get_login_page_error_message()
            if err:
                return 'ERROR_ON_PAGE', err
            return 'ERROR_ON_PAGE', '(still on login page; login-error div not visible)'
        return 'NAVIGATED_AWAY', None


assess_ui_common_obj = AssessmentUICommon()
