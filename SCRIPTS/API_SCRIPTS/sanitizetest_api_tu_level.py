import time
import json
import logging
import urllib3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from SCRIPTS.COMMON.read_excel import excel_read_obj
from SCRIPTS.COMMON.write_excel_new import write_excel_object
from SCRIPTS.CRPO_COMMON.credentials import cred_crpo_admin
from SCRIPTS.CRPO_COMMON.crpo_common import crpo_common_obj, CrpoCommon
from SCRIPTS.COMMON.io_path import *
from SCRIPTS.DB_DELETE.sanitizeapi_resetuser import reset_test_user_obj

urllib3.disable_warnings()

# ---------------------------------------------------
# GLOBAL HTTP SESSION (30% faster API calls)
# ---------------------------------------------------

session = requests.Session()


# ---------------------------------------------------
# GENERIC RETRY WRAPPER
# ---------------------------------------------------

def safe_post(url, headers=None, json_data=None, retries=3):

    for attempt in range(retries):

        try:
            resp = session.post(
                url,
                headers=headers,
                json=json_data,
                verify=False,
                timeout=30
            )

            if resp.status_code == 200:
                return resp.json()

        except requests.exceptions.RequestException as e:

            print(f"API retry {attempt+1}/{retries}: {e}")
            time.sleep(5)

    return {}


# ---------------------------------------------------
# MAIN AUTOMATION CLASS
# ---------------------------------------------------

class SanitizeAutomation:

    def __init__(self):

        reset_test_user_obj.reset_test_users()

        self.row_size = 2

        write_excel_object.save_result(output_path_sanitize_testuser_automation)

        write_excel_object.write_headers_for_scripts(
            0, 0, ["Sanitize relogin automation"],
            write_excel_object.black_color_bold
        )

        headers = [
            "Testcases","Status","Test ID","Candidate ID","Test User ID",
            "Case Number","ExpectedUsecase","ActualUsecase",
            "ExpectedMessage","ActualMessage",
            "ExpectedTestUserStatus","ActualTestUserStatus",
            "ExpectedApplicantStatus","ActualApplicantStatus",
            "ExpectedScoreStatus","ActualScoreStatus",
            "IsCandidateTaggedToT2(Expected)","IsCandidateTaggedToT2(actual)",
            "isVendorTest","IsSLCEnabled",
            "ExpectedDryRun","ActualDryRun"
        ]

        write_excel_object.write_headers_for_scripts(
            1,0,headers,
            write_excel_object.black_color_bold
        )

    # ---------------------------------------------------
    # JOB POLLING
    # ---------------------------------------------------

    def wait_for_job(self, token, context_id):

        for i in range(25):

            job = CrpoCommon.job_status_v2(token, context_id)
            status = job.get("data", {}).get("JobState")

            print(f"Job status: {status}")

            if status != "PENDING":
                return status

            time.sleep(20)

        return "TIMEOUT"


    # ---------------------------------------------------
    # GET APPLICANT STATUS
    # ---------------------------------------------------

    @staticmethod
    def latest_applicant_status(token, candidate_id, applicant_id):

        resp = crpo_common_obj.get_applicant_infos(token, candidate_id)

        for info in resp.get('data', [{}])[0].get('ApplicantDetails', []):

            if info.get('Id') == applicant_id:

                history = info.get('ApplicantHistory', [])

                if history:
                    return history[-1].get('Status')

        return "Unknown"


    # ---------------------------------------------------
    # T2 UNTAG
    # ---------------------------------------------------

    @staticmethod
    def untag_candidate(token, test_id, candidate_id):

        if not test_id:
            return "NotExist"

        tu = crpo_common_obj.search_test_user_by_cid_and_testid(
            token, candidate_id, test_id
        )

        tu_id = tu.get('testUserId')

        if tu_id and tu_id != 'NotExist':

            crpo_common_obj.untag_candidate(
                token, [{"testUserIds":[tu_id]}]
            )

            return "Found"

        return "NotExist"


    # ---------------------------------------------------
    # EXCEL WRITE
    # ---------------------------------------------------

    def excel_write(self, data):

        write_excel_object.current_status = "Pass"
        write_excel_object.current_status_color = write_excel_object.green_color

        write_excel_object.compare_results_and_write_vertically(
            data.get('testCaseInfo'), None, self.row_size, 0)

        write_excel_object.compare_results_and_write_vertically(
            data.get('primaryTestId'), None, self.row_size, 2)

        write_excel_object.compare_results_and_write_vertically(
            data.get('candidateId'), None, self.row_size, 3)

        write_excel_object.compare_results_and_write_vertically(
            data.get('testUserID'), None, self.row_size, 4)

        write_excel_object.compare_results_and_write_vertically(
            data.get('caseNumber'), None, self.row_size, 5)

        write_excel_object.compare_results_and_write_vertically(
            data.get('useCase'), data.get('ActualUsecase'), self.row_size, 6)

        write_excel_object.compare_results_and_write_vertically(
            data.get('message'), data.get('ActualMessage'), self.row_size, 8)

        write_excel_object.compare_results_and_write_vertically(
            data.get('testUserStatus'),
            data.get('ActualTestUserStatus'), self.row_size, 10)

        write_excel_object.compare_results_and_write_vertically(
            data.get('ApplicantStatus'),
            data.get('ActualApplicantStatus'), self.row_size, 12)

        write_excel_object.compare_results_and_write_vertically(
            data.get('scoreStatus'),
            data.get('ActualScoreStatus'), self.row_size, 14)

        write_excel_object.compare_results_and_write_vertically(
            data.get('IsCandidateTaggedToT2'),
            data.get('ActualT2Status'), self.row_size, 16)

        write_excel_object.compare_results_and_write_vertically(
            data.get('isVendorTest'), None, self.row_size, 18)

        write_excel_object.compare_results_and_write_vertically(
            data.get('IsSLCEnabled'), None, self.row_size, 19)

        write_excel_object.compare_results_and_write_vertically(
            data.get('dryRun'), data.get('ActualDryRun'), self.row_size, 20)

        write_excel_object.compare_results_and_write_vertically(
            write_excel_object.current_status, None, self.row_size, 1)

        self.row_size += 1


# ---------------------------------------------------
# PROCESS ONE TEST USER
# ---------------------------------------------------

def process_user(data):

    test_id = int(data['primaryTestId'])
    test_user_id = int(data['testUserID'])
    candidate_id = int(data['candidateId'])
    applicant_id = int(data['applicantId'])
    test2_id = int(data.get('untagUserFromT2',0))

    try:

        # ---------------- DRY RUN ----------------
        dryrun_resp = crpo_common_obj.sanitise_test_automation_testuser_dryrun(crpo_headers, test_user_id, test_id)

        if isinstance(dryrun_resp, dict):
            dryrun_items = dryrun_resp.get('data', [ ])
        elif isinstance(dryrun_resp, list):
            dryrun_items = dryrun_resp
        else:
            dryrun_items = [ ]

        data[ 'ActualDryRun' ] = json.dumps(dryrun_items, indent=2)
        print(data[ 'ActualDryRun' ])

        # -------- EXECUTE --------

        result = crpo_common_obj.sanitise_test_automation_testuser_execute(
            crpo_headers, test_user_id, test_id)

        data['ActualMessage'] = (
            result.get('message')
            or result.get('data', {}).get('Message')
        )

        data['ActualUsecase'] = result.get('data', {}).get('UseCasePassed')

        context_id = result.get('data', {}).get('ContextId')

        if context_id:
            automation.wait_for_job(crpo_headers, context_id)

        # -------- TEST INFO --------

        tc = crpo_common_obj.tests_against_candidate(
            crpo_headers, candidate_id)

        info = tc.get('data', {}).get('TestsAgainstCandidate',[{}])[0]

        data['ActualTestUserStatus'] = info.get('StatusText')

        data['ActualScoreStatus'] = (
            "Available"
            if info.get('TotalScore') not in (None,"null")
            else "Not Available"
        )

        data['ActualApplicantStatus'] = automation.latest_applicant_status(
            crpo_headers, candidate_id, applicant_id)

        data['ActualT2Status'] = automation.untag_candidate(
            crpo_headers, test2_id, candidate_id)

    except Exception as e:

        print(f"Error processing user {test_user_id}: {e}")
        data['ActualMessage'] = str(e)

    return data


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

automation = SanitizeAutomation()

excel_read_obj.excel_read(input_path_sanitize_automation,0)
excel_data = excel_read_obj.details

crpo_headers = crpo_common_obj.login_to_crpo(
    cred_crpo_admin['user'],
    cred_crpo_admin['password'],
    cred_crpo_admin['tenant']
)

# -------- PARALLEL EXECUTION --------

MAX_WORKERS = 5

with ThreadPoolExecutor(MAX_WORKERS) as executor:

    futures = [executor.submit(process_user, d) for d in excel_data]

    for future in as_completed(futures):

        result = future.result()
        automation.excel_write(result)

write_excel_object.write_overall_status(
    testcases_count=len(excel_data)
)