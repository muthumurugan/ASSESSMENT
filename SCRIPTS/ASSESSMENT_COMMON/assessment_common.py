import requests
import json
from SCRIPTS.ASSESSMENT_COMMON import submit_test_data
from SCRIPTS.COMMON.environment import *
import time


class AssessmentCommon:
    main_domain = env_obj.domain
    pearson_domain = env_obj.pearson_domain
    eu_domain = env_obj.eu_domain
    cocubes_domain = env_obj.cocubes_domain
    talentlens_domian = env_obj.talentlens_domain

    @staticmethod
    def login_to_test(login_name, password, tenant):
        header = {"content-type": "application/json", "X-APPLMA": "true", "APP-NAME": "onlineassessment","App-Server": "py310app"}
        data = {"LoginName": login_name, "Password": password, "TenantAlias": tenant}
        response = requests.post(assessment_common_obj.main_domain + "/py/assessment/htmltest/api/v2/login_to_test/",
                                 headers=header,
                                 data=json.dumps(data), verify=False)
        print("Is Server by ECS - Login to test", response.headers.get('X-ServedByEcs'))
        login_response = response.json()
        # login_response = {"content-type": "application/json", "X-AUTH-TOKEN": login_response.get("Token"),
        #                   "X-APPLMA": "true"}
        return login_response

    def decide_domain(self, type_of_test):
        print(type_of_test)
        if type_of_test == 'HP':
            domain = assessment_common_obj.main_domain
        elif type_of_test == 'Cocubes':
            domain = assessment_common_obj.cocubes_domain
        elif type_of_test == 'TALENTLENS':
            domain = assessment_common_obj.talentlens_domian
        elif type_of_test == 'VET':
            domain = assessment_common_obj.pearson_domain
        else:
            domain = assessment_common_obj.main_domain
        return domain

    @staticmethod
    def login_to_test_v2(login_name, password, tenant, domain):
        print(login_name, password, domain)
        header = {"content-type": "application/json", "APP-NAME": "onlineassessment", "X-APPLMA": "true","App-Server": "py310app"}
        data = {"LoginName": login_name, "Password": password, "TenantAlias": tenant}
        login_url = domain + '/py/assessment/htmltest/api/v2/login_to_test/'
        response = requests.post(login_url, headers=header, data=json.dumps(data), verify=False)
        print("Is Server by ECS - Loginto test v2", response.headers.get('X-ServedByEcs'))
        login_response = response.json()
        print(login_response)
        login_token = {}
        are_you_able_to_login = 'No'
        test_type = 'EMPTY'
        if login_response.get('status') == 'OK':
            test_type = json.loads(login_response.get('Config')).get('thirdPartyTestType')
            if not test_type:
                test_type = 'HP'
            are_you_able_to_login = 'Yes'
            login_token = {'X-AUTH-TOKEN': login_response.get("Token"), "X-APPLMA": "true",
                           "APP-NAME": "onlineassessment"}

        elif login_response.get('error').get('errorCode'):
            print("Login Status :- KO ")
            next_test_flags = login_response.get('error').get('nextTestFlags')
            if next_test_flags.get('isShortlisted') or next_test_flags.get('isShortlisted') == None:
                are_you_able_to_login = 'Yes'
        else:
            print("Login Failed")

        # Below code returns respective values if available otherwise it will return "Login Failed"
        test_user_infos = {'nextTestID': login_response.get("TestId", "Login Failed"),
                           'nextTestName': login_response.get("TestName", "Login Failed"),
                           'nextTestCandidateId': login_response.get("CandidateId", "Login Failed"),
                           'login_staus': are_you_able_to_login, 'next_test_type': test_type}

        login_resp = {"login_token": login_token, "domain": domain, "test_user_infos": test_user_infos,
                      "login_response": login_response}

        return login_resp

    @staticmethod
    def submit_test_result(assessment_token, domain, submit_test_request):
        print(assessment_token)
        url = domain + '/py/assessment/htmltest/api/v1/finalSubmitTestResult/'
        data1 = submit_test_data.alldata.get(str(submit_test_request))
        response = requests.post(url,
                                 headers=assessment_token,
                                 data=json.dumps(data1, default=str), verify=False)
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
    def pearson_call_backs(test_user_id, score_details, tenant):

        print(test_user_id, score_details)
        content = """<?xml version = "1.0" encoding = "UTF-8"?>
          <imsx_POXEnvelopeRequest xmlns = "http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">
            <imsx_POXHeader>
              <imsx_POXRequestHeaderInfo>
                <imsx_version>V1.0</imsx_version>
                <imsx_messageIdentifier>7777897</imsx_messageIdentifier>
              </imsx_POXRequestHeaderInfo>
            </imsx_POXHeader>
            <imsx_POXBody>
              <replaceResultRequest>
                <resultRecord>
                  <sourcedGUID>
                    <sourcedId>{test_user_id}</sourcedId>
                  </sourcedGUID>
                  <tin>
                    <tinID>28035214</tinID>
                  </tin>
                  <result>
                    <resultScore>
                      <language>en</language>
                      <textString>{score_response}</textString>
                    </resultScore>
                  </result>
                </resultRecord>
              </replaceResultRequest>
            </imsx_POXBody>
          </imsx_POXEnvelopeRequest> """

        content = content.format(test_user_id="%s" % test_user_id, score_response="%s" % score_details)
        print(content)
        # AUTOMATION
        if tenant == 'AUTOMATION':
            response = requests.post(assessment_common_obj.pearson_domain +
                                     "/py/assessment/assessmentvendor/api/v1/vcb/versant/?tn=76EF28AF-6DB5-11EA-8197-0262BDD19558",
                                     headers={"Content-Type": "application/xml"}, data=content)

        elif tenant == 'AT':
            response = requests.post(assessment_common_obj.pearson_domain +
                                     "/py/assessment/assessmentvendor/api/v1/vcb/versant/?tn=EE596328-A963-11EA-9A76-0262BDD19558",
                                     headers={"Content-Type": "application/xml"}, data=content)
        else:
            print("This is Pearson Callbacks please specify the tenant")

        print("Is Server by ECS - Pearson callbacks", response.headers.get('X-ServedByEcs'))

        print(response.headers)
        print(response)
        print(response.content)

    @staticmethod
    def initiate_automation(submit_token, cid, test_id, domain):
        context_id = None
        next_test_info = None
        url = domain + '/py/assessment/testuser/api/v2/initiate_automation/'
        data = {"candidateId": int(cid), "testId": test_id, "debugTimeStamp": "2020-07-14T07:32:54.904Z"}
        response = requests.post(url,
                                 headers=submit_token,
                                 data=json.dumps(data, default=str), verify=False)
        print("Is Server by ECS - initiate automation", response.headers.get('X-ServedByEcs'))
        itua_resp = response.json()
        print(response.headers.get('X-GUID'))
        print(itua_resp)
        return itua_resp

    @staticmethod
    def get_job_status(token, context_id):
        json_resp = {}
        status = 'Pending'
        data = {"ContextGUID": context_id, "disableBlockUI": True,
                "debugTimeStamp": "2020-12-22T14:13:50.704Z"}
        # print(data)
        while status != 'SUCCESS':
            response = requests.post(
                assessment_common_obj.main_domain + "/py/crpo/api/v1/getStatusOfAsyncAPI",
                headers=token,
                data=json.dumps(data, default=str), verify=False)
            print("Is Server by ECS - assess - job status", response.headers.get('X-ServedByEcs'))
            json_resp = response.json()
            status = json_resp['data']['JobState']
            print(json_resp)
            time.sleep(3)

        return json_resp

    @staticmethod
    def process_next_test_links_for_chaining(json_resp, previous_domain):
        print("job status changed to success")
        job_status_result = json_resp['data']['Result']
        next_test_info = json.loads(job_status_result)
        is_shortlisted = next_test_info['data']['isAutoShortlisting']
        if is_shortlisted:
            print("This is SLC test")
            actual_status = "Shortlisted"
            is_slc_or_auto = 'slc'
        else:
            print("This is Auto Test")
            actual_status = "EMPTY"
            is_slc_or_auto = 'auto'
        if next_test_info['data']['nextTestInfos']:
            is_next_test_infos_available = "Yes"
            next_test_infos = (next_test_info['data']['nextTestInfos'][0])
            proxy_url = next_test_infos.get('proxyUrl')
            if proxy_url:
                domain = proxy_url.split('/')
                domain = domain[2]
                host = previous_domain.split('/')
                next_test_domain_and_host = 'https://' + domain
            else:
                proxy_url = previous_domain
                next_test_domain_and_host = previous_domain
            next_test_login_id = next_test_infos.get('loginId')
            next_test_pwd = next_test_infos.get('password')

        else:
            actual_status = "Rejected"
            next_test_domain_and_host = previous_domain
            is_next_test_infos_available = "No"
            next_test_domain_and_host = "EMPTY"
            next_test_login_id = "EMPTY"
            next_test_pwd = "EMPTY"
            is_slc_or_auto = 'No Chaining'
            print("Candidate is not shortlisted for the next test due to low score or no education profile.")

        next_test = {'actualStatus': actual_status, "nextTestDomainHost": next_test_domain_and_host,
                     'nextTestAvailability': is_next_test_infos_available,
                     'next_test_login_id': next_test_login_id,
                     'next_test_pwd': next_test_pwd, 'is_slc_or_auto': is_slc_or_auto}
        return next_test

    @staticmethod
    def next_test_info_for_2nd_login(login_name, password, tenant, domain):
        second_login_data = {}
        header = {"content-type": "application/json", "APP-NAME": "onlineassessment", "X-APPLMA": "true","App-Server": "py310app"}
        data = {"loginName": login_name, "password": password, "tenantAlias": tenant,
                "debugTimeStamp": "2020-12-02T13:32:30.749Z"}
        login_url = domain + '/py/assessment/htmltest/api/v1/test-user-next_test/'
        response = requests.post(login_url, headers=header, data=json.dumps(data), verify=False)
        print("Is Server by ECS - next test link for 2nd login", response.headers.get('X-ServedByEcs'))
        second_login_response = response.json()
        data = second_login_response.get('nextTestInfos')[0]
        if data.get('isShortlisted'):
            second_login_is_shortlisted = "slc"
        else:
            second_login_is_shortlisted = "auto"

        if data.get('proxyUrl'):
            host = domain.split('/')
            domain = data.get('proxyUrl')

        second_login_data = {'second_login_cid': data.get('candidateId'), 'second_login_test_id': data.get('testId'),
                             'second_test_login_id': data.get('loginId'), 'second_test_password': data.get('password'),
                             'login_url': domain, 'second_login_is_shortlisted': second_login_is_shortlisted}
        return second_login_data

    @staticmethod
    def login_to_test_v3(login_name, password, tenant, domain):
        print(login_name, password, domain)
        header = {"content-type": "application/json", "X-APPLMA": "true","App-Server": "py310app"}
        data = {"LoginName": login_name, "Password": password, "TenantAlias": tenant}
        login_url = domain + '/py/assessment/htmltest/api/v2/login_to_test/'
        response = requests.post(login_url, headers=header, data=json.dumps(data), verify=False)
        print("Is Server by ECS - LogintoTest V3", response.headers.get('X-ServedByEcs'))
        login_response = response.json()
        login_token = {}
        test_user_infos = {}
        if login_response.get('status') == 'OK':
            test_type = json.loads(login_response.get('Config')).get('thirdPartyTestType')
            if not test_type:
                test_type = 'HP'
            are_you_able_to_login = 'Yes'
            login_token = {'X-AUTH-TOKEN': login_response.get("Token"), "X-APPLMA": "true",
                           "APP-NAME": "onlineassessment"}
            test_user_infos = {'nextTestID': login_response.get("TestId"),
                               'nextTestName': login_response.get("TestName"),
                               'nextTestCandidateId': login_response.get("CandidateId"),
                               'login_staus': are_you_able_to_login, 'next_test_type': test_type}

        elif login_response.get('error').get('errorCode'):
            print("Login Status :- KO ")
            nextTestFlags = login_response.get('error').get('nextTestFlags')
            if nextTestFlags.get('isShortlisted') or nextTestFlags.get('isShortlisted') == None:
                are_you_able_to_login = 'Yes'
            else:
                are_you_able_to_login = 'No'
            test_type = 'EMPTY'
            test_user_infos = {'nextTestID': "Login Failed",
                               'nextTestName': "Login Failed",
                               'nextTestCandidateId': "Login Failed",
                               'login_staus': are_you_able_to_login, 'next_test_type': test_type}

        else:
            print("Login Failed")
            are_you_able_to_login = 'No'
            test_type = 'EMPTY'
            test_user_infos = {'nextTestID': "Login Failed",
                               'nextTestName': "Login Failed",
                               'nextTestCandidateId': "Login Failed",
                               'login_staus': are_you_able_to_login, 'next_test_type': test_type}

        login_resp = {"login_token": login_token, "domain": domain, "test_user_infos": test_user_infos,
                      "login_response": login_response}

        return login_resp

    @staticmethod
    def analyze_image(token, file_name, file_path):
        context_id = None
        next_test_info = None
        # url = domain + 'testuser/api/v1/initiate_automation/'
        # url = assessment_common_obj.main_domain + 'testuser/api/v2/initiate_automation/'
        token.pop('content-type', None)
        token.pop('X-APPLMA', None)
        request = {'file': (file_name, open(file_path, 'rb'))}
        token.update({'x-guid': file_name + '12_20_2021_5'})
        print(token.get('x-guid'))
        url = assessment_common_obj.main_domain + '/py/common/face_comparison/v2/analyze_image/true/false/false'
        print(url)
        print(request)
        api_request = requests.post(url, headers=token, files=request, verify=False)
        print("Is Server by ECS - analyze image", api_request.headers.get('X-ServedByEcs'))
        # print(api_request.headers.get('X-GUID'))
        resp_dict = json.loads(api_request.content)
        # print(resp_dict)
        return resp_dict

    @staticmethod
    def code_compiler(token, request):
        json_resp = {}
        response = requests.post(
            assessment_common_obj.main_domain + "/py/assessment/htmltest/api/v1/code-compiler/",
            headers=token,
            data=json.dumps(request, default=str), verify=False)
        print(response)
        print("Is Server by ECS - Code compiler", response.headers.get('X-ServedByEcs'))
        code_token = response.json()
        return code_token

    @staticmethod
    def code_compiler_explicit(token, request):
        json_resp = {}
        response = requests.post(
            assessment_common_obj.main_domain + "/py/assessment/htmltest/api/v1/code-compiler-explicit/",
            headers=token,
            data=json.dumps(request, default=str), verify=False)
        print(response)
        print("Is Server by ECS - Code compiler", response.headers.get('X-ServedByEcs'))
        code_token = response.json()
        return code_token

    @staticmethod
    def code_compiler_get_result(token, request):
        compilation_results = {}
        status = 'Pending'
        counter = 1

        while status != 'SUCCESS' and counter <= 12:
            counter += 1
            response = requests.post(
                assessment_common_obj.main_domain + "/py/assessment/htmltest/api/v1/code-compiler-get-result/",
                headers=token,
                data=json.dumps(request, default=str), verify=False)
            print("Is Server by ECS - Code compiler Result", response.headers.get('X-ServedByEcs'))
            compilation_results = response.json()

            if compilation_results.get('codingCompileResponse') is None:
                time.sleep(5)
            else:
                status = "SUCCESS"

        if status != "SUCCESS":
            print("TimedOut")

        return compilation_results

    @staticmethod
    def code_compiler_get_result_explicit(token, request):
        compilation_results = {}
        status = 'Pending'
        counter = 1
        if counter <= 12:
            while status != 'SUCCESS':
                counter += 1
                response = requests.post(
                    assessment_common_obj.main_domain + "/py/assessment/htmltest/api/v1/code-compiler-get-result-explicit/",
                    headers=token,
                    data=json.dumps(request, default=str), verify=False)
                print("Is Server by ECS - Code compiler Result", response.headers.get('X-ServedByEcs'))
                compilation_results = response.json()
                print(compilation_results)
                if compilation_results['codingCompileResponse'] is None:
                    time.sleep(5)
                else:
                    status = "SUCCESS"
        else:
            print("TimedOut")
        return compilation_results

    @staticmethod
    def get_test_basic_info(token):
        request = {}
        response = requests.post(
            assessment_common_obj.main_domain + "/py/assessment/htmltest/api/v1/get-test-basic-info/",
            headers=token,
            data=json.dumps(request, default=str), verify=False)
        resp_dict = json.loads(response.content)
        return resp_dict


assessment_common_obj = AssessmentCommon()
# test_user_id = 880555
# score_details = [{"scoreComponent": "Overall", "scoreValue": 70.0, "minScore": 20, "maxScore": 80}]
# assessment_common_obj.pearson_call_backs(test_user_id, score_details)
