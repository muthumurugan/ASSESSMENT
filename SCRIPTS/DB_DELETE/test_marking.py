from SCRIPTS.COMMON.dbconnection import *
import datetime


class DeleteTestMarking:

    def __init__(self):
        print(datetime.datetime.now())

    def delete_assessment_test_users(self):
        db_connection = ams_db_connection()
        cursor = db_connection.cursor()
        tuser_result_infos = "delete from test_result_infos where testresult_id in " \
                             "(SELECT tr.id from test_results tr inner join test_users tu on tu.id=tr.testuser_id " \
                             "where tu.test_id in(16241,16243,16249,16267,16265,16345) and tu.status=1);"
        cursor.execute(tuser_result_infos)
        db_connection.commit()

        tuser_results = "delete from test_results where testuser_id in (2550033,2550035,2550037,2549815,2549813,2549819,2549817,2549879,2549877,2549875,2549873,2550047,2550045,2552033,2552031);"
        cursor.execute(tuser_results)
        db_connection.commit()
        tuser_scores = "delete from candidate_scores where testuser_id in(select tu.id from test_users tu " \
                       "inner join tests t on t.id = tu.test_id where test_id in(16241,16243,16249,16267,16265,16345) and login_time " \
                       "is not null and t.tenant_id in (1787));"
        cursor.execute(tuser_scores)
        db_connection.commit()
        tuser_login_infos = "delete from test_user_login_infos where testuser_id in " \
                            "(select tu.id from test_users tu inner join tests t on t.id = tu.test_id " \
                            "where test_id in(16241,16243,16249,16267,16265,16345) and login_time is not null and t.tenant_id in (1787));"
        print(tuser_login_infos)
        cursor.execute(tuser_login_infos)
        db_connection.commit()

        tuser_proctoring_infos = "delete from test_user_proctor_details where testuser_id in " \
                                 "(select tu.id from test_users tu inner join tests t on " \
                                 "t.id = tu.test_id where test_id in(16241,16243,16249,16267,16265,16345) and login_time is not null " \
                                 "and t.tenant_id in (1787));"
        print(tuser_proctoring_infos)
        cursor.execute(tuser_proctoring_infos)
        db_connection.commit()

        update_tuser_statuss = "update test_users set login_time = NULL, log_out_time = NULL, status = 0, " \
                               "client_system_info = NULL, time_spent = NULL, is_password_disabled = 0," \
                               "config = NULL,client_system_info = NULL, total_score = NULL, percentage = NULL, " \
                               "test_start_time = NULL where test_id in(16241,16243,16249,16267,16265,16345) and login_time is not null;"
        print(update_tuser_statuss)
        cursor.execute(update_tuser_statuss)
        db_connection.commit()
        db_connection.close()


del_data = DeleteTestMarking()
del_data.delete_assessment_test_users()
print(datetime.datetime.now())
