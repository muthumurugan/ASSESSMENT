from SCRIPTS.CRPO_COMMON.crpo_common import *
from SCRIPTS.CRPO_COMMON.credentials import *
from SCRIPTS.COMMON.read_excel import *
from SCRIPTS.COMMON.write_excel_new import *
from SCRIPTS.COMMON.io_path import *
from SCRIPTS.CRPO_COMMON.proc_eval_config import *
import json
import time


class GestureDetectionEvaluation:
    def __init__(self):
        write_excel_object.save_result(output_path_gesture_detection_evaluation)

        # 0th Row Header
        header = ['Gesture Detection Proctoring Evaluation']
        write_excel_object.write_headers_for_scripts(0, 0, header, write_excel_object.black_color_bold)

        # 1st Row Header
        header = [
            'Testcases', 'Status', 'Test ID', 'Candidate ID', 'Testuser ID', 'Candidate Name',
            'Expected Gesture Status', 'Actual Gesture Status',
            'Expected Overall Proctoring Status', 'Actual Overall Proctoring Status',
            'Expected Overall Rating', 'Actual Overall Rating',
            'Expected Video Proctoring Status', 'Actual Video Proctoring Status',
            'Expected Proctoring Reason', 'Actual Proctoring Reason',
            'Expected Overall Proctoring Reason', 'Actual Overall Proctoring Reason',
            'Expected Config Name', 'Actual Config Name',
            'Expected Gesture Weightage', 'Actual Gesture Weightage',
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
        write_excel_object.current_status = 'Pass'

        tu_id_val = current_excel_data.get('testUserId')

        if not tu_id_val:
            print(f'Row {row_count} has missing testUserId. Skipping API extraction.')
            return

        tu_id = int(tu_id_val)
        tu_payload = {'tuId': tu_id}

        tu_proctor_details = crpo_common_obj.get_tu_proc_screen_data(token, tu_payload)
        proctor_detail = tu_proctor_details['data']['getProctorDetail']
        overallReasons = proctor_detail.get('overallReasons')

        # Gesture detection: determined via configName in overallReasons (no dedicated faceDetails subkey)
        if overallReasons:
            overall_reason_text = overallReasons.get('reasonText', 'EMPTY')
            reason_data = overallReasons.get('reasonData', {})
            reason_text = reason_data.get('reasonText', 'EMPTY')
            config_name = reason_data.get('configName', 'EMPTY')
            gesture_weightage = reason_data.get('weightage', 0.0)
            reason_path = reason_data.get('path', 'EMPTY')
        else:
            overall_reason_text = 'EMPTY'
            reason_text = 'EMPTY'
            config_name = 'EMPTY'
            gesture_weightage = 0.0
            reason_path = 'EMPTY'

        # Derive actual gesture suspicious status from configName
        is_gesture_suspicious = config_name == 'gesture_detection'
        actual_gesture_status = 'Gesture suspicious' if is_gesture_suspicious else 'Not suspicious'

        video_suspicious = proctor_detail.get('faceSuspicious')
        overall_suspicious_value = proctor_detail.get('systemOverallDecision')
        self.suspicious_or_not_suspicious(overall_suspicious_value)

        # col 5: candidate name (no comparison needed)
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('candidateName'), None, row_count, 5)

        # col 6-7: gesture status
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedGestureStatus'), actual_gesture_status, row_count, 6)

        # col 8-9: overall proctoring status
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('overallProctoringStatus'), self.status, row_count, 8)

        # col 10-11: overall suspicious rating
        excel_overall_suspicious_value = round(current_excel_data.get('overallSuspiciousValue'), 4)
        write_excel_object.compare_results_and_write_vertically(
            excel_overall_suspicious_value, overall_suspicious_value, row_count, 10)

        # col 12-13: video suspicious
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedVideoStatus'), video_suspicious, row_count, 12)

        # col 14-15: proctoring reason
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('ProctoringReason'), reason_text, row_count, 14)

        # col 16-17: overall proctoring reason
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('overallProctoringReason'), overall_reason_text, row_count, 16)

        # col 18-19: config name
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedConfigName', 'EMPTY'), config_name, row_count, 18)

        # col 20-21: gesture weightage
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedGestureWeightage', 'EMPTY'), gesture_weightage, row_count, 20)

        # col 22-23: reason path
        write_excel_object.compare_results_and_write_vertically(
            current_excel_data.get('expectedReasonPath', 'EMPTY'), reason_path, row_count, 22)

        # Baseline row writing
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

    # Push gesture detection config to automation tenant
    content = json.dumps(automation_gesture_detection_proctor_eval_app_pref)
    app_pref_proc_eval_id = automation_tenant_proc_eval_id
    app_pref_proc_eval_type = automation_tenant_proc_eval_type
    update_app_preference = CrpoCommon.save_apppreferences(
        login_token, content, app_pref_proc_eval_id, app_pref_proc_eval_type)
    print('App preference updated.')

    # Load from Sheet Index 9 (gestureDetection sheet)
    excel_read_obj.excel_read(input_path_proctor_evaluation, 9)
    excel_data = excel_read_obj.details

    gesture_obj = GestureDetectionEvaluation()
    tuids = []

    for fetch_tuids in excel_data:
        tuid = fetch_tuids.get('testUserId')
        if tuid:
            tuids.append(int(tuid))

    print(f'Triggering force evaluation for {len(tuids)} tuIds: {tuids}')
    context_id = CrpoCommon.force_evaluate_proctoring(login_token, tuids)
    context_id = context_id['data']['ContextId']
    print('Context ID:', context_id)

    current_job_status = 'Pending'
    while current_job_status != 'SUCCESS':
        job_resp = CrpoCommon.job_status(login_token, context_id)
        current_job_status = job_resp['data']['JobState']
        print('_________________ Gesture Detection Evaluation is in Progress _______________________')
        print(current_job_status)
        time.sleep(20)

    row_count = 2
    for data in excel_data:
        if data.get('testUserId'):
            gesture_obj.proctor_detail(row_count, data, login_token)
            row_count += 1

    write_excel_object.write_overall_status(len(tuids))
    print('Gesture detection proctoring evaluation successfully completed!')
