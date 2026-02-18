import time
import urllib3
from SCRIPTS.COMMON.read_excel import excel_read_obj
from SCRIPTS.COMMON.write_excel_new import write_excel_object
from SCRIPTS.CRPO_COMMON.crpo_common import *
from SCRIPTS.ASSESSMENT_COMMON.assessment_common import *
from SCRIPTS.COMMON.io_path import *
from SCRIPTS.DB_DELETE.sanitizeapi_resetuser import *

urllib3.disable_warnings()


class SanitizeAutomation:
    def __init__(self):
        reset_test_user_obj.reset_test_users()
        self.row_size = 2
        write_excel_object.save_result(output_path_sanitize_automation)
        header = ["Sanitize relogin automation"]
        write_excel_object.write_headers_for_scripts(0, 0, header,
                                                     write_excel_object.black_color_bold)
        header1 = ["Testcases", "Status", "Test ID", "Candidate ID", "Test User ID", "Case Number", "ExpectedUsecase",
                   "ActualUsecase", "ExpectedMessage", "ActualMessage", "ExpectedTestUserStatus",
                   "ActualTestUserStatus", "ExpectedApplicantStatus", "ActualApplicantStatus",
                   "ExpectedScoreStatus", "ActualScoreStatus", "IsCandidateTaggedToT2(Expected)",
                   "IsCandidateTaggedToT2(actual)", "isVendorTest", "IsSLCEnabled"]
        write_excel_object.write_headers_for_scripts(1, 0, header1,
                                                     write_excel_object.black_color_bold)

    def excel_write(self, data):
        write_excel_object.current_status_color = write_excel_object.green_color
        write_excel_object.current_status = "Pass"
        write_excel_object.compare_results_and_write_vertically(data.get('testCaseInfo'), None, self.row_size, 0)
        write_excel_object.compare_results_and_write_vertically(data.get('primaryTestId'), None, self.row_size, 2)
        write_excel_object.compare_results_and_write_vertically(data.get('candidateId'), None, self.row_size, 3)
        write_excel_object.compare_results_and_write_vertically(data.get('testUserID'), None, self.row_size, 4)
        write_excel_object.compare_results_and_write_vertically(data.get('caseNumber'), None, self.row_size, 5)
        write_excel_object.compare_results_and_write_vertically(data.get('useCase'), usecase, self.row_size, 6)
        write_excel_object.compare_results_and_write_vertically(data.get('message'), message, self.row_size, 8)
        write_excel_object.compare_results_and_write_vertically(data.get('testUserStatus'), test_user_status,
                                                                self.row_size, 10)
        write_excel_object.compare_results_and_write_vertically(data.get('ApplicantStatus'), applicant_status,
                                                                self.row_size, 12)
        write_excel_object.compare_results_and_write_vertically(data.get('scoreStatus'), score_status, self.row_size,
                                                                14)
        write_excel_object.compare_results_and_write_vertically(data.get('IsCandidateTaggedToT2'), test2_tuser_status,
                                                                self.row_size, 16)
        write_excel_object.compare_results_and_write_vertically(data.get('isVendorTest'), None, self.row_size, 18)
        write_excel_object.compare_results_and_write_vertically(data.get('IsSLCEnabled'), None, self.row_size, 19)
        write_excel_object.compare_results_and_write_vertically(write_excel_object.current_status, None, self.row_size,
                                                                1)
        self.row_size = self.row_size + 1

    @staticmethod
    def latest_applicant_status(login_token: str) -> str:
        get_applicant_status = crpo_common_obj.get_applicant_infos(login_token, candidate_id)
        for all_applicants_infos in get_applicant_status['data'][0]['ApplicantDetails']:
            if all_applicants_infos.get('Id') == applicant_id:
                applicant_history = all_applicants_infos.get('ApplicantHistory')
                latest_status = applicant_history[-1]['Status']
                return latest_status
        print("Applicant History Not Available in this object")
        return "Unknown"

    @staticmethod
    def check_task_status():
        job_status = CrpoCommon.job_status(crpo_headers, context_id)
        return job_status['data']['JobState']

    @staticmethod
    def untag_candidate(test_id2, candidate_id2):
        if test_id2 != 0:
            test_user_details = crpo_common_obj.search_test_user_by_cid_and_testid(crpo_headers, candidate_id2, test_id2)
            test2_test_user_id = test_user_details.get('testUserId')
            if test2_test_user_id != 'NotExist':
                print(f"Removing test user: {test2_test_user_id}")
                untag_candidates_details = [{"testUserIds": [test2_test_user_id]}]
                crpo_common_obj.untag_candidate(crpo_headers, untag_candidates_details)
                return 'Found'
        return 'NotExist'


re_initiate_obj = SanitizeAutomation()
excel_read_obj.excel_read(input_path_sanitize_automation, 1)
excel_data = excel_read_obj.details
crpo_headers = crpo_common_obj.login_to_crpo(cred_crpo_admin.get('user'), cred_crpo_admin.get('password'),
                                             cred_crpo_admin.get('tenant'))

for data in excel_data:
    test2_id = int(data.get('untagUserFromT2'))
    candidate_id = int(data.get('candidateId'))
    applicant_id = int(data.get('applicantId'))
    applicant_status = 'pending'
    case_no = int(data.get('caseNumber'))
    test_user_id = int(data.get('testUserID'))
    score_status = "Not Available"

    print("Case no : ", case_no)
    result = crpo_common_obj.sanitise_tu_automation(crpo_headers, test_user_id)
    if 'Message' in result['data']:
        message = result['data']['Message']
        response = crpo_common_obj.tests_against_candidate(crpo_headers, candidate_id)
        test_user_status = response['data']['TestsAgainstCandidate'][0]['StatusText']
    else:
        message = "NULL"
        context_id = result['data']['ContextId']
        time.sleep(10)
        current_job_status = 'PENDING'

        for _ in range(10):  # 10 iterations * 30 seconds each = 5 minutes (300 sec)
            current_status = re_initiate_obj.check_task_status()
            if current_status == "PENDING":
                print("Task status is pending. checking again in 30 sec")
                time.sleep(30)
            else:
                time.sleep(5)
                print(f"Task status: {current_status}")
                response = crpo_common_obj.tests_against_candidate(crpo_headers, candidate_id)
                score = response['data']['TestsAgainstCandidate'][0]['TotalScore']
                test_user_status = response['data']['TestsAgainstCandidate'][0]['StatusText']
                score_status = "Available" if score != "null" else "Not Available"
                break
        else:
            # This block executes if the loop completes without breaking
            print("Task is still pending after waiting for 5 minutes. Exiting loop.")

    time.sleep(20)
    applicant_status = re_initiate_obj.latest_applicant_status(crpo_headers)
    print("Latest Applicant Status :", applicant_status)
    usecase = result['data']['UseCasePassed']
    test2_tuser_status = re_initiate_obj.untag_candidate(test2_id, candidate_id)
    re_initiate_obj.excel_write(data)
write_excel_object.write_overall_status(testcases_count=7)
