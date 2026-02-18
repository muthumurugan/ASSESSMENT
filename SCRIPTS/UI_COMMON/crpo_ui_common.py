import time
import traceback
import platform

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class CrpoCommon:
    def __init__(self):
        self.delay = 120
        self.os_name = platform.system()
        print(self.os_name)

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

    def move_to_manage_actions_page(self , url):
        # chrome option is needed in VET cases - ( its handling permissions like mic access)
        self.wait_for_page_load(40)
        self.driver.get(url)
        print("moved to manage actions")
        self.driver.implicitly_wait(10)

    def select_and_save_all_actions(self):
        try:
            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")

            # Check all checkboxes
            for checkbox in checkboxes:
                if not checkbox.is_selected():  # Only check if it's not already checked
                    checkbox.click()
            save = self.driver.find_element(By.XPATH,"//span[@class='pull-right']//button[@type='button'][normalize-space()='Save']")
            self.driver.execute_script("arguments[0].scrollIntoView();", save)
            self.driver.execute_script("arguments[0].click();", save)
            print("Successfully Enabled all actions")


        except Exception as e:
            print(f"Error occurred while enabling checkboxes: {e}")

    def ui_login_to_crpo(self, user_name, password):
        self.wait_for_page_load()
        self.driver.find_element(By.NAME, 'loginName').clear()
        self.driver.find_element(By.NAME, 'loginName').send_keys(user_name)
        self.driver.find_element(By.XPATH, "//input[@type='password']").clear()
        self.driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
        self.driver.find_element(By.XPATH,
                                 '//*[@class = "btn btn-default button_style login ng-binding"]').click()

    def wait_for_page_load(self, timeout=60):
        """Waits until the page loading spinner disappears to ensure UI is ready."""
        try:
            wait = WebDriverWait(self.driver, timeout)  # Default timeout reduced to 15s for efficiency
            loading_elements = self.driver.find_elements(By.CLASS_NAME, "dw-loading-active")

            if loading_elements:
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))

            # if self.driver.find_elements(By.CLASS_NAME, "dw-loading-active"):
            #     wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dw-loading-active")))

        except TimeoutException:
            print("⚠️ Warning: Page load took too long or never completed.")
        except Exception as e:
            print(f"❌ Error while waiting for page load: {str(e)}")
            traceback.print_exc()

    def click_on_filter_button(self):
        """Clicks on the filter button after ensuring the page is ready."""
        try:
            wait = WebDriverWait(self.driver, 10)
            self.wait_for_page_load()
            # Click filter button if present
            filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='cardlist-view-filter']")))
            self.driver.execute_script("arguments[0].click();", filter_button)

        except TimeoutException:
            print("⚠️ Warning: Filter button not found or took too long to load.")
        except Exception as e:
            print(f"❌ Error clicking on filter button: {str(e)}")
            traceback.print_exc()

    def click_on_more_option(self):
        """Clicks on the 'More Options' (three dots) menu safely and efficiently."""
        try:
            wait = WebDriverWait(self.driver, 20)  # Reduced timeout for better efficiency
            crpo_ui_obj.wait_for_page_load()
            # Find and click on more options
            more_options = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='pointer fa fa-lg fa-ellipsis-v']"))
            )
            self.driver.execute_script("arguments[0].click();", more_options)

        except TimeoutException:
            print("⚠️ Warning: 'More Options' button not found or took too long to load.")
        except Exception as e:
            print(f"❌ Error clicking on 'More Options': {str(e)}")
            traceback.print_exc()

    def filter_search_by_id(self , value):
        try:
            wait = WebDriverWait(self.driver, 10)
            if isinstance(value, (int, str)):
                value = [value]

            id_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='ID,ID,ID...']")))
            id_box.clear()

            # Ensure all elements in value are strings
            id_box.send_keys(" ".join(map(str, value)))

            # id_box.send_keys(value)
            button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(2)

        except Exception as e:
            print("Error while searching by id : ", e)

    def filter_search_by_interview_bot_id(self , value):
        try:
            wait = WebDriverWait(self.driver, 10)
            if isinstance(value, (int, str)):
                value = [value]

            id_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='ID,ID,ID, ...']")))
            id_box.clear()

            # Ensure all elements in value are strings
            id_box.send_keys(" ".join(map(str, value)))

            # id_box.send_keys(value)
            button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)

        except Exception as e:
            print("Error while searching by id : ", e)

    def filter_search_by_id_authoring(self, value):
        try:
            wait = WebDriverWait(self.driver, 15)  # Reduced wait time for efficiency

            # Find input box
            id_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[text()='Id '] /following-sibling::input[@type='text']"))
            )
            id_box.clear()

            # Ensure all elements in value are strings
            id_box.send_keys(" ".join(map(str, value)))

            # Find and click the search button
            button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))
            )

            # Scroll and click the button
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)

        except Exception as e:
            print(f"Error while searching by ID: {e}")

    def filter_search_by_single_id_authoring(self, value):
        try:
            wait = WebDriverWait(self.driver, 15)  # Reduced wait time for efficiency

            # Find input box
            id_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[text()='Id '] /following-sibling::input[@type='text']"))
            )
            id_box.clear()

            # Ensure all elements in value are strings
            id_box.send_keys(value)

            # Find and click the search button
            button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))
            )

            # Scroll and click the button
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)

        except Exception as e:
            print(f"Error while searching by ID: {e}")

    def filter_search_by_test_user_id(self , value):
        try:
            wait = WebDriverWait(self.driver, 10)

            # Wait for input field and enter test user id
            test_user_id_box = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Test User Id(s) '] /following-sibling::input[@type='text']")))
            test_user_id_box.clear()
            test_user_id_box.send_keys(" ".join(map(str, value)))

            # test_user_id_box.send_keys(value)
            button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(2)

        except Exception as e:
            print("Error while searching by test user id :",e)

    def filter_search_by_candidate_id(self , value):
        try:
            wait = WebDriverWait(self.driver, 10)

            # Wait for input field and enter test user id
            test_user_id_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='CandidateIds']")))
            test_user_id_box.clear()
            test_user_id_box.send_keys(" ".join(map(str, value)))

            # test_user_id_box.send_keys(value)
            button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(2)

        except Exception as e:
            print("Error while searching by test user id :",e)

    def filter_search_by_id_authoring_bot(self, value):
        try:
            wait = WebDriverWait(self.driver, 10)

            # Wait for input field and enter ID(s)
            id_box = wait.until(EC.presence_of_element_located((By.XPATH, "*//input[@name='Ids']")))
            id_box.clear()

            # ✅ Handle single value or list/tuple of IDs
            if isinstance(value, (list, tuple)):
                id_box.send_keys(" ".join(map(str, value)))
            else:
                id_box.send_keys(str(value))

            # Find and click the filter/search button
            button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary ng-binding']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)

        except Exception as e:
            print("Error while searching by id interview bot authoring:", e)

    def fetch_grid_actions(self, filter_function=None,
                           xpath="//div[@class='popover-content card-actions']/div") -> list:
        """Fetch grid actions from the assessment UI."""
        try:
            time.sleep(1)
            # Apply filter if provided
            if filter_function:
                filter_function()

            actions = self.driver.find_elements(By.XPATH, xpath)
            return [action.text for action in actions]

        except Exception as e:
            print(f"Error in fetching grid actions: {e}")
            return []

    def fetch_bp_grid_actions(self):
        try:
            action_list = []
            time.sleep(1)

            # Locate all action elements inside 'td.td-last.ng-scope'
            actions = self.driver.find_elements(By.CSS_SELECTOR, "td.td-last.ng-scope a")

            for action in actions:
                action_text = action.text.strip()  # Extract visible text

                if not action_text:
                    try:
                        icon_element = action.find_element(By.TAG_NAME, "i")
                        icon_class = icon_element.get_attribute("class")

                        # Map icon class to meaningful names
                        icon_map = {
                            "fa fa-fw fa-eye": "View History Json",
                            "fa fa-fw fa-expand": "Extend Search",
                            "fa fa-fw fa-pencil-square-o": "Edit",
                            "fa fa-fw fa-trash": "Delete"
                        }

                        action_text = icon_map.get(icon_class, "Unknown Action")
                    except Exception:
                        action_text = "Unknown Action"

                action_list.append(action_text)

            return action_list  # Return cleaned action labels

        except Exception as e:
            print(f"Error fetching actions: {e}")
            return []

    def move_to_next_tab(self ):
        try:
            wait = WebDriverWait(self.driver, 10)
            self.wait_for_page_load()
            wait.until(lambda d: len(d.window_handles) > 1)
            self.driver.switch_to.window(self.driver.window_handles[1])

        except Exception as e:
            print(f"❌ Error while moving to next tab ' {str(e)}")
            traceback.print_exc()

    def move_to_previous_tab(self ):
        try:
            first_tab = self.driver.window_handles[0]

            # Step 2: Get current tab handle
            current_tab = self.driver.current_window_handle

            # Step 3: Check if you're not in the first tab
            if current_tab != first_tab:
                # Close the current tab
                self.driver.close()

                # Switch back to the first tab
                self.driver.switch_to.window(first_tab)
            else:
                print("🟡 Already in the first tab. No action taken.")

        except Exception as e:
            print(f"❌ Error while moving to first tab ' {str(e)}")
            traceback.print_exc()

    def move_to_grid_old(self, grid_name, more=None):
        """Navigates to a specified grid in the UI."""
        try:
            wait = WebDriverWait(self.driver, 60)
            self.wait_for_page_load()
            if more :
                more_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='More']"))
                )
                self.driver.execute_script("arguments[0].click();", more_button)

            assessments_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//a[normalize-space()='{grid_name}']"))
            )
            self.driver.execute_script("arguments[0].click();", assessments_button)

        except Exception as e:
            print(f"❌ Error while navigating to grid '{grid_name}': {str(e)}")
            traceback.print_exc()

    def move_to_grid(self, grid_name):
        """Navigate to grid. If visible directly, click it.
           Otherwise click 'More' and then click the grid."""
        try:
            wait = WebDriverWait(self.driver, 30)
            self.wait_for_page_load()
            time.sleep(2)

            grid_locator = (By.XPATH, f"//a[normalize-space()='{grid_name}']")
            grid_elements = self.driver.find_elements(*grid_locator)

            if grid_elements:
                print(f"🔹 Grid '{grid_name}' found directly on page.")
                grid_button = wait.until(EC.element_to_be_clickable(grid_locator))
            else:
                print(f"🔹 Grid '{grid_name}' not visible. Clicking 'More'.")

                # Click More
                more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='More']")))
                self.driver.execute_script("arguments[0].click();", more_button)
                time.sleep(1)
                grid_button = wait.until(EC.element_to_be_clickable(grid_locator))

            # Scroll and click grid
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", grid_button)
            self.driver.execute_script("arguments[0].click();", grid_button)

            print(f"✅ Successfully moved to grid '{grid_name}'")
            self.wait_for_page_load()

        except TimeoutException:
            print(f"❌ Timeout while navigating to grid '{grid_name}'")
        except Exception as e:
            print(f"❌ Error while navigating to grid '{grid_name}': {e}")
            traceback.print_exc()

    def move_inside_authoring_grid(self, grid_name):
        """Navigates to a specified grid in the UI."""
        try:
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[@title='{grid_name}']")))
            self.driver.execute_script("arguments[0].click();", element)
            print(f"✅ Successfully moved to grid '{grid_name}'")


        except Exception as e:
            print(f"❌ Error while navigating to '{grid_name}' grid inside authoring : {str(e)}")
            traceback.print_exc()

    def get_assessment_grid_actions(self, test_user_ids, grid_name, test_id=None):
        try:
            wait = WebDriverWait(self.driver, 10)
            results = []
            grid_actions_list = []
            self.move_to_grid(grid_name)

            if test_id:
                self.click_on_filter_button()
                self.filter_search_by_id(test_id)
                self.click_on_more_option()
                grid_actions_list = self.fetch_grid_actions()
                view_candidates_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'View Candidates')]"))
                )
                self.driver.execute_script("arguments[0].click();", view_candidates_button)

            self.click_on_filter_button()
            self.filter_search_by_test_user_id(test_user_ids)
            self.wait_for_page_load()

            more_options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='pointer fa fa-lg fa-ellipsis-v']"))
            )

            if more_options:  # Ensure the list is not empty
                for element in more_options:
                    try:
                        wait.until(EC.element_to_be_clickable(element)).click()
                        results.append(self.fetch_grid_actions())
                    except Exception as e:
                        print(f"⚠️ Warning: Skipping element due to error: {e}")

            # Return results with a consistent format
            return [grid_actions_list] + results if grid_actions_list else results

        except TimeoutException as te:
            print(f"❌ Timeout Error: {grid_name} grid actions took too long to load: {te}")
        except Exception as e:
            print(f"❌ Error while processing {grid_name} grid actions: {str(e)}")
            traceback.print_exc()
        return []

    def get_event_grid_actions(self, event_test_user_ids, grid_name, event_id):
        """Retrieve available grid actions for an event and its test users."""
        try:
            wait = WebDriverWait(self.driver, 30)
            results = []

            # Move to the required grid and apply event filter
            self.move_to_grid(grid_name)
            self.click_on_filter_button()
            self.filter_search_by_id(event_id)
            self.wait_for_page_load()

            # Navigate to 'View Event Assessments'
            wait.until(
                EC.element_to_be_clickable((By.XPATH, "//i[@class='glyphicon glyphicon-option-horizontal']"))
            ).click()
            wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'View Event Assessments')]"))
            ).click()

            # Fetch actions from the event grid
            self.click_on_more_option()
            event_grid_actions = self.fetch_grid_actions() if self.fetch_grid_actions() else []

            # Navigate to 'View Candidates' and apply filters
            wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'View Candidates')]"))
            ).click()
            self.click_on_filter_button()
            self.filter_search_by_id(event_test_user_ids)  # Batch filtering
            self.wait_for_page_load()

            # Fetch grid actions for each test user ID
            more_options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='pointer fa fa-lg fa-ellipsis-v']"))
            )

            for idx, element in enumerate(more_options):
                try:
                    wait.until(EC.element_to_be_clickable(element)).click()
                    actions = self.fetch_grid_actions()
                    results.append(actions)
                except Exception as e:
                    print(
                        f"⚠️ Warning: Failed to click 'More Options' for test user {event_test_user_ids[idx]}. Error: {e}")

            return [event_grid_actions] + results if event_grid_actions else results

        except TimeoutException as te:
            print(f"❌ Timeout Error: {grid_name} grid actions took too long to load: {te}")
        except Exception as e:
            print(f"❌ Error while processing {grid_name} grid actions: {str(e)}")
            traceback.print_exc()

        return []  # Ensures function always returns a list, even in case of failure

    def get_authoring_grid_actions(self, qp_ids, grid_name, sub_grid):
        try:
            wait = WebDriverWait(self.driver, 20)  # Reduced wait time for efficiency
            results = []

            # Ensure UI object is called correctly
            self.move_to_grid(grid_name)
            self.move_inside_authoring_grid(sub_grid)
            # Apply filters
            self.click_on_filter_button()
            self.filter_search_by_id_authoring(qp_ids)
            self.wait_for_page_load()

            # Wait for all "more options" elements
            more_options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='pointer fa fa-lg fa-ellipsis-v']"))
            )

            # Click each 'More Options' and fetch actions
            for element in more_options:
                wait.until(EC.element_to_be_clickable(element))  # Ensure each element is clickable
                element.click()
                results.append(self.fetch_grid_actions())

            return results

        except TimeoutException as te:
            print(f"❌ Timeout Error: '{grid_name}' grid actions took too long to load:\n{te}")
        except Exception as e:
            print(f"❌ Error while processing '{grid_name}' grid actions:\n{e}")
            traceback.print_exc()

        return []  # Ensure function always returns a list

    def get_blueprint_grid_actions(self, bp_ids, grid_name,sub_grid):
        try:
            results = []
            self.move_to_grid(grid_name)
            self.move_inside_authoring_grid(sub_grid)
            self.click_on_filter_button()
            for bp_id in bp_ids:
                self.filter_search_by_single_id_authoring(bp_id)
                results.append(self.fetch_bp_grid_actions())

            return results

        except TimeoutException as te:
            print(f"❌ Timeout Error: {grid_name} grid actions took too long to load: {te}")
        except Exception as e:
            print(f"❌ Error while processing {grid_name} grid actions: {str(e)}")
            traceback.print_exc()

        return []  # Ensures function always returns a list, even in case of failure

    def get_interview_bot_grid_actions(self, test_user_ids, grid_name, test_id=None):
        try:
            wait = WebDriverWait(self.driver, 10)
            results = []
            grid_actions_list = []
            self.move_to_grid(grid_name)

            if test_id:
                self.click_on_filter_button()
                self.filter_search_by_interview_bot_id(test_id)
                self.click_on_more_option()
                grid_actions_list = self.fetch_grid_actions()
                view_candidates_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'View Candidates')]"))
                )
                self.driver.execute_script("arguments[0].click();", view_candidates_button)

            self.click_on_filter_button()
            self.filter_search_by_candidate_id(test_user_ids)
            self.wait_for_page_load()

            more_options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='pointer fa fa-lg fa-ellipsis-v']"))
            )

            if more_options:  # Ensure the list is not empty
                for element in more_options:
                    try:
                        wait.until(EC.element_to_be_clickable(element)).click()
                        results.append(self.fetch_grid_actions())
                    except Exception as e:
                        print(f"⚠️ Warning: Skipping element due to error: {e}")

            # Return results with a consistent format
            return [grid_actions_list] + results if grid_actions_list else results

        except TimeoutException as te:
            print(f"❌ Timeout Error: {grid_name} grid actions took too long to load: {te}")
        except Exception as e:
            print(f"❌ Error while processing {grid_name} grid actions: {str(e)}")
            traceback.print_exc()
        return []

    def get_interview_bot_authoring_grid_actions(self, ids, grid_name, sub_grid = None):
        try:
            wait = WebDriverWait(self.driver, 10)
            results = []
            grid_actions_list = []
            self.move_to_grid(grid_name)

            self.move_inside_authoring_grid(sub_grid)
            self.move_to_next_tab()
            self.click_on_filter_button()
            self.filter_search_by_id_authoring_bot(ids)
            self.wait_for_page_load()

            more_options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='pointer fa fa-lg fa-ellipsis-v']"))
            )

            if more_options:  # Ensure the list is not empty
                for element in more_options:
                    try:
                        wait.until(EC.element_to_be_clickable(element)).click()
                        results.append(self.fetch_grid_actions())
                    except Exception as e:
                        print(f"⚠️ Warning: Skipping element due to error: {e}")


            self.move_to_previous_tab()

            # Return results with a consistent format
            return [grid_actions_list] + results if grid_actions_list else results

        except TimeoutException as te:
            print(f"❌ Timeout Error: {grid_name} grid actions took too long to load: {te}")
        except Exception as e:
            print(f"❌ Error while processing {grid_name} grid actions: {str(e)}")
            traceback.print_exc()
        return []

    def crpo_more_functionality(self):
        self.driver.find_element(By.LINK_TEXT, 'More').click()

    def crpo_assessment_candidates(self):
        self.driver.find_element_by_xpath('//*[@class="ng-binding ng-scope"]').click()
        #self.driver.find_element(By.LINK_TEXT, 'Assessment Candidates').click()
        # time.sleep(5)

    def crpo_assessment_candidates_filter(self):
        time.sleep(30)
        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.ID, 'cardlist-view-filter'))).click()

    def crpo_assessment_candidates_filter_by_id(self, value):
        self.driver.find_element(By.NAME, 'Ids').send_keys(value)

    def crpo_assessment_candidates_filter_search(self):
        time.sleep(2)
        self.driver.find_element(By.XPATH, '//button[text()="Search"]').click()

    def crpo_assessment_candidates_view_video_review(self):
        self.driver.find_element(By.XPATH, '//*[@class="img_margin_1 pointer ng-binding ng-scope"]').click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(5)

    def review_page_is_suspicious(self):
        value = "//*[@class='btn btn-default dropdown-toggle pull-right']"
        self.driver.find_element_by_xpath(value).click()
        time.sleep(2)

    def review_page_is_suspicious_comments(self, comments):
        time.sleep(2)
        self.driver.find_element_by_xpath(
            '//*[@class = "form-control ng-pristine ng-untouched ng-valid ng-empty"]').send_keys(comments)
        # self.driver.find_element_by_xpath(
        #     '//*[@class = "form-control ng-pristine ng-valid ng-not-empty ng-touched"]').send_keys(comments)

    def review_page_is_suspicious_submit(self):
        self.driver.find_element(By.XPATH, '//button[text()="Submit"]').click()
        # self.driver.find_element(By.LINK_TEXT('Submit')).click()

    def select_dropdown_yes(self):
        self.driver.find_element(By.LINK_TEXT, 'Yes').click()


crpo_ui_obj = CrpoCommon()
