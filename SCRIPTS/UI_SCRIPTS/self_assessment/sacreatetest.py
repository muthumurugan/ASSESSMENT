from SCRIPTS.UI_COMMON.self_assessment_common import *
from SCRIPTS.COMMON.io_path import *
from SCRIPTS.CRPO_COMMON.credentials import cred_crpo_suparya_crpodemo
from SCRIPTS.COMMON.write_excel_new import *
from SCRIPTS.COMMON.read_excel import *
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("sa_test.log", mode='w')])


class SaTest:
    def __init__(self):
        self.browser = None
        self.row_size = 2
        write_excel_object.save_result(output_path_ui_self_assessment)
        self._initialize_excel_headers()

    @staticmethod
    def _initialize_excel_headers():
        """Initialize headers in the Excel file."""
        headers = ["Self Assessment test creation"]
        headers_sub = ["Test cases", "Status", "Expected status", "Actual status"]
        write_excel_object.write_headers_for_scripts(0, 0, headers, write_excel_object.black_color_bold)
        write_excel_object.write_headers_for_scripts(1, 0, headers_sub, write_excel_object.black_color_bold)

    def write_to_excel(self, test_case, expected_status, actual_status, start_test_status=None, end_test_status=None):
        """Write test case results to the Excel file."""
        try:
            current_status = "Pass" if expected_status == actual_status else "Fail"
            write_excel_object.compare_results_and_write_vertically(test_case, None, self.row_size, 0)
            write_excel_object.compare_results_and_write_vertically(expected_status, actual_status, self.row_size, 2)
            write_excel_object.compare_results_and_write_vertically(current_status, None, self.row_size, 1)

            if start_test_status:
                write_excel_object.compare_results_and_write_vertically(start_test_status, None, self.row_size, 3)
                write_excel_object.compare_results_and_write_vertically(current_status, None, self.row_size, 1)
            if end_test_status:
                write_excel_object.compare_results_and_write_vertically(end_test_status, None, self.row_size, 4)
                write_excel_object.compare_results_and_write_vertically(current_status, None, self.row_size, 1)

            self.row_size += 1
        except Exception as e:
            logging.error(f"Error writing to Excel: {e}")

    def execute_test_case(self, test_case):
        """Execute individual test case based on its type."""
        try:
            # Mapping test case types to corresponding actions
            test_mapping = {
                # 'Test Creation': lambda: 'Test created successfully',
                'RTC Question Creation': lambda: self_assessment_obj.create_rtc_q(),
                'RTC Addition (Local)': lambda: self_assessment_obj.add_rtc_local('ReferenceToContext'),
                'RTC Addition (HirePro)': lambda: self_assessment_obj.add_rtc_hirepro('ReferenceToContext'),
                'MCQ Question Creation': lambda: self_assessment_obj.create_mcq_q(),
                'MCQ Addition (Local)': lambda: self_assessment_obj.add_q_local("136095",'MCQ'),
                'MCQ Addition (HirePro)': lambda: self_assessment_obj.add_q_hirepro("136097",'MCQ'),
                'FIB Question Creation': lambda: self_assessment_obj.create_fib_q(),
                'FIB Addition (Local)': lambda: self_assessment_obj.add_q_local("141667",'FillInTheBlank'),
                'FIB Addition (HirePro)': lambda: self_assessment_obj.add_q_hirepro("141693",'FillInTheBlank'),
                'MCA Question Creation': lambda: self_assessment_obj.create_mca_q(),
                'MCA Addition (Local)': lambda: self_assessment_obj.add_q_local("142459",'MultipleCorrectAnswer'),
                'MCA Addition (HirePro)': lambda: self_assessment_obj.add_q_hirepro("142463",'MultipleCorrectAnswer'),
                'MCQWW Question Creation': lambda: self_assessment_obj.create_mcqww_q(),
                'MCQWW Addition (Local)': lambda: self_assessment_obj.add_q_local("142461",'MCQWithWeightage'),
                'MCQWW Addition (HirePro)': lambda: self_assessment_obj.add_q_hirepro("142465",'MCQWithWeightage'),
                'Coding Question Creation': lambda: self_assessment_obj.create_coding_q(),
                'Coding Addition (Local)': lambda: self_assessment_obj.add_q_local("142593",'Coding'),
                'Coding Addition (HirePro)': lambda: self_assessment_obj.add_q_hirepro("142591",'Coding'),
                'Subjective Question Creation': lambda: self_assessment_obj.create_subjective_q(),
                'Subjective Addition (Local)': lambda: self_assessment_obj.add_q_local("141573",'QA'),
                'Subjective Addition (HirePro)': lambda: self_assessment_obj.add_q_hirepro("141575",'QA'),
            }

            # Retrieve action for the given test case
            action = test_mapping.get(test_case['testCases'])

            if action:
                # Execute the action and check its result
                status = action()  # This line will invoke the lambda and execute the function
                actual_status = "SUCCESS" if status == "SUCCESS" else status
            else:
                logging.warning(f"Test case type '{test_case['testCases']}' is not recognized.")
                actual_status = "UNKNOWN"

            # Write the result to the Excel
            self.write_to_excel(test_case['testCases'], test_case['expectedStatus'], actual_status)

            if actual_status != "SUCCESS":
                logging.error(f"Test case '{test_case['testCases']}' failed.")
                return False
            return True

        except Exception as e:
            logging.error(f"Error executing test case '{test_case['testCases']}': {e}")
            return False

    def self_assessment(self, username, password, q_test_cases):
        """Main self-assessment workflow."""
        try:
            self.browser = self_assessment_obj.initiate_browser(amsin_crpodemo_crpo_login, chrome_driver_path)
            logging.info("Browser initiated successfully.")

            login_status = self_assessment_obj.ui_login_to_tenant(username, password)
            if login_status != 'SUCCESS':
                logging.error(f"Login failed: {login_status}")
                return
            logging.info("Login successful.")
            test_creation_status, test_name = self_assessment_obj.create_test_sa()
            # test_creation_status, test_name = 'SUCCESS', 'Automation_sa_03-12-2024_19:11:14'

            if test_creation_status != 'SUCCESS':
                logging.error("Test creation failed.")
                for test_case in q_test_cases:
                    self.write_to_excel(test_case['testCases'], test_case['expectedStatus'], test_creation_status)
                return
            else :
                self.write_to_excel("Test Creation", "SUCCESS", test_creation_status)
                for test_case in q_test_cases:
                    if not self.execute_test_case(test_case):
                        break

                # Test activation
                activation_status = self_assessment_obj.activate_test()
                self.write_to_excel("Test Activation", "SUCCESS", activation_status)
                if activation_status != 'SUCCESS':
                    return

                # Candidate invitation
                invite_status = self_assessment_obj.invite_candidate()
                self.write_to_excel("Invite Candidate", "SUCCESS", invite_status)
                if invite_status != 'SUCCESS':
                    return

                # Test Updation
                update_test = self_assessment_obj.update_test()
                self.write_to_excel("Update Candidate", "SUCCESS", update_test)
                if update_test != 'SUCCESS':
                    return

                # Test participation
                start_status, end_status = self_assessment_obj.attend_test(test_name)
                self.write_to_excel("Start Test", "Test Started", start_status)
                self.write_to_excel("End Test", "Test Ended Successfully", end_status)

                manual_eval_status = self_assessment_obj.manual_evaluation(test_name)
                print(manual_eval_status)
                self.write_to_excel("Manual Evaluation", "SUCCESS", manual_eval_status)

                score, percentage = self_assessment_obj.get_score_percentage(test_name)
                self.write_to_excel("Score", "10", score)
                self.write_to_excel("Percentage", "41.67", percentage)

            logging.info("Self-assessment workflow completed successfully.")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

        finally:
            if self.browser:
                self.browser.quit()


if __name__ == "__main__":
    try:
        logging.info("Script started.")
        print(datetime.datetime.now())

        assessment_obj = SaTest()
        excel_read_obj.excel_read(input_path_ui_self_assessment, 0)
        test_cases = excel_read_obj.details

        assessment_obj.self_assessment(cred_crpo_suparya_crpodemo.get('user'),
                                       cred_crpo_suparya_crpodemo.get('password'),
                                       test_cases)

        write_excel_object.write_overall_status(testcases_count=len(test_cases)+9)
        print(datetime.datetime.now())
        logging.info("Script completed successfully.")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
