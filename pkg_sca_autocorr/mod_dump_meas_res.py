#!/usr/bin/python_curr
# coding=utf-8

import pkg_sca_autocorr.mod_global_param as g
import pkg_sca_autocorr.mod_use_exception as e
import sqlalchemy as sy
import io
import csv
import re

class ClsDumpMeas(object) :

    def __init__(self, t_meas_res_file_grp_id) :
    
        self.m_meas_res_file_grp_id = t_meas_res_file_grp_id
        self.m_engine_str = 'mysql+pymysql://%s:%s@%s/%s?charset=%s' % \
                (g.g_sca.CfgDatabaseConnection.DatabaseUser,g.g_sca.CfgDatabaseConnection.DatabasePass, \
                g.g_sca.CfgDatabaseConnection.DatabaseHost,g.g_sca.CfgDatabaseConnection.DatabaseName \
                g.g_sca.CfgDatabaseConnection.DatabaseCharset)
        self.m_engine = sy.create_engine(self.m_engine_str)
        self.m_conn = self.m_engine.connect()
        self.m_meta = sy.MetaData()
        self.m_seq_dump_log = sy.Sequence('seq_dump_log_id', metadata=self.m_meta)
        self.m_tab_meas_res_grp = sy.Table('msca_meas_res_file_grp_store', self.m_meta, autoload=True, autoload_with=self.m_engine)
        tmp_sql = sy.sql.select([self.m_tab_meas_res_grp]).where(self.m_tab_meas_res_grp.c.meas_res_file_grp_id == self.m_meas_res_file_grp_id)
        tmp_rp = self.m_conn.execute(tmp_sql)
        self.m_row_meas_res_grp = tmp_rp.fetchone()
        self.m_tab_meas_res_type = sy.Table('sca_meas_res_type_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        tmp_sql = sy.sql.select([self.m_tab_meas_res_type]).where(self.m_tab_meas_res_type.c.meas_res_type_id == self.m_row_meas_res_grp['meas_res_type_id'])
        tmp_rp = self.m_conn.execute(tmp_sql)
        self.m_row_meas_res_type = tmp_rp.fetchone()
        self.m_tab_meas_dump_log = sy.Table('msca_meas_res_file_dump_log', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_monitor_dir = self.m_row_meas_res_grp['file_loc_dir']
        self.m_monitor_file_re = re.compile(self.m_row_meas_res_grp['filename_re_pattern'])
        self.m_db_tab_name = 'm%d_%s' % (self.m_meas_res_file_grp_id,self.m_row_meas_res_grp['db_tab_prefix_str'])
        self.m_res_format_id = self.m_row_meas_res_type['meas_res_format_id']

    def save_file_todb_csvtab(self, t_file_name) :
        
        f = io.open(t_file_name, 'r', encoding='gbk')
        readerdata = csv.DictReader(f, dialect='excel-tab')
        max_len = readerdata.fieldnames.__len__() - 2
        cr_tab_str = 'sy.Table(\'%s\', self.m_meta, ' % self.m_db_tab_name
        cr_tab_str = cr_tab_str + 'Column(\'dump_log_id\',sy.Integer(),index=True), Column(\'line_num\',sy.BigInteger()), '
        for i in range(max_len-1) :
            cr_tab_str = cr_tab_str + 'Column(\'%s\',sy.Text()), ' % readerdata.fieldnames[i]
        cr_tab_str = cr_tab_str + ' Column(\'%s\',sy.Text()) )' % readerdata.fieldnames[max_len]
        dyn_tab_obj = eval(cr_tab_str)
        self.m_meta.create_all(self.m_engine)
        v_dump_log_id = self.m_seq_dump_log.next_value()
        ins_stat = dyn_tab_obj.insert()
        for rec in readerdata :
            ins_data = rec
            ins_data['dump_log_id'] = v_dump_log_id
            ins_data['line_num'] = readerdata.line_num
            self.m_conn.execute(ins_stat, ins_data)
        ins_log_stat = self.m_tab_meas_dump_log.insert()
        ins_log_data = {}
        ins_log_data['dump_log_id'] = v_dump_log_id
        ins_log_data['meas_res_file_grp_id'] = self.m_meas_res_file_grp_id
        ins_log_data['meas_res_type_id'] = self.m_row_meas_res_grp['meas_res_type_id']
        ins_log_data['full_file_name'] = t_file_name
        ins_log_data['full_db_tab_name'] = self.m_db_tab_name
        self.m_conn.execute(ins_log_stat, ins_log_data)
        
    def save_file_todb_others(self, t_file_name) :
        
        e.g_exp.raise_exp_data('EN00001')
        
    def run_dump(self) :
        
        all_files = os.listdir(path = self.m_monitor_dir)
        # 以tab分隔的带标题行的csv文件格式
        if self.m_res_format_id == 1 :
            save_func_name = 'save_file_todb_csvtab'
        # 以逗号分隔的带标题行的csv文件格式（暂未实现）
        elif self.m_res_format_id == 2 :
            save_func_name = 'save_file_todb_csvcom'
        # 其它文件格式（报出异常）
        else
            save_func_name = 'save_file_todb_others'
        for eachfile in all_files :
            chk_str = self.m_monitor_file_re.match(eachfile)
            if chk_str is not None :
                eval(save_func_name)(self, self.m_monitor_dir + eachfile)
