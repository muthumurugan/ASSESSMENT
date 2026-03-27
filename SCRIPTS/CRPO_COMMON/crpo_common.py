import requests
import json
import time
from SCRIPTS.COMMON.environment import *
import logging

class CrpoCommon:
    domain = env_obj.domain
    pearson_domain = env_obj.pearson_domain
    eu_domain = env_obj.eu_domain

    @staticmethod
    def login_to_crpo(login_name, password, tenant):
        print("Entered")
        logging.info('Entered in to  login to CRPO ')
        print(crpo_common_obj.domain)
        header = {"content-type": "application/json"}
        data = {"LoginName": login_name, "Password": password, "TenantAlias": tenant, "UserName": login_name}
        print(data)
        response = requests.post(crpo_common_obj.domain + "/py/common/user/login_user/", headers=header,
                                 data=json.dumps(data), verify=False)
        login_response = response.json()
        headers = {"content-type": "application/json", "APP-NAME": "CRPO", "X-APPLMA": "true",
                   "X-AUTH-TOKEN": login_response.get("Token")}
        print(headers)
        logging.info('Successfully Exited From login to CRPO ')
        return headers

    @staticmethod
    def eu_login_to_crpo(login_name, password, tenant):
        logging.info('Entered in to  login to EU CRPO ')
        header = {"content-type": "application/json"}
        data = {"LoginName": login_name, "Password": password, "TenantAlias": tenant, "UserName": login_name}
        response = requests.post(crpo_common_obj.eu_domain + "/py/common/user/login_user/", headers=header,
                                 data=json.dumps(data), verify=False)
        login_response = response.json()

        headers = {"content-type": "application/json", "APP-NAME": "CRPO", "X-APPLMA": "true",
                   "X-AUTH-TOKEN": login_response.get("Token")}
        print(headers)
        logging.info('Successfully exited from eu CRPO ')
        return headers

    @staticmethod
    def candidate_web_transcript(token, test_id, test_user_id):
        logging.info('Entered Candidate web Transcript')
        request = {"testId": int(test_id), "testUserId": int(test_user_id),
                   "reportFlags": {"eduWorkProfilesRequired": True, "testUsersScoreRequired": True,
                                   "fileContentRequired": False, "isProctroingDetailsRequired": True,
                                   "testUserItemRequired": True}, "print": False}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/report/api/v1/candidatetranscript/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info(response.json())
        return response.json()

    @staticmethod
    def force_evaluate_proctoring_old(token, tu_ids):
        logging.info('Entered to force evaluate proctoring')
        request = {
            "testUserIds": tu_ids, "isForce": True}
        response = requests.post(crpo_common_obj.domain +
                                 "/py/assessment/htmltest/api/v1/initiate-test-proc/?isSync=false",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info(response.json())
        return response.json()

    @staticmethod
    def force_evaluate_proctoring(token, tu_ids):
        logging.info('Entered to force evaluate proctoring')
        headers = token.copy()
        request_payload = {"testUserIds":tu_ids, "isForce":True}
        response = requests.post(
            crpo_common_obj.domain + "/py/assessment/htmltest/api/v1/initiate-test-proc/?isSync=false", headers=headers,
            json=request_payload,  # better than data=json.dumps
            verify=False)

        # Extract x-guid from response headers
        x_guid = response.headers.get("x-guid")

        # If API failed
        if response.status_code != 200:
            print("Force evaluate API failed")
            print(f"Status Code: {response.status_code}")
            print(f"x-guid: {x_guid}")
            return None

        # If empty response
        if not response.text.strip():
            print("Force evaluate API returned empty response")
            print(f"x-guid: {x_guid}")
            return None

        try:
            response_json = response.json()
            logging.info(response_json)
            return response_json
        except ValueError:
            print("Invalid JSON received in force evaluate API")
            print(f"Status Code: {response.status_code}")
            print(f"x-guid: {x_guid}")
            return None

    # interviews Grid
    @staticmethod
    def run_proctoring(token, ir_id):
        logging.info('Entered Run Proctoring')
        request = {"interviewId": int(ir_id)}
        response = requests.post(crpo_common_obj.domain +
                                 "/py/crpo/api/v1/interview/interviewer/view_proctored_data/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info(response.json())
        return response.json()

    # interviews Grid
    @staticmethod
    def lip_sync(token, ir_id):
        logging.info('Entered Lipsync')
        request = {"irId": int(ir_id)}
        response = requests.post(crpo_common_obj.domain +
                                 "/py/crpo/api/v1/interview/lipsync/get_lipsync_samples/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info(response.json())
        return response.json()

    @staticmethod
    def job_status(token, contextguid):
        logging.info('Entered Jobstatus Context id :- %s', contextguid)
        request = {"ContextGUID": contextguid}
        response = requests.post(crpo_common_obj.domain + "/py/crpo/api/v1/getStatusOfAsyncAPI",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        resp_dict = json.loads(response.content)
        logging.info(resp_dict)
        return resp_dict

    @staticmethod
    def job_status_v2(token, contextguid):

        print(contextguid)
        logging.info('Entered to jobstatus v2')

        request = {"ContextGUID":contextguid}

        job_state = "PENDING"
        resp_dict = {}

        counter = 0
        max_retry = 25

        while job_state != "SUCCESS" and counter < max_retry:

            counter += 1

            try:
                response = requests.post(crpo_common_obj.domain + "/py/crpo/api/v1/getStatusOfAsyncAPI", headers=token,
                    data=json.dumps(request, default=str), verify=False, timeout=30)

            except requests.exceptions.RequestException as e:
                print(f"job_status_v2: Request failed: {e}")
                time.sleep(10)
                continue

            # 🔐 Empty response protection
            if not response.content or not response.content.strip():
                print("job_status_v2: Empty response received")
                time.sleep(30)
                continue

            try:
                resp_dict = response.json()
            except ValueError:
                print(f"job_status_v2: Non-JSON response: {response.text}")
                time.sleep(30)
                continue

            job_state = resp_dict.get("data", {}).get("JobState", "PENDING")

            print(f"Job status: {job_state} (attempt {counter})")

            # exit immediately if finished
            if job_state == "SUCCESS":
                break

            time.sleep(30)

        logging.info(resp_dict)

        return resp_dict

    @staticmethod
    def upload_files(token, file_name, file_path):
        logging.info('Entered to upload files')
        token.pop('content-type', None)
        token.pop('X-APPLMA', None)
        request = {'file': (file_name, open(file_path, 'rb'))}
        print(token)
        print(crpo_common_obj.domain)
        token.update({'x-guid': file_name + '12_20_2021_5'})
        url = crpo_common_obj.domain + '/py/common/filehandler/api/v2/upload/.doc,.rtf,.dot,.docx,' \
                                       '.docm,.dotx,.dotm,.docb,.pdf,.xls,.xlt,.xlm,.xlsx,.xlsm,.xltx,.xltm,.xlsb,.xla,.xlam,.xll,' \
                                       '.xlw,.ppt,.pot,.pps,.pptx,.pptm,.potx,.potm,.ppam,.ppsx,.ppsm,.sldx,.sldm,.zip,.rar,.7z,.gz,.jpeg,' \
                                       '.jpg,.gif,.png,.msg,.txt,.mp4,.mvw,.3gp,.sql,.webm,.csv,.odt,.json,.ods,.ogg,.p12,/5000/'

        api_request = requests.post(url, headers=token, files=request, verify=False)
        resp_dict = json.loads(api_request.content)
        logging.info(resp_dict)
        return resp_dict

    @staticmethod
    def untag_candidate(token, data1):
        logging.info("Enterd to untag candidate %s", data1)
        for request in data1:
            response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/un-tag/",
                                     headers=token,
                                     data=json.dumps(request, default=str), verify=False)
            logging.info(response)

    @staticmethod
    def proctor_evaluation_detail_old(token, testuser_id):
        logging.info("Entered to proctor evaluation %s", testuser_id)
        token.pop('X-APPLMA', None)
        request = {"testUserId": testuser_id}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/get_proctor_detail/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        time.sleep(10)
        tu_proctor_details = response.json()
        logging.info(tu_proctor_details)
        return tu_proctor_details


    @staticmethod
    def proctor_evaluation_detail(token, testuser_id):
        logging.info("Entered to proctor evaluation %s", testuser_id)
        headers = token.copy()
        headers.pop('X-APPLMA', None)
        request_payload = {"testUserId":testuser_id}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/get_proctor_detail/",
            headers=headers, json=request_payload, verify=False)

        # Extract x-guid from response headers
        x_guid = response.headers.get("X-Guid")

        # If API failed
        if response.status_code != 200:
            print(f"API failed for testuser_id {testuser_id}")
            print(f"Status Code: {response.status_code}")
            print(f"x-guid: {x_guid}")
            return None

        # If response body is empty
        if not response.text.strip():
            print(f"Empty response received for testuser_id {testuser_id}")
            print(f"x-guid: {x_guid}")
            return None

        try:
            tu_proctor_details = response.json()
            logging.info(tu_proctor_details)
            return tu_proctor_details

        except ValueError:
            print(f"Invalid JSON received for testuser_id {testuser_id}")
            print(f"Status Code: {response.status_code}")
            print(f"x-guid: {x_guid}")
            return None

    @staticmethod
    def get_tu_proc_screen_data_old(token, testuser_id):
        logging.info("Entered to proctor evaluation %s", testuser_id)
        # token.pop('X-APPLMA', None)
        request = testuser_id
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/get_tu_proc_screen_data/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        time.sleep(10)
        tu_proctor_details = response.json()
        logging.info(tu_proctor_details)
        return tu_proctor_details

    @staticmethod
    def get_tu_proc_screen_data(token, testuser_id):
        logging.info("Entered to get TU proc screen data %s", testuser_id)
        headers = token.copy()
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/get_tu_proc_screen_data/",
            headers=headers, json=testuser_id,  # better than data=json.dumps
            verify=False)
        time.sleep(10)
        # Extract x-guid header
        x_guid = response.headers.get("x-guid")

        # If API failed
        if response.status_code != 200:
            print(f"get_tu_proc_screen_data API failed for testuser_id {testuser_id}")
            print(f"Status Code: {response.status_code}")
            print(f"x-guid: {x_guid}")
            return None

        # If empty response
        if not response.text.strip():
            print(f"Empty response for testuser_id {testuser_id}")
            print(f"x-guid: {x_guid}")
            return None

        try:
            tu_proctor_details = response.json()
            logging.info(tu_proctor_details)
            return tu_proctor_details
        except ValueError:
            print(f"Invalid JSON received for testuser_id {testuser_id}")
            print(f"Status Code: {response.status_code}")
            print(f"x-guid: {x_guid}")
            return None

    @staticmethod
    def save_apppreferences(token, content, id, type):
        logging.info("Entered to save app_preference :- %s", type)
        data = {"AppPreference": {"Id": id, "Content": content, "Type": type}, "IsTenantGlobal": True}

        response = requests.post(crpo_common_obj.domain + "/py/common/common_app_utils/save_app_preferences/",
                                 headers=token, data=json.dumps(data, default=str), verify=False)
        logging.info(response.json())
        return response.json()

    @staticmethod
    def re_initiate_automation(token, test_id, candidate_id):
        logging.info("Entered to reinitiate automation test id:- %s candidate_id:- %s", test_id, candidate_id)
        token.pop('X-APPLMA', None)
        request = {"testId": test_id, "candidateId": candidate_id}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/re_initiate_automation/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)

    @staticmethod
    def sanitise_tu_automation(token, test_user_id):
        logging.info("sanitise tu automation started for tu id :- %s", test_user_id)
        token.pop('X-APPLMA', None)
        request = {"testUserId": test_user_id}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/sanitise_tu_automation/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        data = response.json()
        logging.info(data)
        return data

    @staticmethod
    def sanitise_test_automation_test_level_execute(token, test_id):
        token.pop('X-APPLMA', None)

        request = {"invokeSync":True, "testId":test_id, "isDryRun":False}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/sanitise_test_automation/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        response = response.json()
        print(response)

        # Return full sanitisedData list
        time.sleep(10)
        return response['data']['sanitisedData']

    @staticmethod
    def sanitise_test_automation_test_level_dryrun(token, test_id):
        token.pop('X-APPLMA', None)

        request = {"invokeSync":True, "testId":test_id, "isDryRun":True}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/sanitise_test_automation/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        response = response.json()
        print(response)

        # Return full sanitisedData list
        time.sleep(10)
        return response['data']['sanitisedData']

    @staticmethod
    def sanitise_test_automation_testuser_execute(token, test_user_id, test_id):
        token.pop('X-APPLMA', None)

        # {"invokeSync":true,"testId":"27041","testUserIds":[3842257],"isDryRun":true}
        # {"invokeSync":false,"testId":"18453","testUserIds":[3842245],"isDryRun":false}

        request = {"invokeSync":True, "testId":test_id, "testUserIds":[test_user_id], "isDryRun":False}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/sanitise_test_automation/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        response = response.json()
        data = response['data']['sanitisedData'][0]['response']
        return data

    @staticmethod
    def sanitise_test_automation_testuser_dryrun(token, test_user_id, test_id):
        token.pop('X-APPLMA', None)

        request = {"invokeSync":True, "testId":test_id, "testUserIds":[test_user_id], "isDryRun":True}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/sanitise_test_automation/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        response = response.json()
        data = response['data']['sanitisedData'][0]['response']
        return data

    @staticmethod
    def tests_against_candidate(token, candidateid):
        logging.info("tests against candidate started for candidate id :-", candidateid)
        payload = {"CandidateId": candidateid}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/test/api/v1/tests-against-candidate/",
                                 headers=token,
                                 data=json.dumps(payload, default=str), verify=False)
        test_infos = response.json()
        logging.info(test_infos)
        return test_infos

    @staticmethod
    def get_all_questions(token, request_data):
        logging.info("get all candidate started")
        response = requests.post(crpo_common_obj.domain + "/py/assessment/authoring/api/v1/getAllQuestion/",
                                 headers=token,
                                 data=str(request_data.get('request')), verify=False)
        get_all_questions_resp = json.loads(response.content)
        logging.info(get_all_questions_resp)
        return get_all_questions_resp

    @staticmethod
    def generate_applicant_report(token, request_payload):
        logging.info("generate applicant report started")
        response = requests.post(crpo_common_obj.domain + "/py/common/xl_creator/api/v1/generate_applicant_report/",
                                 headers=token, data=json.dumps(request_payload, default=str), verify=False)
        resp_dict = json.loads(response.content)
        logging.info(resp_dict)
        return resp_dict

    @staticmethod
    def generate_plagiarism_report(token, request_payload):
        logging.info("Plagiarism report started")
        response = requests.post(crpo_common_obj.domain + "/py/assessment/report/api/v1/plagiarismreport/",
                                 headers=token, data=json.dumps(request_payload, default=str), verify=False)
        resp_dict = json.loads(response.content)
        logging.info(resp_dict)
        return resp_dict

    @staticmethod
    def candidate_transcript_report(token, request_payload):
        logging.info('candidatetranscript started')
        url = crpo_common_obj.domain + "/py/assessment/report/api/v1/candidatetranscript/"
        headers = token
        data = json.dumps(request_payload, default=str)
        
        max_retries = 3
        retry_delay = 2  # Initial delay in seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    data=data,
                    verify=False,
                    timeout=(30, 300)  # (connect timeout, read timeout) - 30s to connect, 5min to read
                )
                resp_dict = json.loads(response.content)
                logging.info(resp_dict)
                return resp_dict
                
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logging.warning(f'Connection error on attempt {attempt + 1}/{max_retries}: {str(e)}')
                    logging.info(f'Retrying in {wait_time} seconds...')
                    time.sleep(wait_time)
                else:
                    logging.error(f'Connection error after {max_retries} attempts: {str(e)}')
                    raise
                    
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logging.warning(f'Timeout error on attempt {attempt + 1}/{max_retries}: {str(e)}')
                    logging.info(f'Retrying in {wait_time} seconds...')
                    time.sleep(wait_time)
                else:
                    logging.error(f'Timeout error after {max_retries} attempts: {str(e)}')
                    raise
                    
            except requests.exceptions.RequestException as e:
                logging.error(f'Request error: {str(e)}')
                raise
                
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f'Failed to parse JSON response: {str(e)}')
                try:
                    logging.error(f'Response content: {response.content[:500]}')
                except NameError:
                    logging.error('Response content: No response available')
                raise

    @staticmethod
    def initiate_vendor_score(crpotoken, cid, test_id):
        logging.info('initiateVendorScore started')
        url = crpo_common_obj.domain + '/py/assessment/assessmentvendor/api/v1/initiateVendorScore/'
        data = {"testId": test_id, "candidateIds": [cid], "isForced": True}

        response = requests.post(url,
                                 headers=crpotoken,
                                 data=json.dumps(data, default=str), verify=False)
        it_vendor_resp = response.json()
        logging.info(it_vendor_resp)
        return it_vendor_resp

    @staticmethod
    def untag_candidate_by_cid(token, test_id, candidate_ids):
        logging.info("un-tag candidate started")
        data1 = [{"testId": test_id, "candidateIds": candidate_ids}]
        for request in data1:
            response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/un-tag/",
                                     headers=token,
                                     data=json.dumps(request, default=str), verify=False)
            logging.info(response)

    @staticmethod
    def create_candidate(token, usn):
        logging.info("create candidate started")
        email =  "S1N1J1E1V11111" + usn + "@gmail.com"
        remove_chars = "- :."  # characters to remove
        translation_table = str.maketrans("", "", remove_chars)
        email_id = email.translate(translation_table)

        request = {"PersonalDetails": {"FirstName": 'Muthumurugan', "Email1":email_id, "USN": usn,
                                       "DateOfBirth": "2022-02-08T18:30:00.000Z"}}
        response = requests.post(crpo_common_obj.domain + "/py/rpo/create_candidate/", headers=token,
                                 data=json.dumps(request), verify=False)
        response_data = response.json()
        candidate_id = response_data.get('CandidateId')
        if response_data.get('status') == 'OK':
            logging.info("Candidate created successfully ")
            print("candidate created in crpo")
            url = 'https://automation-in.hirepro.in/?candidate=%s' % candidate_id
        else:
            print("candidate not created in CRPO_COMMON due to some technical glitch")
            print(response_data)
            logging.info("Candidate created Failed %s" % response_data)
        return candidate_id

    @staticmethod
    def create_candidate_v2(token, request):
        logging.info("create candidate v2 %s" % request)
        response = requests.post(crpo_common_obj.domain + "/py/rpo/create_candidate/", headers=token,
                                 data=json.dumps(request), verify=False)
        response_data = response.json()
        logging.info("careate candidate api response %s" % response_data)
        candidate_id = response_data.get('CandidateId')
        if response_data.get('status') == 'OK':
            print("candidate created in crpo")
            logging.info("Candidate created successfully ")
        else:
            print("candidate not created in CRPO_COMMON due to some technical glitch")
            logging.info("Candidate not created in CRPO_COMMON due to some technical glitch")

        return candidate_id

    @staticmethod
    def tag_candidate_to_test(token, cid, testid, eventid, jobroleid):
        request = {"CandidateIds": [int(cid)], "TestIds": [int(testid)], "EventId": int(eventid),
                   "JobRoleId": int(jobroleid), "Sync": "True"}
        logging.info("Tag candidate to test Request is %s" % request)
        response = requests.post(crpo_common_obj.domain +
                                 "/py/crpo/applicant/api/v1/tagCandidatesToEventJobRoleTests/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info("Tag candidate to test Response is %s" % response)
        return response

    @staticmethod
    def test_user_credentials(token, tu_id):
        logging.info("Begin getCredential api")
        request = {"testUserId": tu_id}
        response = requests.post(crpo_common_obj.domain +
                                 "/py/assessment/testuser/api/v1/getCredential/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info("End of getCredential api %s", response)
        return response.json()

    @staticmethod
    def get_all_test_user(token, cid):
        logging.info("Begin getAllTestUser api")
        request = {"isMyAssessments": False, "search": {"candidateIds": [cid]}}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/getAllTestUser/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        data = response.json()
        test_user_id = data['data']['testUserInfos'][0]['id']
        logging.info("End of getAllTestUser api %s" % data)
        return test_user_id

    @staticmethod
    def get_candidate_by_id(token, cid):
        logging.info("Begin get_candidate_details_by_id api")
        request = {"CandidateId": cid, "RequiredDetails": [1]}
        response = requests.post(crpo_common_obj.domain + "/py/rpo/get_candidate_details_by_id/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        candidate_details = response.json()
        logging.info("End of get_candidate_details_by_id api %s", candidate_details)
        return candidate_details

    @staticmethod
    def get_all_event(token):
        logging.info("Begin getAllEvent api")
        request = {"Paging": {"MaxResults": 20, "PageNumber": 1, "IsCountRequired": True}, "isAllEventRequired": False,
                   "Sort": 0, "Order": 0, "Search": None,
                   "flags": {"isAllEventOwnersRequired": False, "isEventCollegesRequired": True,
                             "isEventActivityCountRequired": False, "isEventApplicantCountRequired": True}, "Status": 1}
        response = requests.post(crpo_common_obj.domain + "/py/crpo/event/api/v1/getAllEvent/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info("End of getAllEvent api %s" % response)
        candidate_details = response.json()

        return candidate_details

    @staticmethod
    def create_question(token, request):
        logging.info("Begin of createQuestion api")
        response = requests.post(crpo_common_obj.domain + "/py/assessment/authoring/api/v1/createQuestion/",
                                 headers=token, data=json.dumps(request), verify=False)
        question_id_resp = response.json()
        question_id = question_id_resp['data']['questionId']
        logging.info("End of createQuestion api %s" % question_id_resp)
        return question_id

    @staticmethod
    def get_question_for_id(token, question_id):
        request = {"id": question_id}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/authoring/api/v1/getQuestionForId/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        question_id_details = response.json()
        return question_id_details

    @staticmethod
    def get_exported_question_data(token, question_id):
        request = {"questionId": question_id}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/authoring/api/v1/getExportedQuestionData/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        exported_qn_details = response.json()
        return exported_qn_details

    @staticmethod
    def get_question_dump(token, question_id, qtype):
        request = {"questionIds":[question_id]}
        api = "/py/assessment/authoring/api/v1/getQuestionsDump/"
        if qtype.lower() == 'mcq':
            response = requests.post(crpo_common_obj.domain + api,headers=token,
                                     data=json.dumps(request, default=str), verify=False)
        else:
            api = "/py/assessment/authoring/api/v1/getQuestionsDump/" +qtype.lower()+'/'
            response = requests.post(crpo_common_obj.domain + api,headers=token,
                                     data=json.dumps(request, default=str), verify=False)
        question_dump = response.json()
        return question_dump

    @staticmethod
    def create_question_using_dump(token, request_data):
        request =  {
            "questionsDump": request_data,
            "invokeSync": False
        }
        # request = {"questionIds": [question_id]}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/authoring/api/v1/createQuestionsUsingDump/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        question_id_details = response.json()
        return question_id_details

    @staticmethod
    def calculate_question_statistics(token, question_ids):
        request = {"isPagingRequired": True, "questionIds": question_ids, "isComputeOnly": False,
                   "questionConfig": {"dontUpdateSystemDifficulty": False}}
        response = requests.post(
            crpo_common_obj.domain + "/py/assessment/report/api/v1/question_statistics/?isSync=false",
            headers=token,
            data=json.dumps(request, default=str), verify=False)
        question_status = response.json()
        question_status_context_id = question_status['data']['ContextId']
        return question_status_context_id

    @staticmethod
    def calculate_hirepro_question_statistics(token, question_ids):
        request = {"questionIds": question_ids, "isComputeOnly": False}
        print(request)
        response = requests.post(
            crpo_common_obj.domain + "/py/assessment/report/api/v1/hirepro_question_stats_api/",
            headers=token,
            data=json.dumps(request, default=str), verify=False)
        question_status = response.json()
        question_status_context_id = question_status['data']['ContextId']
        return question_status_context_id

    @staticmethod
    def calculate_question_statistics_for_tests(token, test_ids):
        request = {"testIds": [test_ids]}
        response = requests.post(
            crpo_common_obj.domain + "/py/assessment/report/api/v1/question_statistics_for_tests/?isSync=false",
            headers=token,
            data=json.dumps(request, default=str), verify=False)
        question_stats = response.json()
        test_question_stats_context_id = question_stats['data']['ContextId']
        return test_question_stats_context_id

    @staticmethod
    def get_test_user_infos(token, payload):
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/info/",
                                 headers=token,
                                 data=json.dumps(payload, default=str), verify=False)
        test_user_infos = response.json()
        return test_user_infos

    @staticmethod
    def search_test_user_by_cid_and_testid(token, cid, test_id):
        logging.info('Entered in to search_test_user_by_cid_and_testid method')

        request = {"isPartnerTestUserInfo": True, "testId": test_id,
                   "search": {"status": 6, "candidateSearch": {"ids": [cid]}}}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/getTestUsersForTest/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        data = response.json()
        if 'testInfo' in data['data']:
            test_user_id = data['data']['testUserInfos'][0]['applicantBasicInfos'][0]['testUserId']
            copied_test_user_id = data['data']['testUserInfos'][0]['copiedTestUserId']
            offline_attended = data['data']['testUserInfos'][0]['isOffline']
            # total_score = int(data['data']['testUserInfos'][0]['totalScore'])
            test_user_data = {'testUserId': test_user_id, 'parentTestUserId': copied_test_user_id,
                              'Offline': offline_attended}
        else:
            test_user_data = {'testUserId': "NotExist", 'parentTestUserId': "EMPTY",
                              'Offline': "EMPTY"}
        logging.info('Exited from search_test_user_by_cid_and_testid method')

        return test_user_data

    @staticmethod
    def get_test_user_infos_v2(token, tuid):
        payload = {"testUserId": tuid, "requiredFlags": {"isGroupSectionWiseMarks": True, "isVendorDetails": True,
                                                         "isCodingSummary": False}}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/info/",
                                 headers=token,
                                 data=json.dumps(payload, default=str), verify=False)
        test_user_infos = response.json()
        return test_user_infos

    @staticmethod
    def change_applicant_status(token, applicant_id, event_id, jobrole_id, status_id):
        logging.info(
            "Changing applicant status for applicant id {0},eventid: {1}, jobrole_id:{2} statusid: {status_id}",
            applicant_id, event_id, jobrole_id, status_id)
        payload = {"ApplicantIds": [applicant_id], "EventId": event_id, "JobRoleId": jobrole_id,
                   "ToStatusId": status_id,
                   "Sync": "False", "Comments": "", "InitiateStaffing": False}
        response = requests.post(crpo_common_obj.domain + "/py/crpo/applicant/api/v1/applicantStatusChange/",
                                 headers=token,
                                 data=json.dumps(payload, default=str), verify=False)
        test_user_infos = response.json()
        logging.info("Successfully changed applicant status")
        return test_user_infos

    @staticmethod
    def get_applicant_infos(token, candidate_id):
        payload = {"CandidateIds": [candidate_id]}
        response = requests.post(crpo_common_obj.domain + "/py/crpo/applicant/api/v1/getApplicantsInfo/",
                                 headers=token,
                                 data=json.dumps(payload, default=str), verify=False)
        applicant_infos = response.json()
        return applicant_infos

    @staticmethod
    def force_untag_testuser(token, test_user_id):
        logging.info('Entered in to Force Untag and untagging tu: {0}', test_user_id)
        request = {"testUserIds": [test_user_id], "isForced": True}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/un-tag/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info('Successfully untagged tu: {0}', test_user_id)
        return response

    @staticmethod
    def persistent_save(token, s3_url):
        request = [{
            "origFileUrl": s3_url,
            "relativePath": "at/proctor/image/10324/1367938", "isSync": True, "targetBucket": "recording-bucket",
            "metaData": None}]
        response = requests.post(crpo_common_obj.pearson_domain +
                                 "/py/common/filehandler/api/v2/persistent-save/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        resp = json.loads(response.content)
        return resp

    @staticmethod
    def persistent_save_v2(token, request):
        # request =  [{"relativePath":"AT/question",
        #              "origFileUrl":s3_url,"isSync":True}]
        response = requests.post(crpo_common_obj.pearson_domain +
                                 "/py/common/filehandler/api/v2/persistent-save/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        resp = json.loads(response.content)
        return resp

    @staticmethod
    def check_audio_distortion(token, s3_persistent_url):
        request = {"FileUrl": s3_persistent_url}
        response = requests.post(crpo_common_obj.pearson_domain +
                                 "/py/common/voice_distortion/check_audio_distortion/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        resp = json.loads(response.content)
        print(s3_persistent_url)
        print("Is Server by ECS - Loginto test v2", response.headers.get('x-ecsnode'))
        print("Is Server by ECS - Loginto test v2", response.headers.get('x-isecs'))
        return resp

    @staticmethod
    def get_app_preference(domain, token):
        request = {}
        response = requests.post(domain + "/py/assessment/test/api/v1/getAll/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        get_all_resp = response.json()
        # get_all_resp_status = get_all_resp['status']
        return get_all_resp

    @staticmethod
    def app_node_by_random_api(domain, token):
        request = {}

        response = requests.post(domain + "/py/assessment/test/api/v1/getAll/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        app_node = response.headers.get('X-APP_NODE')
        get_all_resp = response.json()
        resp = {'app_node': app_node, 'get_all_resp': get_all_resp}
        return resp

    @staticmethod
    def update_role(request, token):
        response = requests.post(crpo_common_obj.domain + "/py/common/role/update/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        update_role = response.json()
        return update_role

    @staticmethod
    def get_app_preference(token):
        request = {"Type": "crpo.dashboard.config", "IsTenantGlobal": True}
        response = requests.post(crpo_common_obj.domain + "/py/common/common_app_utils/api/v1/getAppPreference/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        app_preference = response.json()
        return app_preference

    @staticmethod
    def auth_user_v2(token):
        request = {}

        response = requests.post(crpo_common_obj.domain + "/py/common/user/auth_user_v2/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        auth_user_v2 = response.json()
        return auth_user_v2

    @staticmethod
    def generating_backend_token(integration_id, client_id, client_secret):
        header = {"content-type": "application/json"}
        data = {"client_id": client_id, "client_secret": client_secret}
        url = crpo_common_obj.domain + "/py/oauth2/" + integration_id + "/access_token/"
        print(url)
        response = requests.post(url, headers=header, data=json.dumps(data), verify=False)
        login_response = response.json()
        headers = {"content-type": "application/json", "APP-NAME": "CRPO", "X-APPLMA": "true", "App-Server": "py310app",
                   "Authorization": "bearer " + login_response.get("access_token")}
        print(headers)
        return headers

    @staticmethod
    def download_assessment_docket(token, request_payload):
        response = requests.post(
            crpo_common_obj.domain + "/py/assessment/report/api/v1/get_cand_src_code_and_attachments/",
            headers=token, data=json.dumps(request_payload, default=str), verify=False)
        resp_dict = json.loads(response.content)

        return resp_dict

    @staticmethod
    def generating_ui_token(integration_id, client_id, admin_token, cid, event_id, job_id):
        header = {"content-type": "application/json", "isClientUpdatedWithCaptcha": "true"}
        data = {"client_id": client_id}
        url = crpo_common_obj.domain + "/py/oauth2/" + integration_id + "/access_token/"
        print(url)
        response = requests.post(url, headers=header, data=json.dumps(data), verify=False)
        access_token = response.json()
        print(access_token)

        data_get_hash = {"candidateId": cid, "eventId": event_id, "jobId": job_id}
        get_hash_url = crpo_common_obj.domain + "/py/crpo/assessment/slotmgmt/recruiter/api/v1/getHash/"
        get_hash_resp = requests.post(get_hash_url, headers=admin_token, data=json.dumps(data_get_hash), verify=False)
        get_hash_response = get_hash_resp.json()
        hash = get_hash_response['data']['hash']
        print(get_hash_response)

        data_verify_hash = {"data": "candidate=" + str(cid) + "&event=" + str(event_id) + "&job=" + str(job_id),
                            "hash": hash}
        verify_hash_url = crpo_common_obj.domain + "/py/crpo/assessment/slotmgmt/candidate/api/v1/verifyHash/"
        verify_hash_resp = requests.post(verify_hash_url, headers=admin_token, data=json.dumps(data_verify_hash),
                                         verify=False)
        verify_hash_response = verify_hash_resp.json()
        print(verify_hash_response)
        ui_token = {"authorization": "bearer " + access_token.get('access_token')}
        return ui_token

    @staticmethod
    def generating_slots(token, event_id):
        data = {"eventId": event_id}
        url = crpo_common_obj.domain + "/py/crpo/assessment/slotmgmt/candidate/api/v1/getAllSlots/"
        print(url)
        response = requests.post(url, headers=token, data=json.dumps(data), verify=False)
        slot_response = response.json()
        return slot_response

    @staticmethod
    def get_app_preference_generic(token, request):
        response = requests.post(crpo_common_obj.domain + "/py/common/common_app_utils/api/v1/getAppPreference/",
                                 headers=token, data=json.dumps(request, default=str), verify=False)
        # print(response.headers.get('X-APP_NODE'))
        app_preference = response.json()
        return app_preference

    @staticmethod
    def update_api_audit(token, req):
        response = requests.post(crpo_common_obj.domain + "/py/hirepro_admin/api_audit_config/update_api_audit_config/",
                                 headers=token,
                                 data=json.dumps(req), verify=False)
        print(response)
        return response

    @staticmethod
    def update_tenant_config(token, tenant_id, encr):
        request = {"id": tenant_id, "tenant": {
            "additionalConfig": {"isEuTenant": False, "payloadEncryptionConfig": {"isResponseEncrypted": encr},
                                 "bucketConfig": {}, "samlDomain": ""}}, "masterConfiguration": {"loginStrategy": ""}}
        print(request)
        response = requests.post(crpo_common_obj.domain + "/py/hirepro_admin/tenant/api/v1/update/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        print(response)
        return response

    @staticmethod
    def clear_tenant_cache(token, tenant):
        request = {"aliasList": [tenant]}
        response = requests.post(crpo_common_obj.domain + "/py/common/api/v1/ctic/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        print("Tenant cache cleared for", tenant)
        print(response)
        return response.json()

    @staticmethod
    def security_login_to_crpo(login_name, password, tenant):
        header = {"content-type": "application/json", "X-APPLMA": "true", "App-Server": "py310app"}
        data = {"LoginName": login_name, "Password": password, "TenantAlias": tenant, "UserName": login_name}
        response = requests.post(crpo_common_obj.domain + "/py/common/user/v2/login_user/", headers=header,
                                 data=json.dumps(data), verify=False)
        return response.content

    @staticmethod
    def get_tu_proc_screen_data_v2(token, payload):
        response = requests.post(crpo_common_obj.domain + "/py/assessment/testuser/api/v1/get_tu_proc_screen_data/",
                                 headers=token,
                                 data=json.dumps(payload, default=str), verify=False)
        proctored_data = response.json()
        return proctored_data

    @staticmethod
    def audio_transcript(token, request_payload):
        response = requests.post(crpo_common_obj.domain + "/py/assessment/report/api/v1/candidatetranscript/",
                                 headers=token, data=json.dumps(request_payload, default=str), verify=False)
        resp_dict = json.loads(response.content)
        return resp_dict

    def clear_test_results(self, token, request_payload):
        response = requests.post(crpo_common_obj.domain + "/py/assessment/eval/api/v1/ccsr_eval/",
                                 headers=token, data=json.dumps(request_payload, default=str), verify=False)
        resp_dict = json.loads(response.content)
        return resp_dict

    def evaluate_candidate(self, token, request_payload):
        response = requests.post(crpo_common_obj.domain + "/py/assessment/eval/api/v1/eval-online-assessment/",
                                 headers=token, data=json.dumps(request_payload, default=str), verify=False)
        resp_dict = json.loads(response.content)
        return resp_dict

    @staticmethod
    def send_test_user_credntials(token, test_user_id):
        request_payload = {"testUserIds": [test_user_id], "isSync": False}
        print(test_user_id)
        response = requests.post(crpo_common_obj.domain +
                                 "/py/assessment/htmltest/api/v1/sendTestUserCredential/",
                                 headers=token, data=json.dumps(request_payload, default=str), verify=False)
        time.sleep(2)
        return response.json()

    @staticmethod
    def login_to_test(login_name, password, tenant):
        header = {"content-type": "application/json", "X-APPLMA": "true", "APP-NAME": "onlineassessment",
                  "App-Server": "py310app"}
        data = {"LoginName": login_name, "Password": password, "TenantAlias": tenant}
        response = requests.post(crpo_common_obj.domain + "/py/assessment/htmltest/api/v2/login_to_test/",
                                 headers=header,
                                 data=json.dumps(data), verify=False)
        print("Is Server by ECS - Login to test", response.headers.get('X-ServedByEcs'))
        login_response = response.json()
        login_response = {"content-type": "application/json", "X-AUTH-TOKEN": login_response.get("Token"),
                          "X-APPLMA": "true"}
        return login_response

    @staticmethod
    def final_submit(assessment_token, request):
        print(assessment_token)
        url = crpo_common_obj.domain + '/py/assessment/htmltest/api/v1/finalSubmitTestResult/'
        response = requests.post(url,
                                 headers=assessment_token,
                                 data=json.dumps(request, default=str), verify=False)
        print("Is Server by ECS - submit test result", response.headers.get('X-ServedByEcs'))
        json_resp = response.json()
        if json_resp.get('isResultSubmitted'):
            submit_xauth_token = json_resp.get('systemTkn')
        else:
            print("The Result is not submitted")
            submit_xauth_token = None
        submit_token = {'X-AUTH-TOKEN': submit_xauth_token, "X-APPLMA": "true", "APP-NAME": "onlineassessment"}
        return submit_token

    @staticmethod
    def initiate_automation(submit_token, req):
        url = crpo_common_obj.domain + '/py/assessment/testuser/api/v2/initiate_automation/'
        # data = {"candidateId": int(cid), "testId": test_id, "debugTimeStamp": "2020-07-14T07:32:54.904Z"}
        response = requests.post(url,
                                 headers=submit_token,
                                 data=json.dumps(req, default=str), verify=False)
        print("Is Server by ECS - initiate automation", response.headers.get('X-ServedByEcs'))
        itua_resp = response.json()
        print(response.headers.get('X-GUID'))
        print(itua_resp)
        return itua_resp

    # InterviewBot Grid
    @staticmethod
    def generate_feedback(token, interview_id):
        logging.info('Entered Run Proctoring')
        request = {"InterviewId": int(interview_id)}
        response = requests.post(crpo_common_obj.domain +
                                 "/py/interview_bot/generate_feedback/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info(response.json())
        generate_feedback_resp = response.json()
        return generate_feedback_resp

    # InterviewBot Grid
    @staticmethod
    def get_interview_by_id(token, interview_id):
        logging.info('Entered Run Proctoring')
        request = {"InterviewId": int(interview_id)}
        response = requests.post(crpo_common_obj.domain +
                                 "/py/interview_bot/get_interview_by_id/",
                                 headers=token,
                                 data=json.dumps(request, default=str), verify=False)
        logging.info(response.json())
        get_interview_by_id_resp = response.json()
        return get_interview_by_id_resp


crpo_common_obj = CrpoCommon()
