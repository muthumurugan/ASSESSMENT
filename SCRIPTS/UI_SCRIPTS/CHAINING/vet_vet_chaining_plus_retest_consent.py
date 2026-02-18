from SCRIPTS.UI_COMMON.assessment_ui_common_v2 import *
from SCRIPTS.ASSESSMENT_COMMON.assessment_common import *
from SCRIPTS.COMMON.io_path import *
from SCRIPTS.UI_SCRIPTS.assessment_data_verification import *
from SCRIPTS.COMMON.read_excel import *
import xlsxwriter
from SCRIPTS.DB_DELETE.db_cleanup import *


class VetChaining:

    def __init__(self):
        # data clean up is important, b'coz we need to create a candidate everytime to check the create is working fine.
        data_clean_obj.vet_ui_chaining_delete()
        time = datetime.datetime.now()
        self.date = time.strftime('%y_%m_%d')
        self.started = time.strftime("%Y-%M-%d-%H-%M-%S")
        self.row_size = 2
        self.write_excel = xlsxwriter.Workbook(output_path_ui_vet_vet_chaining)
        self.final_status = ''
        self.ws = self.write_excel.add_worksheet()
        self.black_color = self.write_excel.add_format({'font_color': 'black', 'font_size': 9})
        self.red_color = self.write_excel.add_format({'font_color': 'red', 'font_size': 9})
        self.green_color = self.write_excel.add_format({'font_color': 'green', 'font_size': 9})
        self.orange_color = self.write_excel.add_format({'font_color': 'orange', 'font_size': 9})
        self.black_color_bold = self.write_excel.add_format({'font_color': 'black', 'bold': True, 'font_size': 9})
        self.over_all_status_pass = self.write_excel.add_format({'font_color': 'green', 'bold': True, 'font_size': 9})
        self.over_all_status_failed = self.write_excel.add_format({'font_color': 'red', 'bold': True, 'font_size': 9})
        self.over_all_status_color = self.over_all_status_pass
        self.over_all_status = 'Pass'
        self.ws.write(0, 0, "hirepro chaining", self.black_color_bold)
        self.ws.write(1, 0, "Testcases", self.black_color_bold)
        self.ws.write(1, 1, "Status", self.black_color_bold)
        self.ws.write(1, 2, "Test ID", self.black_color_bold)
        self.ws.write(1, 3, "Candidate ID", self.black_color_bold)
        self.ws.write(1, 4, "Login Name", self.black_color_bold)
        self.ws.write(1, 5, "Password", self.black_color_bold)
        self.ws.write(1, 6, "T1 Expected Status", self.black_color_bold)
        self.ws.write(1, 7, "T1 Actual Status", self.black_color_bold)
        self.ws.write(1, 8, "Expected SLC Page Message", self.black_color_bold)
        self.ws.write(1, 9, "Actual SLC Page Message", self.black_color_bold)
        self.ws.write(1, 10, "Expected consentYesButtonMessage", self.black_color_bold)
        self.ws.write(1, 11, "Actual consentYesButtonMessage", self.black_color_bold)
        self.ws.write(1, 12, "Expected consentNOButtonMessage", self.black_color_bold)
        self.ws.write(1, 13, "Actual consentNOButtonMessage", self.black_color_bold)
        self.ws.write(1, 14, "Expected consentMessage Paragraph", self.black_color_bold)
        self.ws.write(1, 15, "Actual consentMessage Paragraph", self.black_color_bold)
        self.ws.write(1, 16, "Expected overAllPageMessage", self.black_color_bold)
        self.ws.write(1, 17, "Actual overAllPageMessage", self.black_color_bold)

    def vet_vet_chaining_with_retest_consent(self, current_excel_data, row_value):
        # screenshot_directory = "F:\\screenshot\\" + current_excel_data.get('testCases')
        # path = os.path.join(screenshot_directory)
        # if not os.path.exists(path):
        #     os.mkdir(path)
        # screenshot_directory = path + '\\screen_shot_' + self.date
        # path = os.path.join(screenshot_directory)
        # if not os.path.exists(path):
        #     os.mkdir(path)
        #
        # self.common_path = path
        # print(self.common_path)

        self.browser = assess_ui_common_obj.initiate_browser(amsin_at_vet_url)
        login_details = assess_ui_common_obj.ui_login_to_test(current_excel_data.get('loginName'),
                                                              (current_excel_data.get('password')))
        # self.browser.get_screenshot_as_file(self.common_path + "\\1_t1_afterlogin.png")
        self.ws.write(row_value, 0, current_excel_data.get('testCases'), self.black_color)
        self.ws.write(row_value, 2, current_excel_data.get('testId'), self.black_color)
        self.ws.write(row_value, 3, current_excel_data.get('candidateId'), self.black_color)
        self.ws.write(row_value, 4, current_excel_data.get('loginName'), self.black_color)
        self.ws.write(row_value, 5, current_excel_data.get('password'), self.black_color)
        self.ws.write(row_value, 6, current_excel_data.get('t1ExpectedStatus'), self.black_color)
        self.ws.write(row_value, 8, current_excel_data.get('message'), self.black_color)
        self.ws.write(row_value, 10, current_excel_data.get('consentYesButtonMessage'), self.black_color)
        self.ws.write(row_value, 12, current_excel_data.get('consentNoButtonMessage'), self.black_color)
        self.ws.write(row_value, 14, current_excel_data.get('consentMessage'), self.black_color)
        self.ws.write(row_value, 16, current_excel_data.get('overAllPageMessage'), self.black_color)
        if login_details == 'SUCCESS':
            i_agreed = assess_ui_common_obj.select_i_agree()
            if i_agreed:
                start_test_status = assess_ui_common_obj.start_test_button_status()
                assess_ui_common_obj.start_test()
                # self.browser.get_screenshot_as_file(self.common_path + "\\2_t1_afterstarttest.png")
                time.sleep(5)
                # self.browser.get_screenshot_as_file(self.common_path + "\\3_t1_beforeendtest.png")
                assess_ui_common_obj.end_test()
                # self.browser.get_screenshot_as_file(self.common_path + "\\4_t1_beforeconfirm.png")
                assess_ui_common_obj.end_test_confirmation()
                # self.browser.get_screenshot_as_file(self.common_path + "\\5_t1_afterconfirm.png")
                assessment_common_obj.pearson_call_backs(int(current_excel_data.get('testUserId')),
                                                         current_excel_data.get('scoreCallBack'), 'AT')

                time.sleep(120)
                # self.browser.get_screenshot_as_file(self.common_path + "\\6_t1_slcpage.png")
                status = assess_ui_common_obj.shortlisting_page()
                print(status)
                # is_needed_to_call_next_method = True
                if status.get('is_next_test_available') == 'Available':
                    if current_excel_data.get('consent') == "No":
                        is_needed_to_call_next_method = False
                        assess_ui_common_obj.consent_no()
                        # self.browser.get_screenshot_as_file(self.common_path + "\\10_t1_consent_no.png")
                        # self.browser.quit()

                    else:
                        print("Candidate is shortlisted or Autotest")
                        is_needed_to_call_next_method = False
                        # assess_ui_common_obj.start_next_test()
                        # time.sleep(3)
                        # self.browser.get_screenshot_as_file(self.common_path + "\\7_t2_nexttestlogin.png")
                        # time.sleep(2)
                        # assess_ui_common_obj.select_i_agree()
                        # assess_ui_common_obj.start_test()
                        # time.sleep(3)
                        # self.browser.get_screenshot_as_file(self.common_path + "\\8_t2_afterstarttest.png")
                        # assess_ui_common_obj.end_test()
                        # assess_ui_common_obj.end_test_confirmation()
                        # time.sleep(3)
                        # self.browser.get_screenshot_as_file(self.common_path + "\\9_t2_aftersubmission.png")
                        # self.browser.quit()

                elif status.get('is_next_test_available') == 'Not Available':
                    assess_ui_common_obj.vet_retest(current_excel_data.get('retestConsent'))
                    is_needed_to_call_next_method = False

                else:
                    is_needed_to_call_next_method = True

                if is_needed_to_call_next_method is True:
                    status = assess_ui_common_obj.rejection_page()
                    if status.get('is_next_test_available') == 'Not Available' and status.get(
                            'is_shortlisted') == 'Rejected':
                        print("Candidate is Rejected")
                        is_needed_to_call_next_method = False
                    else:
                        is_needed_to_call_next_method = True

                if is_needed_to_call_next_method is True:
                    print("Write SLC Code here")
                    print("Need to Debug Hirepro chaining")
            color = self.green_color
            tc_status = 'pass'
            if status.get('is_shortlisted') == current_excel_data.get('t1ExpectedStatus'):
                self.browser.quit()
                self.ws.write(row_value, 7, status.get('is_shortlisted'), self.green_color)
            else:
                self.ws.write(row_value, 7, status.get('is_shortlisted'), self.red_color)
                self.over_all_status = 'Fail'
                self.over_all_status_color = self.red_color
                color = self.red_color
                tc_status = 'Fail'

            if status.get('message') == current_excel_data.get('message'):
                self.ws.write(row_value, 9, status.get('message'), self.green_color)
            else:
                self.ws.write(row_value, 9, status.get('message'), self.red_color)
                self.over_all_status_color = self.red_color
                self.over_all_status = 'Fail'
                color = self.red_color
                tc_status = 'Fail'

            if status.get('consent_yes') == current_excel_data.get('consentYesButtonMessage'):
                self.ws.write(row_value, 11, status.get('consent_yes'), self.green_color)
            else:
                self.ws.write(row_value, 11, status.get('consent_yes'), self.red_color)
                self.over_all_status_color = self.red_color
                self.over_all_status = 'Fail'
                color = self.red_color
                tc_status = 'Fail'

            if status.get('consent_no') == current_excel_data.get('consentNoButtonMessage'):
                self.ws.write(row_value, 13, status.get('consent_no'), self.green_color)
            else:
                self.ws.write(row_value, 13, status.get('consent_no'), self.red_color)
                self.over_all_status_color = self.red_color
                self.over_all_status = 'Fail'
                color = self.red_color
                tc_status = 'Fail'

            if status.get('consent_paragraph') == current_excel_data.get('consentMessage'):
                self.ws.write(row_value, 15, status.get('consent_paragraph'), self.green_color)
            else:
                self.ws.write(row_value, 15, status.get('consent_paragraph'), self.red_color)
                self.over_all_status_color = self.red_color
                self.over_all_status = 'Fail'
                color = self.red_color
                tc_status = 'Fail'

            if status.get('next_test_page_message') == current_excel_data.get('overAllPageMessage'):
                self.ws.write(row_value, 17, status.get('next_test_page_message'), self.green_color)
            else:
                self.ws.write(row_value, 17, status.get('next_test_page_message'), self.red_color)
                self.over_all_status_color = self.red_color
                self.over_all_status = 'Fail'
                color = self.red_color
                tc_status = 'Fail'

            self.ws.write(row_value, 1, tc_status, color)

        else:
            print("login failed due to below reason")
        print(login_details)


chaining_obj = VetChaining()
# input_file_path = r"F:\automation\PythonWorkingScripts_InputData\UI\Assessment\hirepro_chaining_at.xls"
# input_file_path = r"F:\qa_automation\PythonWorkingScripts_InputData\UI\Assessment\hirepro_chaining_at.xls"
crpo_headers = crpo_common_obj.login_to_crpo(cred_crpo_admin.get('user'), cred_crpo_admin.get('password'),
                                             cred_crpo_admin.get('tenant'))
test_id = 10037
candidate_ids = [1296720, 1299174]
crpo_common_obj.untag_candidate_by_cid(crpo_headers, test_id, candidate_ids)
excel_read_obj.excel_read(input_path_ui_vet_vet_chaining, 0)
excel_data = excel_read_obj.details
row_value = 1
for current_excel_row in excel_data:
    row_value += 2
    chaining_obj.vet_vet_chaining_with_retest_consent(current_excel_row, row_value)
chaining_obj.ws.write(0, 1, chaining_obj.over_all_status, chaining_obj.over_all_status_color)
time.sleep(10)
chaining_obj.write_excel.close()
print(datetime.datetime.now())
