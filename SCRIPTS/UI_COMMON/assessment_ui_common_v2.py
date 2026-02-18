import os
import platform
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



from selenium.common.exceptions import TimeoutException
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

    def ui_login_to_test(self, user_name, password):

        # Username
        user_input = self.wait.until(
            EC.visibility_of_element_located((By.NAME, 'loginUsername'))
        )
        user_input.clear()
        user_input.send_keys(user_name)

        # Password
        user_pass = self.driver.find_element(By.NAME, 'loginPassword')
        user_pass.clear()
        user_pass.send_keys(password)

        # ✅ WAIT for Angular block UI to disappear
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, "block-ui-overlay")
                )
            )
        except TimeoutException:
            pass  # overlay might not appear every time

        # ✅ WAIT for button to be CLICKABLE (not just visible)
        login_btn = self.wait.until(
            EC.element_to_be_clickable((By.NAME, 'btnLogin'))
        )

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

    def select_answer_for_mca_question(self, answer):
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

    def vet_start_test(self):
        time.sleep(5)
        try:
            self.driver.switch_to.frame('thirdPartyIframe')
            # To accept consent button
            element = self.driver.find_element(By.ID, "accept-consent-button")
            if element.is_displayed():
                element.click()
            else:
                pass
            self.driver.find_element(By.XPATH, "//*[@class='wdtContextualItem  wdtContextStart']").click()
            print("VET Test is started Successfully")
            vet_test_started = "Successful"
            is_element_successful = True

        except Exception as e:
            print(e)
            print("VET Start test is failed")
            is_element_successful = False
            vet_test_started = "Failed"
        return vet_test_started, is_element_successful

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


assess_ui_common_obj = AssessmentUICommon()
