from SCRIPTS.COMMON.dbconnection import *
import datetime


class ResetTestUser:

    def __init__(self):
        print(datetime.datetime.now())

    @staticmethod
    def reset_test_users():
        # resetting test users to there previous state
        db_connection = ams_db_connection()
        cursor = db_connection.cursor()
        print("---------------------Started Resetting Test users-----------------------------")

        # CASE 1 : Vendor INITIATE_AUTOMATION
        # Test level is_password_never_expire flag should not be enabled
        update_tuser1 = "update test_users set login_time = DATE_SUB(NOW(),INTERVAL 60 MINUTE), log_out_time = " \
                        "DATE_SUB(NOW(),INTERVAL 55 MINUTE), total_score = NULL, percentage = NULL, " \
                        "automation_info = NULL, automation_task_id = NULL where id in (3748161,3748443) and " \
                        "candidate_id in(1554121,1554229) and test_id = 18671;"
        print(update_tuser1)
        cursor.execute(update_tuser1)
        db_connection.commit()

        update_test_users_partner_info1 = "update test_users_partner_info set score_status = NULL,task_id_score_fetch" \
                                          " = NULL, report_link = NULL, third_party_status = NULL, " \
                                          "third_party_overall_status = NULL where testuser_id in(3748161,3748443);"
        print(update_test_users_partner_info1)
        cursor.execute(update_test_users_partner_info1)
        db_connection.commit()

        update_applicant_status1 = "update applicant_statuss set current_status_id = 167301, comments = NULL where" \
                                   " id in(1334979,1334791) and candidate_id in(1554121,1554229) and tenant_id= 1787;"
        print(update_applicant_status1)
        cursor.execute(update_applicant_status1)
        db_connection.commit()

        # CASE 2 : Vendor SCORE_FETCH_RE_INITIATE_AUTOMATION
        # Test level is_password_never_expire flag should not be enabled
        update_tuser2 = """update test_users set login_time = DATE_SUB(NOW(),INTERVAL 60 MINUTE), log_out_time = 
        DATE_SUB(NOW(),INTERVAL 55 MINUTE), total_score = NULL, percentage = NULL, automation_info = '{"timestamp": 
        "24-07-01 17:03:47", "adHocPrams": null, "apiResponse": {"isSuccess": true, "nextTestInfos": null, 
        "nextTestLinks": null, "isAutoShortlisting": false}}' where id in (3748163,3748445) and candidate_id in (
        1554123,1554231) and test_id = 18671; """
        print(update_tuser2)
        cursor.execute(update_tuser2)
        db_connection.commit()

        update_test_users_partner_info2 = "update test_users_partner_info set score_status = 3, report_link = NULL," \
                                          " third_party_status = NULL, third_party_overall_status = NULL where" \
                                          " testuser_id in (3748163,3748445);"
        print(update_test_users_partner_info2)
        cursor.execute(update_test_users_partner_info2)
        db_connection.commit()

        update_applicant_status2 = "update applicant_statuss set current_status_id = 167301 where id " \
                                   "in (1334793,1334981) and candidate_id in (1554123,1554231) and tenant_id= 1787;"
        print(update_applicant_status2)
        cursor.execute(update_applicant_status2)
        db_connection.commit()

        # CASE 3 : Vendor SCORE_FETCH_INITIATE_AUTOMATION
        # Test level is_password_never_expire flag should not be enabled
        update_tuser3 = "update test_users set total_score = NULL, percentage = NULL, log_out_time = NULL, status = 4," \
                        " automation_info = NULL, json_config = NULL where id in (3747819,3748447) and " \
                        "candidate_id in (1554125,1554233) and test_id = 18671;"
        print(update_tuser3)
        cursor.execute(update_tuser3)
        db_connection.commit()

        update_test_users_partner_info3 = "update test_users_partner_info set score_status = NULL, " \
                                          "task_id_score_fetch = NULL, report_link = NULL, third_party_status = NULL," \
                                          " third_party_overall_status  = NULL where testuser_id in (3747819,3748447);"
        print(update_test_users_partner_info3)
        cursor.execute(update_test_users_partner_info3)
        db_connection.commit()

        update_applicant_status3 = "update applicant_statuss set current_status_id = 167301, comments = NULL where" \
                                   " id in (1334671,1334983) and candidate_id in (1554125,1554233) and tenant_id= 1787;"
        print(update_applicant_status3)
        cursor.execute(update_applicant_status3)
        db_connection.commit()

        # CASE 4 (PASSWORD_EXPIRED_TO_PASSWORD_DISABLED) Attending_to_Password_Disabled
        # Test level is_password_never_expire flag should not be enabled
        update_tuser4 = "update test_users set status = 4, is_password_disabled = 0 where id = 3741833 and test_id = " \
                        "19299 and candidate_id = 1552023; "
        print(update_tuser4)
        cursor.execute(update_tuser4)
        db_connection.commit()

        # CASE 5 (SUBMIT_PASSWORD_NEVER_EXPIRED) Attending_to_Attended
        # Test level is_password_never_expire flag should be enabled
        update_tuser5 = "update test_users set status = 4, log_out_time = NULL where id = 3741855 and test_id = 19313 " \
                        "and candidate_id = 1552025; "
        print(update_tuser5)
        cursor.execute(update_tuser5)
        db_connection.commit()

        # CASE 6 (SUBMIT_PASSWORD_DISABLED) Password_Disabled_to_Attended
        # Test level is_password_never_expire flag should not be enabled
        update_tuser6 = "update test_users set status = 5, is_password_disabled = 1, log_out_time = NULL where id = " \
                        "3741837 and test_id = 19299 and candidate_id = 1552027; "
        print(update_tuser6)
        cursor.execute(update_tuser6)
        db_connection.commit()

        # CASE 7 (ATTENDED_INITIATE_AUTOMATION) Attended_to_Attended_With_Inititate_Automation
        update_tuser7 = "update test_users set  login_time = DATE_SUB(NOW(),INTERVAL 60 MINUTE), log_out_time = " \
                        "DATE_SUB(NOW(),INTERVAL 55 MINUTE), total_score = NULL, percentage = NULL," \
                        "correct_answers = NULL, in_correct_answers = NULL, un_attended_questions=NULL, " \
                        "is_partially_evaluated = NULL, eval_status = NULL, eval_by = NULL, eval_on = NULL, " \
                        "json_config = NULL, automation_task_id = NULL, automation_info = NULL, evaluation_info = " \
                        "NULL where id in (3741839,3748455) and candidate_id in(1552029,1554241) and test_id = 19299"
        print(update_tuser7)
        cursor.execute(update_tuser7)
        db_connection.commit()

        update_applicant_status7 = "update applicant_statuss set current_status_id = 167301, comments = NULL where id " \
                                   "in(1330487,1334991) and candidate_id in(1552029,1554241) and tenant_id= 1787; "
        print(update_applicant_status7)
        cursor.execute(update_applicant_status7)
        db_connection.commit()

        # CASE 8 (SUBMIT_NOT_ATTENDED_INITIATE_AUTOMATION) Not_Attended_with_logintime_to_Attended_With_Inititate_Automation

        update_tuser8 = "update test_users set  login_time = DATE_SUB(NOW(),INTERVAL 60 MINUTE), log_out_time = " \
                        "NULL, total_score = NULL, percentage = NULL, status = 0, time_spent = 65," \
                        "correct_answers = NULL, in_correct_answers = NULL, un_attended_questions=NULL, " \
                        "is_partially_evaluated = NULL, eval_status = NULL, eval_by = NULL, eval_on = NULL, " \
                        "json_config = NULL, automation_task_id = NULL, automation_info = NULL, evaluation_info = " \
                        "NULL where id in (3842673, 3842675) and candidate_id in (1586789, 1586791) and test_id = 19299"
        print(update_tuser8)
        cursor.execute(update_tuser8)
        db_connection.commit()

        update_applicant_status8 = "update applicant_statuss set current_status_id = 167301, comments = NULL where id " \
                                   "in (1411531,1411533) and candidate_id in (1586789, 1586791) and tenant_id= 1787; "
        print(update_applicant_status8)
        cursor.execute(update_applicant_status8)
        db_connection.commit()

        # CASE 4.1 (BOT_PASSWORD_EXPIRED_TO_PASSWORD_DISABLED) Attending_to_Password_Disabled
        # Test level is_password_never_expire flag should not be enabled
        update_tuser4_1 = "update test_users set status = 4, is_password_disabled = 0 where id = 3859381 and test_id = " \
                        "27805 and candidate_id = 1597137; "
        print(update_tuser4_1)
        cursor.execute(update_tuser4_1)
        db_connection.commit()

        # CASE 5.1 (BOT_SUBMIT_PASSWORD_NEVER_EXPIRED) Attending_to_Attended
        # Test level is_password_never_expire flag should be enabled
        update_tuser5_1 = "update test_users set status = 4, log_out_time = NULL where id = 3859465 and test_id = 21713 " \
                        "and candidate_id = 1597143; "
        print(update_tuser5_1)
        cursor.execute(update_tuser5_1)
        db_connection.commit()

        # CASE 6.1 (BOT_SUBMIT_PASSWORD_DISABLED) Password_Disabled_to_Attended
        # Test level is_password_never_expire flag should not be enabled
        update_tuser6_1 = "update test_users set status = 5, is_password_disabled = 1, log_out_time = NULL where id = " \
                        "3859389 and test_id = 27805 and candidate_id = 1597139; "
        print(update_tuser6_1)
        cursor.execute(update_tuser6_1)
        db_connection.commit()

        # CASE 7.1 (BOT_NON_VENDOR_INITIATE_AUTOMATION) Attended_to_Attended_With_Inititate_Automation
        update_tuser7_1 = "update test_users set  login_time = DATE_SUB(NOW(),INTERVAL 60 MINUTE), log_out_time = " \
                        "DATE_SUB(NOW(),INTERVAL 55 MINUTE), total_score = NULL, percentage = NULL," \
                        "correct_answers = NULL, in_correct_answers = NULL, un_attended_questions=NULL, " \
                        "is_partially_evaluated = NULL, eval_status = NULL, eval_by = NULL, eval_on = NULL, " \
                        "json_config = NULL, automation_task_id = NULL, automation_info = NULL, evaluation_info = " \
                        "NULL where id in (3859513) and candidate_id in(1597153) and test_id = 27805"
        print(update_tuser7_1)
        cursor.execute(update_tuser7_1)
        db_connection.commit()

        update_applicant_status7_1 = "update applicant_statuss set current_status_id = 167301, comments = NULL where id " \
                                   "in(1426731) and candidate_id in(1597153) and tenant_id= 1787; "
        print(update_applicant_status7_1)
        cursor.execute(update_applicant_status7_1)
        db_connection.commit()

        # CASE 8.1 (BOT_SUBMIT_NOT_ATTENDED_INITIATE_AUTOMATION) Not_Attended_with_logintime_to_Attended_With_Inititate_Automation

        update_tuser8_1 = "update test_users set  login_time = DATE_SUB(NOW(),INTERVAL 60 MINUTE), log_out_time = " \
                        "NULL, total_score = NULL, percentage = NULL, status = 0, time_spent = 65," \
                        "correct_answers = NULL, in_correct_answers = NULL, un_attended_questions=NULL, " \
                        "is_partially_evaluated = NULL, eval_status = NULL, eval_by = NULL, eval_on = NULL, " \
                        "json_config = NULL, automation_task_id = NULL, automation_info = NULL, evaluation_info = " \
                        "NULL where id in (3859393) and candidate_id in (1597145) and test_id = 27805"
        print(update_tuser8_1)
        cursor.execute(update_tuser8_1)
        db_connection.commit()

        update_applicant_status8_1 = "update applicant_statuss set current_status_id = 167301, comments = NULL where id " \
                                   "in (1426639) and candidate_id in (1597145) and tenant_id= 1787; "
        print(update_applicant_status8_1)
        cursor.execute(update_applicant_status8_1)
        db_connection.commit()

        db_connection.close()

        print("---------------------Resetting Test user Done Successfully-----------------------------")


reset_test_user_obj = ResetTestUser()
# print(datetime.datetime.now())
reset_test_user_obj.reset_test_users()