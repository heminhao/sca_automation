#!/usr/bin/python3.5.1
# coding=utf-8

import pkg_sca_autocorr.mod_global_param as g
import pkg_sca_autocorr.mod_use_exception as e
import MySQLdb
import collections
import time

class ClsDbDataComm(object) :
    
    def __init__(self, t_db_conn_mode) :
    
        #self.m_db_conn_mode = t_db_conn_mode
        self.m_db_host_ip = g.g_sca.CfgDatabaseConnection.DatabaseHost
        self.m_db_host_port = g.g_sca.CfgDatabaseConnection.DatabasePort
        self.m_db_name = g.g_sca.CfgDatabaseConnection.DatabaseName
        self.m_db_user = g.g_sca.CfgDatabaseConnection.DatabaseUser
        self.m_db_pass = g.g_sca.CfgDatabaseConnection.DatabasePass
        self.m_db_charset = g.g_sca.CfgDatabaseConnection.DatabaseCharset
        # m_db_status为对象实例的数据库连接状态
        # 0表示未连接或连接已关闭
        # 1表示已执行connect成功连接
        self.m_db_status = 0
    
    def conn_db(self) :

        if self.m_db_status!=0 :
            e.g_exp.raise_exp_data("EI00003")
        self.m_db_conn_obj = MySQLdb.connect(host=self.m_db_host_ip, port=self.m_db_host_port, db=self.m_db_name, \
            user=self.m_db_user, passwd=self.m_db_pass, charset=self.m_db_charset)
        self.m_db_status = 1

    def close_db(self) :
        
        if self.m_db_status!=1 :
            e.g_exp.raise_exp_data("EI00004")
        self.m_db_conn_obj.commit()
        self.m_db_conn_obj.close()
        del self.m_db_conn_obj
        self.m_db_status = 0

    def chk_active_conn(self) :
        
        if self.m_db_status!=1 :
            e.g_exp.raise_exp_data("EI00005")
        try:
            self.m_db_conn_obj.ping()
        except Exception as ept:
            try_cnt = 0
            succ_bit = 0
            while try_cnt<g.g_sca.SysGlobalControl.MaxDbReConnTryNums :
                time.sleep(g.g_sca.SysGlobalControl.SleepTimeDbPerReConn)
                try:
                    self.m_db_conn_obj = MySQLdb.connect(host=self.m_db_host_ip, port=self.m_db_host_port, db=self.m_db_name, \
                        user=self.m_db_user, passwd=self.m_db_pass, charset=self.m_db_charset)
                    succ_bit = 1
                    break
                except Exception as ept2:
                    pass
                try_cnt = try_cnt + 1
            if succ_bit!=1 :
                e.g_exp.raise_exp_data("EI00006")

    # t_column_def : OrderedDict
    # 参数说明：
    # t_column_def : OrderedDict类型，按序存放字段定义
    # t_drop_bit : 是否删除同名表，如果为Y则删除再建，如果为N则不允许同名，同名会报错
    def create_table(self, t_tab_name, t_column_def, t_drop_bit) :
        
        if self.m_db_status!=1 :
            e.g_exp.raise_exp_data("EI00002")
        tmp_cr_sql = "create table " + t_tab_name + " ( "
        tmp_first_bit = True
        for tmp_name,tmp_type in t_column_def.items() :
            if not tmp_first_bit :
                tmp_cr_sql = tmp_cr_sql + " , "
            else :
                tmp_first_bit = False
            tmp_cr_sql = tmp_cr_sql + tmp_name + " " + tmp_type
        tmp_cr_sql = tmp_cr_sql + " ) "

    def get_meas_res_file_grp(self, t_meas_res_file_grp_id) :
        
        self.conn_db()
        cur = self.m_db_conn_obj.cursor()
        run_sql = ("select meas_res_file_grp_desc,meas_res_type_id,file_loc_dir,filename_re_pattern,db_tab_prefix_str,"
                "scan_delay from msca_meas_res_file_grp_store t where (t.type_status='S') and (t.meas_res_file_grp_id=%s) ")
        run_param = [ t_meas_res_file_grp_id ]
        cur.execute(run_sql,run_param)
        query_res = cur.fetchone()
        ret_dict = {}
        if query_res is not None:
            ret_dict['meas_res_file_grp_desc'] = query_res[0]
            ret_dict['meas_res_type_id'] = query_res[1]
            ret_dict['file_loc_dir'] = query_res[2]
            ret_dict['filename_re_pattern'] = query_res[3]
            ret_dict['db_tab_prefix_str'] = query_res[4]
            ret_dict['scan_delay'] = query_res[5]
        else:
            e.G_CLS_EXP_DATA_OBJ.raise_exp_data("EI00001")
        self.close_db()
        return ret_dict
