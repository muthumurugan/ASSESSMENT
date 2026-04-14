from SCRIPTS.CRPO_COMMON.crpo_common import *
from SCRIPTS.CRPO_COMMON.credentials import *
from SCRIPTS.COMMON.read_excel import *
from SCRIPTS.COMMON.write_excel_new import *
from SCRIPTS.COMMON.io_path import *
from SCRIPTS.CRPO_COMMON.proc_eval_config import *
import json
import time


class ReadingDetectionEvaluation:
    def __init__(self):
        # Use dedicated reading detection output path
        write_excel_object.save_result(output_path_reading_detection_evaluation)

        # 0th Row Header
        header = ['Reading Detection Proctoring Evaluation']
        write_excel_object.write_headers_for_scripts(0, 0, header, write_excel_object.black_color_bold)

        # 1st Row Header
        header = [
            'Testcases', 'Status', 'Test ID', 'Candidate ID', 'Testuser ID',
            'Expected Reading Status', 'Actual Reading Status',
            'Expected Overall Proctoring Status', 'Actual Overall Proctoring Status',
            'Expected Overall Rating', 'Actual Overall Rating',
            'Expected Video Proctoring Status', 'Actual Video Proctoring Status',
            'Expected Proctoring Reason', 'Actual Proctoring Reason',
            'Expected Overall Proctoring Reason', 'Actual Overall Proctoring Reason',
            'Expected Config Name', 'Actual Config Name',
            'Expected Reading Weightage', 'Actual Reading Weightage',
            'Expected Reason Path', 'Actual Reason Path'
        ]
        write_excel_object.write_headers_for_scripts(1, 0, header, write_excel_object.black_color_bold)

    def suspicious_or_not_suspicious(self, overall_proctoring_status_value):
        if overall_proctoring_status_value == 0:
            self.status = 'Not Suspicious'
        elif overall_proctoring_status_value >= 0.66:
            self.status = 'Highly Suspicious'
        elif overall_proctoring_status_value >= 0.35:
            self.status = 'Medium'
        elif overall_proctoring_status_value > 0:
            self.status = 'Low'
        else:
            self.status = 'Suspicious'

    def proctor_detail(self, row_count, current_excel_data, token):
        write_excel_object.current_status_color = write_excel_object.green_color
        write_excel_object.current_status = "Pass"

        tu_id_val = current_excel_data.get('testUserId')

        # Graceful handling if cell is empty
        if not tu_id_val:
            print(f"Row {row_count} has missing testUserId. Skipping API extraction.")
            return

        tu_id = int(tu_id_val)
        tu_payload = {"tuId": tu_id}

        tu_proctor_details = crpo_common_obj.get_tu_proc_screen_data(token, tu_payload)
        proctor_detail = tu_proctor_details['data']['getProctorDetail']
        overallReasons = proctor_detail.get('overallReasons')

        # Extract reading_detection_suspicious boolean flag
        face_details = proctor_detail.get('faceDetails')
        if not face_details or 'reading_gauge_details' not in face_details:
            reading_suspicious = 'EMPTY'
        else:
            is_reading_suspicious = face_details['reading_gauge_details'].get(
                'reading_gauge_suspicious', False)
            reading_suspicious = 'Reading suspicious' if is_reading_suspicious else 'Not suspicious'

        # Extract reasoning
        if overallReasons:
            overall_reason_text = overallReasons.get('reasonText', 'EMPTY')
            reason_data = overallReasons.get('reasonData', {})
            reason_text = reason_data.get('reasonText', 'EMPTY')
            config_name = reason_data.get('configName', 'EMPTY')
            reading_weightage = reason_data.get('weightage', 0.0)
            reason_path = reason_data.get('path', 'EMPTY')
        else:
            overall_reason_text = 'EMPTY'
            reason_text = 'EMPTY'
            config_name = 'EMPTY'
            reading_weightage = 0.0
            reason_path = 'EMPTY'

        # Write Extracted Data -> Columns
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedReadingStatus'), reading_suspicious, row_count, 5)

        video_suspicious = proctor_detail.get('faceSuspicious')
        overall_suspicious_value = proctor_detail.get('systemOverallDecision')

        self.suspicious_or_not_suspicious(overall_suspicious_value)

        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('overallProctoringStatus'), self.status, row_count, 7)

        excel_overall_suspicious_value = round(current_excel_data.get('overallSuspiciousValue'), 4)
        write_excel_object.compare_results_and_write_vertically(
            excel_overall_suspicious_value, overall_suspicious_value, row_count, 9)

        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedVideoStatus'), video_suspicious, row_count, 11)

        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('ProctoringReason'), reason_text, row_count, 13)

        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('overallProctoringReason'), overall_reason_text, row_count, 15)

        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedConfigName', 'EMPTY'), config_name, row_count, 17)

        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedReadingWeightage', 'EMPTY'), reading_weightage, row_count, 19)

        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedReasonPath', 'EMPTY'), reason_path, row_count, 21)

        # Baseline Row Writing
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('testCase'), None, row_count, 0)
        write_excel_object.compare_results_and_write_vertically(
            write_excel_object.current_status, None, row_count, 1)
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('testId'), None, row_count, 2)
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('candidateId'), None, row_count, 3)
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('testUserId'), None, row_count, 4)


if __name__ == '__main__':
    login_token = crpo_common_obj.login_to_crpo(
        cred_crpo_admin.get('user'),
        cred_crpo_admin.get('password'),
        cred_crpo_admin.get('tenant')
    )

    # Push reading detection config to automation tenant
    content = json.dumps(automation_reading_detection_proctor_eval_app_pref)
    app_pref_proc_eval_id = automation_tenant_proc_eval_id
    app_pref_proc_eval_type = automation_tenant_proc_eval_type
    update_app_preference = CrpoCommon.save_apppreferences(
        login_token, content, app_pref_proc_eval_id, app_pref_proc_eval_type)

    # Load from Sheet Index 8 (readingDetection sheet)
    excel_read_obj.excel_read(input_path_proctor_evaluation, 8)
    excel_data = excel_read_obj.details

    reading_obj = ReadingDetectionEvaluation()
    tuids = []

    for fetch_tuids in excel_data:
        tuid = fetch_tuids.get('testUserId')
        if tuid:
            tuids.append(int(tuid))

    if not tuids:
        print("Empty TestUser IDs found in the excel sheet. Please run setup_reading_detection_data.py first.")
        exit(1)

    context_id = CrpoCommon.force_evaluate_proctoring(login_token, tuids)
    print("Triggering force evaluation for tuIds:", tuids)
    context_id = context_id['data']['ContextId']
    print("Context ID:", context_id)

    current_job_status = 'Pending'

    while current_job_status != 'SUCCESS':
        job_resp = CrpoCommon.job_status(login_token, context_id)
        current_job_status = job_resp['data']['JobState']
        print("_________________ Reading Detection Evaluation is in Progress _______________________")
        print(current_job_status)
        time.sleep(20)

    row_count = 2
    for data in excel_data:
        if data.get('testUserId'):
            reading_obj.proctor_detail(row_count, data, login_token)
            row_count += 1

    write_excel_object.write_overall_status(len(tuids))
    print("Reading detection proctoring evaluation successfully completed!")
