import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.expected_conditions as EC  # Import and assign to EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, \
    StaleElementReferenceException, ElementClickInterceptedException

from SCRIPTS.SECURITY.char_encoding import value
from SCRIPTS.UI_COMMON.assessment_ui_common_v2 import *


class SelfAssessmentLogin:
    def __init__(self):
        self.delay = 120

    def initiate_browser(self, url, path):
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        # chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--disable-gpu")  # Recommended to prevent GPU errors in headless mode
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(executable_path=path, chrome_options=chrome_options)
        self.driver.get(url)
        # self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        self.driver.switch_to.window(self.driver.window_handles[0])
        print("Browser initiated")
        return self.driver

    def ui_login_to_tenant(self, user_name, password):
        time.sleep(2)
        try:
            # To select vendors/tpo/placecom option before login page
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            element = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Vendors/TPO/Placecom')]"))
            )
            element.click()
            time.sleep(2)
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            # self.driver.find_element(By.XPATH, '//*[contains(text(), "Vendors/TPO/Placecom")]').click()
            self.driver.find_element(By.NAME, 'loginName').clear()
            self.driver.find_element(By.NAME, 'loginName').send_keys(user_name)
            self.driver.find_element(By.XPATH, "//input[@type='password']").clear()
            self.driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
            time.sleep(1)
            self.driver.find_element(By.XPATH, '//*[@class = "btn btn-default button_style login ng-binding"]').click()
            # self.driver.get(
            #     "https://amsin.hirepro.in/crpo/#/crpodemo/assessment/selfAssessment/eyJ0ZXN0SWQiOjIwNjIzfQ==/question")
            print("tenant login success")

            login_status = 'SUCCESS'

        except Exception as e:
            print(e)
            login_status = 'FAILED'
        return login_status

    def create_test_sa(self):
        current_date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
        test_status = 'FAILED'
        wait = WebDriverWait(self.driver, 120)
        test_name = f"Automation_sa_{current_date}"
        print(f"Test name : {test_name}")
        try:
            print("Inside create test")
            WebDriverWait(self.driver, 180).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            time.sleep(5)

            WebDriverWait(self.driver, 180).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            create_button = self.driver.find_element(By.XPATH,
                                                     "//i[@class='fa fa-plus']")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", create_button)
            self.driver.execute_script("arguments[0].click();", create_button)

            WebDriverWait(self.driver, 180).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            name = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@ng-model='vm.test.name']")))
            name.send_keys(test_name)
            WebDriverWait(self.driver, 180).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            save_test_button = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class="btn btn-primary_"]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_test_button)
            self.driver.execute_script("arguments[0].click();", save_test_button)
            growl_message = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located(growl_message_locator)
            )
            print("Test status: ", growl_message.text)

            if growl_message.text == 'Test Created Successfully.':
                test_status = 'SUCCESS'

        except TimeoutException as te:
            print(f"TimeoutException occurred: {te}")
        except Exception as e:
            print(f"Exception occurred: {e}")

        return test_status, test_name

    def select_plus(self, section_name):
        try:
            time.sleep(2)
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            section = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//strong[contains(text(), '"+section_name+"')]")
                )
            )
            time.sleep(2)
            add_question_button = section.find_element(
                By.XPATH, ".//following::a[contains(@ng-click, 'createQuestion') and contains(., 'Add Question')]"
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", add_question_button)
            self.driver.execute_script("arguments[0].click();", add_question_button)
            time.sleep(2)

            return 'SUCCESS'

        except TimeoutException as te:
            print(f"TimeoutException occurred: {te}")
            return 'FAILED'
        except StaleElementReferenceException as e:
            print(f"Stale element reference error: {e}")
        except Exception as e:
            print(f"Exception occurred: {e}")
            return 'FAILED'

    def select_question_attributes(self):
        try:

            wait = WebDriverWait(self.driver, 40)
            dropdown_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.tad-container button.dropdown-toggle")))
            dropdown_button.click()

            difficulty = self.driver.find_element(By.XPATH,
                                                  '//*[@class = "dropdown-menu ng-scope am-fade bottom-left"]')
            time.sleep(1)
            if difficulty.is_displayed():
                ele = self.driver.find_element(By.XPATH, '//a[@title="Low"]')
                ele.click()
            else:
                print("Difficulty not selected")

            self.driver.find_element(By.XPATH,
                                     '//input[@placeholder="Author"]/following-sibling::div/button').click()
            category = self.driver.find_element(By.XPATH,
                                                '//*[@class = "dropdown-menu ng-scope am-fade bottom-left"]')
            time.sleep(1)
            if category.is_displayed():
                ele = self.driver.find_element(By.XPATH, "//a[@title='administrator']")
                ele.click()
            else:
                print("Author not selected")

            self.driver.find_element(By.XPATH,
                                     '//input[@placeholder="Category"]/following-sibling::div/button').click()
            category = self.driver.find_element(By.XPATH,
                                                '//*[@class = "dropdown-menu ng-scope am-fade bottom-left"]')
            time.sleep(1)
            if category.is_displayed():
                ele = self.driver.find_element(By.XPATH, '//a[@title="Automobile Engineering"]')
                ele.click()
            else:
                print("Category not selected")

            self.driver.find_element(By.XPATH,
                                     '//input[@placeholder="Topic"]/following-sibling::div/button').click()
            topic = self.driver.find_element(By.XPATH,
                                             '//*[@class = "dropdown-menu ng-scope am-fade bottom-left"]')
            time.sleep(1)
            if topic.is_displayed():
                ele = self.driver.find_element(By.XPATH, '//a[@title="Automotive Chassis"]')
                ele.click()
            else:
                print("Topic not selected")

            self.driver.find_element(By.XPATH,
                                     '//input[@placeholder="Status"]/following-sibling::div/button').click()
            status = self.driver.find_element(By.XPATH,
                                              '//*[@class = "dropdown-menu ng-scope am-fade bottom-left"]')
            time.sleep(1)
            if status.is_displayed():
                ele = self.driver.find_element(By.XPATH, '//a[@title="QA Approved"]')
                ele.click()
            else:
                print("Status not selected")

            return 'SUCCESS'

        except Exception as e:
            print(e)

        return 'FAILED'

    def create_mcq_q(self):
        try:
            print("Creating mcq question...")
            # time.sleep(5)

            # self.wait_for_overlay_to_disappear()
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            self_assessment_obj.add_new_section()
            wait = WebDriverWait(self.driver, 20)
            mcq_sec = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='MCQ Section']")))
            mcq_sec.click()
            time.sleep(1)

            self_assessment_obj.select_plus('MCQ')
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "tab-option"]'))
            ).click()
            self_assessment_obj.select_question_attributes()
            self.driver.find_element(By.XPATH, "//i[@class='fa fa-fw fa-text-width']").click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Question Description']"))
            ).send_keys("po mcq create q sa automation don't use /ans : B ")

            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//textarea[@class='form-control ng-pristine ng-untouched ng-valid ng-empty']"))
            )
            for idx, e in enumerate(elements, start=1):
                e.send_keys(str(idx))
            options = self.driver.find_elements(By.XPATH, "//*[@name='answer']")
            options[1].click()

            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, "//div[@ng-if='!vm.data.explanationAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"))
            ).send_keys(" Notes sample Data c\n !@#$%^&*()_+-=094521;',.?/ ")
            time.sleep(1)
            WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-default btn-success btn-sm ng-scope"]'))
            ).click()
            # time.sleep(2)
            return 'SUCCESS'

        except Exception as e:
            print(f"Exception occurred while creating MCQ: {e}")
            return 'FAILED'

    def create_rtc_q(self):
        try:
            print("Creating rtc question...")
            # creating question - rtc
            time.sleep(2)
            self_assessment_obj.add_new_section()
            wait = WebDriverWait(self.driver, 20)
            rtc_sec = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Paragraph Section']")))
            rtc_sec.click()
            time.sleep(1)

            self_assessment_obj.select_plus('ReferenceToContext')

            self.driver.find_element(By.XPATH, '//*[@class = "tab-option"]').click()

            self_assessment_obj.select_question_attributes()

            time.sleep(2)
            # self_assessment_obj.select_text_toggle_button(1)
            self.driver.find_element(By.CSS_SELECTOR,
                                     '''label[ng-class="{'btn-primary':vm.data.paragraphAsText}"] i[class='fa fa-fw fa-text-width']''').click()
            rtc_parent_text = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Paragraph']")
            rtc_parent_text.send_keys("po RTC create q with 2 child sa automation don't use ")
            self.driver.find_element(By.XPATH,
                                     '''//label[@ng-class="{'btn-primary':!question.questionStringAsHtml}"]//i[@class='fa fa-fw fa-text-width']''').click()
            rtc_child_text = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Question']")
            rtc_child_text.send_keys("child q1 sa automation /ans : A ")

            elements = self.driver.find_elements(By.XPATH,
                                                 "//textarea[@class='form-control ng-pristine ng-untouched ng-valid "
                                                 "ng-empty']")
            options = 1
            for e in elements:
                e.send_keys(options)
                options += 1
            time.sleep(1)

            option = self.driver.find_elements(By.XPATH, "//*[@name='answer']")
            option[0].click()
            time.sleep(2)

            self.driver.find_element(By.CSS_SELECTOR,
                                     '''button[ng-click="vm.actionClicked('addNewQuestion');"]''').click()
            time.sleep(2)

            self.driver.find_element(By.XPATH,
                                     '''//label[@ng-class="{'btn-primary':!question.questionStringAsHtml}"]//i[@class='fa fa-fw fa-text-width']''').click()
            rtc_child_text = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Question']")
            rtc_child_text.send_keys("child q2 sa automation /ans : B ")

            elements = self.driver.find_elements(By.XPATH,
                                                 "//textarea[@class='form-control ng-pristine ng-untouched ng-valid "
                                                 "ng-empty']")
            options = 1
            for e in elements:
                e.send_keys(options)
                options += 1
            time.sleep(2)

            option = self.driver.find_elements(By.XPATH, "//*[@name='answer']")
            option[1].click()
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[@ng-if='!vm.data.explanationAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"))
            ).send_keys(" Notes sample Data c\n !@#$%^&*()_+-=094521;',.?/ ")
            time.sleep(1)

            element = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-default btn-success btn-sm ng-scope"]'))
            )

            # Scroll to the element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

            # Click the element
            element.click()

            return 'SUCCESS'

        except Exception as e:
            print(e)

        return 'FAILED'

    def create_subjective_q(self):
        try:
            print("Creating subjective question...")
            wait = WebDriverWait(self.driver, 20)

            # Adding a new section and selecting the subjective section
            time.sleep(2)
            self_assessment_obj.add_new_section()
            subjective_sec = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Subjective Section']"))
            )
            subjective_sec.click()
            time.sleep(1)

            self_assessment_obj.select_plus('QA')
            self.driver.find_element(By.XPATH, '//*[@class="tab-option"]').click()
            self_assessment_obj.select_question_attributes()

            # Selecting question type and writing question description
            time.sleep(2)
            self.driver.find_element(By.CSS_SELECTOR,
                                     "label[ng-class=\"{'btn-primary':vm.data.questionAsText}\"] i.fa.fa-fw.fa-text-width"
                                     ).click()

            # Filling in the question and sample answer
            self.driver.find_element(By.XPATH, "//textarea[@placeholder='Question Description']").send_keys(
                '''po subjective create q with all config self-assessment automation don't use \n self_assessment.xls \n Which is your favourite food, dish or cuisine? Write two paragraphs about your favourite food, dish or cuisine. Make sure you follow all the rules about sentences and paragraphs you have learnt.'''
            )

            self.driver.find_element(By.XPATH, "//textarea[@placeholder='Sample Answer']").send_keys(
                "I am very foodie. I love to eat. Among the number of foods, Pizza is my favourite food because it tastes and smells fabulous. My Mom cooks the best Pizzas in the world. I always ask her to make Pizza. In Pizzas, I love onion cheese Pizza a lot. This is because cheese pizza is healthy and makes me strong. To create fun we also organize pizza races in terms of who can eat the maximum number of pizzas. I can eat many pizzas at a time."
            )

            # Configuring dynamic answer and attachment options
            self.driver.find_element(By.CSS_SELECTOR,
                                     "label[ng-class=\"{'btn-primary':vm.data.questionInfo.isDynamicAnswerConfig === true}\"]"
                                     ).click()
            time.sleep(1)

            def configure_option(option_name, checkbox_label):
                self.driver.find_element(By.XPATH,
                                         f"//span[text()='{option_name}']/ancestor::div[contains(@class,'panel')]//input[@type='text' and @ng-model='answerConfig.name']"
                                         ).send_keys(option_name)
                self.driver.find_element(By.XPATH,
                                         f"//span[text()='{option_name}']/ancestor::div[contains(@class,'panel')]//label[text()='{checkbox_label}']"
                                         ).click()

            configure_option('TextArea', 'Yes')
            configure_option('Attachment', 'Yes')

            # Configuring attachment options
            self.driver.find_element(By.XPATH,
                                     "//span[text()='Attachment']/ancestor::div[contains(@class,'panel')]//div[@title='Extensions']//span[@class='caret']"
                                     ).click()
            self.driver.find_element(By.CSS_SELECTOR, "button[data-ng-click='vm.moveAllItemsRight();']").click()
            self.driver.find_element(By.XPATH, "//a[text()='Done']").click()

            configure_option('Capture', 'Yes')

            # Uploading file
            time.sleep(5)
            label = self.driver.find_element(By.XPATH,
                                             "//b[normalize-space()='Do you want to Upload File in Question Description']")
            actions = ActionChains(self.driver)
            actions.move_to_element(label).click().perform()

            checkbox = self.driver.find_element(By.XPATH,
                                                "//input[@type='checkbox' and @ng-model='vm.data.attachment.replaceQuestionDescription']")
            print("Selected File upload in Question Description : ", checkbox.is_selected())

            self.driver.find_element(By.XPATH,
                                     "//input[@placeholder='File name to be saved with extensions. Eg: fileName.csv,fileName.txt']").send_keys(
                'self_assessment.xls')
            upload_element = self.driver.find_element(By.XPATH, "//label[text()='File Name:']/following::div//input[@type='file']")
            file_path = 'D:/automation_new/ASSESSMENT/PythonWorkingScripts_InputData/UI/Assessment/self_assessment.xls'
            upload_element.send_keys(file_path)

            growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
            growl_message = wait.until(EC.visibility_of_element_located(growl_message_locator))
            print(growl_message.text)
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[@ng-if='!vm.data.explanationAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"))
            ).send_keys(" Notes sample Data c\n !@#$%^&*()_+-=094521;',.?/ ")
            time.sleep(1)

            element = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default btn-success btn-sm ng-scope']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()

            return 'SUCCESS'

        except Exception as e:
            print(e)
            return 'FAILED'

    def create_fib_q(self):
        try:
            print("Creating FIB question...")

            # Add a new section
            self_assessment_obj.add_new_section()

            # Wait for "Fill In The Blank Section" to be clickable
            wait = WebDriverWait(self.driver, 40)
            fib_section = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Fill In The Blank Section']"))
            )
            fib_section.click()

            # Select "Fill In The Blank" question type
            self_assessment_obj.select_plus("Fill In The Blank")

            # Click on the tab option
            wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "tab-option"]'))
            ).click()

            # Select question attributes
            self_assessment_obj.select_question_attributes()

            # Input question text
            editable_body = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@ng-if='!vm.data.questionAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"
                ))
            )
            editable_body.send_keys("po fib create q self-assessment automation don't use\n int(1234) ")

            # Create blank
            create_blank_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Create Blank')]"))
            )
            create_blank_button.click()

            # Select "Answer Type"
            answer_type_dropdown = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//input[@placeholder="Answer Type"]/following-sibling::div/button'))
            )
            answer_type_dropdown.click()

            # Choose "Distinct" from the dropdown
            category_menu = wait.until(
                EC.visibility_of_element_located((
                    By.XPATH, '//*[@class = "dropdown-menu ng-scope am-fade bottom-left"]'
                ))
            )
            if category_menu.is_displayed():
                distinct_option = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@title='Distinct']"))
                )
                distinct_option.click()
            else:
                print("Answer type dropdown not visible.")

            # Enter the answer
            answer_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Single Answer']"))
            )
            answer_field.send_keys("1234")

            # Confirm answer addition
            confirm_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-sm btn-primary']"))
            )
            confirm_button.click()

            # Add explanation
            explanation_field = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@ng-if='!vm.data.explanationAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"
                ))
            )
            explanation_field.send_keys("Notes sample Data c\n !@#$%^&*()_+-=094521;',.?/ ")

            # Scroll to the "Save" button and click
            save_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-default btn-success btn-sm ng-scope"]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            save_button.click()

            print("FIB question created successfully.")
            return 'SUCCESS'

        except StaleElementReferenceException as stale_err:
            print(f"Stale element encountered: {stale_err}")
            return 'FAILED'

        except TimeoutException as timeout_err:
            print(f"Timeout while creating FIB question: {timeout_err}")
            return 'FAILED'

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 'FAILED'

    def create_mca_q(self):
        try:
            print("Creating mca question...")
            self_assessment_obj.add_new_section()
            wait = WebDriverWait(self.driver, 20)
            mca_sec = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Multiple Correct Answer Section']")))
            mca_sec.click()
            time.sleep(1)

            self_assessment_obj.select_plus('Multiple Correct Answer')
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "tab-option"]'))
            ).click()
            self_assessment_obj.select_question_attributes()
            self.driver.find_element(By.XPATH, "//i[@class='fa fa-fw fa-text-width']").click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Question Description']"))
            ).send_keys("po mca create q sa automation don't use /ans : B , C ")

            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//textarea[@class='form-control ng-pristine ng-untouched ng-valid ng-empty']"))
            )
            for idx, e in enumerate(elements, start=1):
                e.send_keys(str(idx))
            options = self.driver.find_elements(By.XPATH, "//input[@type='checkbox' and @title='select answer']")
            options[1].click()
            options[2].click()
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[@ng-if='!vm.data.explanationAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"))
            ).send_keys(" Notes sample Data c\n !@#$%^&*()_+-=094521;',.?/ ")
            time.sleep(1)

            WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-default btn-success btn-sm ng-scope"]'))
            ).click()
            time.sleep(2)
            return 'SUCCESS'

        except Exception as e:
            print(f"Exception occurred while creating MCA q : {e}")
            return 'FAILED'

    def create_mcqww_q(self):
        try:
            print("Creating mcq with weightage question...")
            self_assessment_obj.add_new_section()
            wait = WebDriverWait(self.driver, 20)
            mca_sec = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='MCQ With Weightage Section']")))
            mca_sec.click()
            time.sleep(1)

            self_assessment_obj.select_plus('MCQWithWeightage')
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "tab-option"]'))
            ).click()
            self_assessment_obj.select_question_attributes()
            self.driver.find_element(By.XPATH, "//i[@class='fa fa-fw fa-text-width']").click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Question Description']"))
            ).send_keys("po mcqww create q sa automation don't use /ans : B : 100 , C : 50")

            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//textarea[@class='form-control ng-pristine ng-untouched ng-valid ng-empty']"))
            )
            for idx, e in enumerate(elements, start=1):
                e.send_keys(str(idx))
            options = self.driver.find_elements(By.XPATH, "//input[@type='checkbox' and @title='select answer']")
            options[1].click()
            options[2].click()

            options_value = self.driver.find_elements(By.XPATH, "//input[@type='number' and @max='100' and @min='0']")
            options_value[1].send_keys(100)
            options_value[2].send_keys(50)
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[@ng-if='!vm.data.explanationAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"))
            ).send_keys(" Notes sample Data c\n !@#$%^&*()_+-=094521;',.?/ ")
            time.sleep(1)

            WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-default btn-success btn-sm ng-scope"]'))
            ).click()
            time.sleep(2)
            return 'SUCCESS'

        except Exception as e:
            print(f"Exception occurred while creating MCQww q : {e}")
            return 'FAILED'

    def add_test_case(self, input_data):
        WebDriverWait(self.driver, 120).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
        )
        self.driver.find_element(By.XPATH, "//textarea[@ng-model='language.inputTestCase']").send_keys(
            input_data)
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Execute']").click()
        save_testcase = WebDriverWait(self.driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save Test Case']"))
        )
        save_testcase.click()

    def create_coding_q(self):
        try:
            print("Creating coding question...")
            self_assessment_obj.add_new_section()
            wait = WebDriverWait(self.driver, 20)
            add_sec = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Coding Section']"))
            )
            add_sec.click()
            time.sleep(1)

            self_assessment_obj.select_plus('Coding')
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "tab-option"]'))
            ).click()
            self_assessment_obj.select_question_attributes()
            self.driver.find_element(By.XPATH, "//textarea[@placeholder='Problem Title']").send_keys(
                "po coding create q sa automation don't use")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//div[@ng-if='!vm.data.questionAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']")
                )
            ).send_keys("po coding create q sa automation don't use \n c program to add 2 numbers")

            # Select C language
            c_lang = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[normalize-space()='C']")
                )
            )
            c_lang.click()

            # Enter master answer
            master_answer = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@ng-model=\"language.masterAnswer\"]//textarea[@role='textbox']")
                )
            )
            master_answer.send_keys(''' 
            #include <stdio.h>
            int main() {    
                int number1, number2, sum;
                scanf("%d %d", &number1, &number2);
                sum = number1 + number2;      
                printf("%d + %d = %d", number1, number2, sum);
                return 0;
            }
             ''')
            self.driver.find_element(By.XPATH, "//span[normalize-space()='Test Cases']").click()
            self.add_test_case("2363\n4378")
            self.add_test_case("3456\n4588")
            self.add_test_case("8427\n1467")
            self.add_test_case("64225\n12367")
            self.add_test_case("86867\n90467")
            print("test cases added")
            time.sleep(1)

            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            self.driver.find_element(By.CSS_SELECTOR, "input[title='Mark as sample']").click()
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[@ng-if='!vm.data.explanationAsText']//div[@class='se-wrapper-inner se-wrapper-wysiwyg sun-editor-editable']"))
            ).send_keys(" Notes sample Data c\n !@#$%^&*()_+-=094521;',.?/ ")
            time.sleep(1)

            WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default btn-success btn-sm ng-scope']"))
            ).click()

            time.sleep(2)
            return 'SUCCESS'

        except Exception as e:
            print(f"Exception occurred while creating coding q : {e}")
            return 'FAILED'

    def add_q_local(self, question_id, section_name):
        try:
            print("Adding question from my question library...")

            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            self_assessment_obj.select_plus(section_name)

            # Wait until the loading overlay disappears
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Wait for the input field to be visible
            qid = WebDriverWait(self.driver, 130).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Eg: 1234, 2312,...']"))
            )
            qid.clear()  # Optional: Clear the field before entering a new question ID
            qid.send_keys(question_id)

            # Wait for the search button to be clickable and click it
            search = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary_ pull-right']"))
            )
            search.click()

            # Wait for the loading overlay to disappear after search
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Wait for the question checkbox to be clickable and select it
            select_q = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.NAME, 'grid_items'))
            )
            select_q.click()

            # Wait for the 'Save and Continue' button to be clickable and click it
            save_and_continue = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-success_ pull-right']"))
            )
            save_and_continue.click()

            # Wait a bit for the action to complete before finishing
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            print("Question added successfully.")
            return 'SUCCESS'

        except TimeoutException as te:
            print(f"TimeoutException occurred: {te}")
            return 'FAILED'

        except NoSuchElementException as nse:
            print(f"NoSuchElementException occurred: {nse}")
            return 'FAILED'

        except Exception as e:
            print(f"Exception occurred while adding question local: {e}")
            return 'FAILED'

    def add_rtc_local(self , section_name):
        try:
            print("Adding rtc question from my question library")

            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            self_assessment_obj.select_plus(section_name)
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            qid = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Eg: 1234, 2312,...']"))
            )
            qid.send_keys("141427")
            search = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary_ pull-right']"))
            )
            search.click()
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            select_q = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.NAME, 'grid_items'))
            )
            select_q.click()
            time.sleep(1)
            save_and_continue = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-success_ pull-right']"))
            )
            save_and_continue.click()
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            time.sleep(5)
            final_confirm_button = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-success pull-right']"))
            )
            final_confirm_button.click()
            return 'SUCCESS'

        except Exception as e:
            print(f"Exception occurred while adding question rtc local: {e}")
            return 'FAILED'

    def add_q_hirepro(self, question_id, section_name):
        try:
            print("Adding question from Hirepro tenant")
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            self_assessment_obj.select_plus(section_name)
            # Wait for any loading overlay to disappear
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Click on 'Hirepro Library' tab
            hirepro_library_tab = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Hirepro Library")]'))
            )
            hirepro_library_tab.click()
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Enter Question ID
            qid_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@type="text"]'))
            )
            qid_input.clear()
            qid_input.send_keys(question_id)

            # Click on 'Search' button
            search_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-primary_ pull-right"]'))
            )
            search_button.click()

            # Wait for loading overlay to disappear
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Select the question from search results
            select_question_checkbox = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@name="grid_items"]'))
            )
            select_question_checkbox.click()
            # Wait for any loading overlay
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Click on 'Save and Continue'
            save_and_continue_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-success_ pull-right']"))
            )
            save_and_continue_button.click()
            # Wait for loading overlay to disappear
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Success message
            print("Question added successfully")
            return 'SUCCESS'

        except TimeoutException as e:
            print(f"TimeoutException occurred while adding question: {e}")
            self.driver.save_screenshot("timeout_exception_screenshot.png")
            return 'FAILED'
        except Exception as e:
            print(f"Exception occurred while adding question hirepro: {e}")
            self.driver.save_screenshot("exception_screenshot.png")
            return 'FAILED'

    def add_rtc_hirepro(self, section_name):
        try:
            print("Adding RTC question from Hirepro tenant")

            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            self_assessment_obj.select_plus(section_name)

            # Wait for any loading spinners to disappear
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Click 'Hirepro Library'
            hirepro_library = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Hirepro Library")]'))
            )
            hirepro_library.click()

            # Wait for any loading spinners to disappear
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Enter QID
            qid_input = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@type="text"]'))
            )
            qid_input.send_keys("141417")

            # Click 'Next' (or primary button)
            next_button = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-primary_ pull-right"]'))
            )
            next_button.click()

            # Wait for loading to disappear
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Select an item from the grid
            grid_item = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@name="grid_items"]'))
            )
            grid_item.click()

            # Click 'Submit'
            submit_button = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class = "btn btn-success_ pull-right"]'))
            )
            submit_button.click()

            # Wait for loading to disappear
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            # Final confirmation
            confirm_button = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@class="btn btn-success pull-right"]'))
            )
            confirm_button.click()

            print("RTC question added successfully.")
            return 'SUCCESS'

        except TimeoutException as e:
            print(f"Timeout occurred: {e}")
        except StaleElementReferenceException as e:
            print(f"Stale element reference error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while adding rtc q hirepro: {e}")

        return 'FAILED'

    def add_new_section(self):
        try:
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            # print("Loading overlay disappeared.")
            time.sleep(2)
            add_section = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//strong[text()='Add Section']")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", add_section)
            self.driver.execute_script("arguments[0].click();", add_section)

        except Exception as e:
            print(f"Error during add_new_section: {e}")

    def activate_test(self):
        try:
            print("Test Activation")
            wait = WebDriverWait(self.driver, 120)
            # Wait until loading is complete
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
            time.sleep(2)
            # Retry logic for finding the element if it is stale
            attempt = 0
            while attempt < 3:
                try:
                    activate_test_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Activate test']"))
                    )
                    # Try clicking the button
                    self.driver.execute_script("arguments[0].click();", activate_test_button)
                    break  # Exit retry loop if successful
                except StaleElementReferenceException:
                    attempt += 1
                    print(f"Stale element encountered, retrying... Attempt {attempt}")
                    if attempt >= 3:
                        raise Exception("Failed to click 'Activate test' after 3 attempts")
                except Exception as e:
                    print(f"Unexpected error: {str(e)}")
                    raise
            # Wait for the success message
            growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
            growl_message = wait.until(EC.visibility_of_element_located(growl_message_locator))
            print(growl_message.text)

            if growl_message.text == 'Test is active now.':
                test_status = 'SUCCESS'
            else:
                test_status = 'FAILED'
        except Exception as e:
            print(f"Error while activating test: {str(e)}")
            raise  # Re-raise the exception to capture the full stack trace
        return test_status

    def invite_candidate(self):
        try:
            print("Candidate invitation")
            # wait = WebDriverWait(self.driver, 20)
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            invite_candidate_tab = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Invite Candidate']")))
            self.driver.execute_script("arguments[0].click();", invite_candidate_tab)

            WebDriverWait(self.driver, 40).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )
            # print("Loading overlay disappeared.")
            self.driver.find_element(By.XPATH, "//textarea[@type='text']").send_keys(
                "qatesthirepro@gmail.com automation_selfassessment cand 5829372829")
            time.sleep(2)
            invite_candidate = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Invite Candidate']")))
            # self.driver.execute_script("arguments[0].scrollIntoView(true);", add_section)
            self.driver.execute_script("arguments[0].click();", invite_candidate)
            # time.sleep(1)

            growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
            growl_message = WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located(growl_message_locator))
            print(growl_message.text)
            invite_status = 'SUCCESS'
            # if growl_message.text == 'Candidate invitation is in progress. Please check the invitation details below.':
            #     invite_status = 'SUCCESS'
            # else :
            #     invite_status = 'FAILED'
            time.sleep(2)
        except Exception as e:
            print(f"Error while inviting candidate: {e}")
            invite_status = 'FAILED'
        return invite_status

    def update_test(self):
        update_test_status = 'FAILED'
        try:
            print("Update Test")
            wait = WebDriverWait(self.driver, 120)

            test_settings = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Test Settings']")))
            self.driver.execute_script("arguments[0].click();", test_settings)
            wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            self.driver.find_element(By.XPATH, "//label[contains(text(),'Shuffle Questions')]/following-sibling::div//label[contains(@class, 'btn-sm') and contains(., 'Off')]").click()
            self.driver.find_element(By.XPATH, "//label[contains(text(),'Instant Evaluation')]/following-sibling::div//label[contains(@class, 'btn-sm') and contains(., 'On')]").click()
            self.driver.find_element(By.XPATH, "//label[contains(text(),'Allow Copy/Paste in Answers')]/following-sibling::div//label[contains(@class, 'btn-sm') and contains(., 'On')]").click()
            self.driver.find_element(By.XPATH, "//label[contains(text(),'Restrict Navigation from Test')]/following-sibling::div//label[contains(@class, 'btn-sm') and contains(., 'Off')]").click()
            self.driver.find_element(By.XPATH, "//label[contains(text(),'Choose Proctoring Mode')]/following-sibling::div//label[contains(@class, 'btn-sm') and contains(., 'Off')]").click()

            update_test = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Update')]")))
            self.driver.execute_script("arguments[0].click();", update_test)

            wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active"))
            )

            growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
            growl_message = wait.until(EC.visibility_of_element_located(growl_message_locator))
            print(growl_message.text)
            if growl_message.text == 'Test updated successfully.':
                update_test_status = 'SUCCESS'
            else :
                update_test_status = 'FAILED'
            time.sleep(2)
        except Exception as e:
            print(f"Error while updating test: {e}")
        return update_test_status

    def attend_test(self, test_name):
        start_test_status = "Not Started"
        end_test_status = "Not Ended"
        try:
            wait = WebDriverWait(self.driver, 180)
            print("Attend test module")

            # Moving to Assessment applicants page
            self_assessment_obj.view_candidates_page(test_name)

            self.driver.find_element(By.XPATH, "//div[contains(text(),'View Test Link')]").click()

            test_link = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[contains(text(),'https://amsin.hirepro.in/assessment/#/assess/lo')]")))

            test_link.click()
            self.driver.switch_to.window(self.driver.window_handles[-1])

            print("New tab title:", self.driver.title)

            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))

            # Handle test agreement and starting the test
            i_agreed = self_assessment_obj.select_i_agree()
            if i_agreed:
                start_test_status = self_assessment_obj.start_test()
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))

                # Answer the questions and end the test
                self_assessment_obj.select_answer_generic()
                self_assessment_obj.end_test()
                end_test_status =self_assessment_obj.end_test_confirmation()

                time.sleep(5)

        except Exception as e:
            print(f"Error while attending test: {e}")

        # Return start and end test status
        return start_test_status, end_test_status

    def select_answer_generic(self):
        try:
            time.sleep(2)

            # RTC
            self_assessment_obj.select_answer_for_the_question('A')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('B')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('C')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('D')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('')
            self_assessment_obj.next_question()
            # MCQ
            self_assessment_obj.select_answer_for_the_question('B')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('C')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('')
            self_assessment_obj.next_question()
            # FIB
            self_assessment_obj.select_answer_for_fib_question('')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_fib_question('Answer@2')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_fib_question('-4634.26')
            self_assessment_obj.next_question()
            # MCA
            self_assessment_obj.select_answer_for_mca_question('1,2')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_mca_question('')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_mca_question('0,2')
            self_assessment_obj.next_question()
            # MCQWW
            self_assessment_obj.select_answer_for_the_question('B')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('C')
            self_assessment_obj.next_question()
            self_assessment_obj.select_answer_for_the_question('D')
            self_assessment_obj.next_question()
            # coding

            self_assessment_obj.send_answer_for_coding_question(''' 
        #include <stdio.h>
        int main() {    
        
        int number1, number2, sum;
        
        scanf("%d %d", &number1, &number2);
        
        // calculate the sum
        sum = number1 + number2;      
        
        printf("%d + %d = %d", number1, number2, sum);
        return 0;
        }
        ''')
            time.sleep(1)
            self.driver.find_element(By.XPATH,"//button[normalize-space()='Run Tests']").click()
            time.sleep(5)
            self_assessment_obj.next_question()
            self_assessment_obj.send_answer_for_coding_question(''' 
        import java.util.Scanner;
        
        public class TestClass {
        
        public static void main(String[] args) {
        
        Scanner reader = new Scanner(System.in);
        
        System.out.print("Enter a number: ");
        int num = reader.nextInt();
        
        if(num % 2 == 0)
        System.out.println(num + " is even");
        else
        System.out.println(num + " is odd number");
        }
        }
        ''')
            time.sleep(1)
            self.driver.find_element(By.XPATH, "//button[normalize-space()='Submit & Continue Coding']").click()
            time.sleep(5)

            self_assessment_obj.next_question()
            self_assessment_obj.send_answer_for_coding_question(''' 
             # Python program to check if the number is an Armstrong number or not
        
        # take input from the user
        num = int(input(""))
        
        # initialize sum
        sum = 0
        
        # find the sum of the cube of each digit
        temp = num
        while temp > 0:
        digit = temp % 10
        sum += digit ** 3
        temp //= 10
        
        # display the result
        if num == 8:
        print("Is the given number armstrong yes :  True")
        elif num == sum:
        print("Is the given number armstrong yes :  True")
        else:
        print("Is the given number armstrong no :  False")
        
             ''')
            time.sleep(1)
            self_assessment_obj.next_question()

            # subjective
            self_assessment_obj.send_answer_for_qa_question("I am very foodie. I love to eat. Among the number of foods, Pizza is my favourite food because it tastes and smells fabulous. My Mom cooks the best Pizzas in the world. I always ask her to make Pizza. In Pizzas, I love onion cheese Pizza a lot. This is because cheese pizza is healthy and makes me strong. To create fun we also organize pizza races in terms of who can eat the maximum number of pizzas. I can eat many pizzas at a time.")
            self_assessment_obj.next_question()
            self_assessment_obj.send_answer_for_qa_question(
                "I am very foodie. I love to eat. Among the number of foods, Pizza is my favourite food because it tastes and smells fabulous. My Mom cooks the best Pizzas in the world. I always ask her to make Pizza. In Pizzas, I love onion cheese Pizza a lot. This is because cheese pizza is healthy and makes me strong. To create fun we also organize pizza races in terms of who can eat the maximum number of pizzas. I can eat many pizzas at a time.")
            self_assessment_obj.next_question()
            self_assessment_obj.send_answer_for_qa_question('')

        except Exception as e:
            print(f"Error while answering questions : {e}")

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

    def start_test(self):
        # time.sleep(1)
        self.driver.find_element(By.NAME, 'btnStartTest').click()
        return 'Test Started'

    def select_answer_for_the_question(self, answer):
        time.sleep(1)
        if not answer:
            return
        value = "//input[@name='answerOptions' and @value='%s']" % answer
        answered = self.driver.find_element(By.XPATH, value)
        is_answered = answered.is_selected()
        if not is_answered:
            answered.click()

    def select_answer_for_fib_question(self, answer):
        if answer:
            value = "//input[@placeholder = 'Blank']"
            elem = self.driver.find_element(By.XPATH, value)
            self.driver.implicitly_wait(10)
            ActionChains(self.driver).move_to_element(elem).send_keys_to_element(elem, answer).perform()
        else:
            pass

    def select_answer_for_mca_question(self, answer):
        # If user wants to select one or more options then If condition will work other wise else will pass the stmt.
        if answer:
            # user can choose n number of options, options be passed as string and comma separated
            # below split will split the string by using comma and will make a list.
            answer_choices = answer.split(',')
            for options in answer_choices:
                # strip is necessary to remove the leading and trailing space of each option.
                options = options.strip()
                # elem = self.driver.find_element_by_xpath('//*[@id="option2"]')
                value = '//*[@id="option%s"]' % options
                # elem = self.driver.find_element_by_xpath(value)
                elem = self.driver.find_element(By.XPATH, value)
                self.driver.implicitly_wait(10)
                ActionChains(self.driver).move_to_element(elem).click(elem).perform()
        else:
            # User does not want to select any option, so pass the stmt.
            pass

    def send_answer_for_coding_question(self, answer):
        if answer:
            # Locate the editor container
            editor_container = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ace_editor')]")

            # Use JavaScript to set the content
            script = """
            var editor = ace.edit(arguments[0]);
            editor.setValue(arguments[1]);
            """
            self.driver.execute_script(script, editor_container, answer)

            # elem = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ace_editor')]//textarea")
            # self.driver.implicitly_wait(10)
            # ActionChains(self.driver).move_to_element(elem).send_keys(answer)

        else:
            # User does not want answer, so pass the stmt.
            pass

    def send_answer_for_qa_question(self, answer):
        if answer:
            try:
                # Wait for the textarea to be clickable
                elem = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//textarea[@name='qaTextArea' and @ng-model='vm.question.selectedAns']")
                    )
                )

                # Clear any pre-existing text (if necessary)
                elem.send_keys(Keys.CONTROL + "a")  # Select all text
                elem.send_keys(Keys.BACKSPACE)  # Clear selected text

                # Send the new answer to the textarea
                elem.send_keys(answer)
                # print("Answer sent successfully.")

                # Capture image for subjective question (if implemented)
                self_assessment_obj.capture_img_subjective()
                WebDriverWait(self.driver, 60).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "block-ui-overlay"))
                )
                # print("Captured image.")

                # Upload file (if needed)
                self_assessment_obj.upload_file()
                WebDriverWait(self.driver, 60).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "block-ui-overlay"))
                )
                # print("File uploaded.")

            except Exception as e:
                print(f"Error while sending answer: {e}")
        else:
            print("No answer provided.")

    def capture_img_subjective(self):
        wait = WebDriverWait(self.driver, 20)
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Add New']").click()
        time.sleep(5)
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Take Picture']").click()
        time.sleep(2)
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Save & Proceed']").click()
        growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
        growl_message = wait.until(EC.visibility_of_element_located(growl_message_locator))
        print(growl_message.text)
        time.sleep(2)

    def upload_file(self):
        try:
            wait = WebDriverWait(self.driver, 20)
            time.sleep(1)
            # Locate the file input element
            upload_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            # Path to the file to be uploaded
            file_path = 'D:/automation_new/ASSESSMENT/PythonWorkingScripts_InputData/UI/Assessment/self_assessment.xls'
            # Send the file path to the input element
            upload_input.send_keys(file_path)
            # Wait for growl message and print it
            growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
            growl_message = wait.until(EC.visibility_of_element_located(growl_message_locator))
            print(f"Growl message displayed: {growl_message.text}")

            time.sleep(2)

        except Exception as e:
            print(f"Exception occurred while uploading the file: {e}")

    def check_answered_status(self, previous_answer):
        value = "//input[@name='answerOptions' and @value='%s']" % previous_answer
        answered = self.driver.find_element(By.XPATH, value).is_enabled()
        return answered

    def next_question(self):
        # time.sleep(1)
        # value = "btnQuestionIndex%s" % str(question_index)
        self.driver.find_element(By.NAME, 'btnNextQuestion').click()

    def start_test_button_status(self):
        # time.sleep(1)
        is_enabled = self.driver.find_element(By.NAME, 'btnStartTest').is_enabled()
        if is_enabled:
            start_button_status = 'Enabled'
        else:
            start_button_status = 'Disabled'
        return start_button_status

    def end_test(self):
        try:
            time.sleep(3)  # Give the page some time to settle
            # Find and click the 'End Test' button
            self.driver.find_element(By.XPATH, "//button[@class='btn btn-danger ng-scope']").click()
            print('Clicked on End test')
        except Exception as e:
            print(f"Error during end test click: {e}")

    def end_test_confirmation(self):
        try:
            time.sleep(5)
            self.driver.find_element(By.NAME, 'btnCloseTest').click()
            print("Test is ended Successfully")
            return 'Test Ended Successfully'
        except Exception as e:
            print(f"Error during final end test: {e}")
            return 'Test End Failed'

    def view_candidates_page(self, test_name):
        try:
            wait = WebDriverWait(self.driver, 180)
            time.sleep(3)
            print("Moving to assessment applicants page")
            self.driver.refresh()
            # Wait for loading to disappear and ensure the "Assessments" link is clickable
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Assessments']"))).click()
            # Wait for loading to disappear again
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
            # Click the filter
            click_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='cardlist-view-filter']")))
            self.driver.execute_script("arguments[0].click();", click_filter)
            # Wait for input field and enter test name
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Test Name']"))).send_keys(
                test_name)
            # Wait for button to be clickable and submit
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))).click()
            # Wait for the next page to load
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
            # Click on View candidates
            wait.until(EC.element_to_be_clickable((By.XPATH, "//i[@class='ng-scope fa fa-fw fa-users fa-lg']"))).click()

            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
            # Click on more options
            self.driver.find_element(By.XPATH, "//a[@class='pointer fa fa-lg fa-ellipsis-v']").click()
            time.sleep(1)

        except Exception as e:
            print(f"Error while moving to assessment applicants page : {e}")
            eval_status = 'FAILED'

    def manual_evaluation(self, test_name):
        try:
            eval_status = 'FAILED'
            wait = WebDriverWait(self.driver, 180)
            print("Manual Evaluation")

            self.driver.switch_to.window(self.driver.window_handles[0])

            # Wait for loading to disappear and ensure the "Assessments" link is clickable
            self_assessment_obj.view_candidates_page(test_name)

            self.driver.find_element(By.XPATH, "//div[contains(text(),'Evaluate Manually')]").click()

            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))

            elements = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//h5[@class='list-group-item-heading']//div//div[@class='ng-scope']")
            ))
            # time.sleep(2)
            # print(len(elements))

            # Iterate over the elements
            for index, element in enumerate(elements, start=1):
                # Scroll to the element to make sure it's in view
                # self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                # Click on the element
                element.click()
                self_assessment_obj.save_score_manual(1)


            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
            status_element = self.driver.find_element(By.XPATH,
                                                      "//div[@ng-if and contains(@ng-if, 'vm.data.testConfigs.isInstantEvaluation')]//span[@class='ng-binding']")
            status = status_element.text
            print(f"Status: {status}")
            # status = self.driver.find_element(By.XPATH,"div[ng-if='!(vm.data.testConfigs.isInstantEvaluation && vm.data.testConfigs.isAnyVideoQuestion)'] span[class='ng-binding']").text
            # print(status)
            time.sleep(2)
            if status == 'Evaluated' :
                eval_status = 'SUCCESS'

        except Exception as e:
            print(f"Error in manual evaluation : {e}")
            eval_status = 'FAILED'

        return eval_status

    def save_score_manual(self, mark):
        try:
            wait = WebDriverWait(self.driver, 180)
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))

            # Locate the input field
            input_element = self.driver.find_element(By.XPATH, "//input[@type='number']")

            # Check if input field is enabled
            if not input_element.is_enabled():
                print("Answer not available.")
                return

            # Clear the input field and enter the score
            input_element.clear()
            input_element.send_keys(mark)
            print("Score entered successfully.")

            # Locate the save button
            button = self.driver.find_element(By.XPATH,
                                              "//button[@class='btn btn-primary btn-sm' and contains(@ng-click, 'saveSubjectiveScore')]")

            # Handle any potential obstructing elements
            try:
                overlay = self.driver.find_element(By.XPATH,
                                                   "//div[contains(@class, 'container') and @style='position: relative;z-index: 100;']")
                self.driver.execute_script("arguments[0].style.display = 'none';", overlay)
                print("Obstructing overlay removed.")
            except NoSuchElementException:
                print("No obstructing overlay found.")

            # Scroll and click the button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)  # Small delay to ensure visibility
            if button.is_enabled():
                try:
                    button.click()
                    print("Save button clicked.")
                except WebDriverException:
                    # Use JavaScript if normal click fails
                    self.driver.execute_script("arguments[0].click();", button)
                    print("Save button clicked using JavaScript.")
            else:
                print("Save button is disabled.")
                return

            # Wait for growl message
            growl_message_locator = (By.XPATH, "//div[@class='growl-message ng-binding']")
            growl_message = wait.until(EC.visibility_of_element_located(growl_message_locator))
            print(f"Evaluation status: {growl_message.text}")

            # Wait for loading to complete
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))
            time.sleep(5)

        except Exception as e:
            print(f"Error in save_score_manual: {e}")

    def get_score_percentage(self, test_name):
        score = 0
        percentage = 0
        try:
            wait = WebDriverWait(self.driver, 180)
            print("fetching score")

            # Wait for loading to disappear and ensure the "Assessments" link is clickable
            self_assessment_obj.view_candidates_page(test_name)

            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))

            elements = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//span[@title and not(@title='') and number(@title)]")
            ))
            score = elements[2].text
            percentage = elements[3].text
            # for index, element in enumerate(elements, start=1):
            #     print(element.text)

            print(score)
            print(percentage)

        except Exception as e:
            print(f"Error in fetching score and percentage : {e}")

        return score,percentage



self_assessment_obj = SelfAssessmentLogin()
