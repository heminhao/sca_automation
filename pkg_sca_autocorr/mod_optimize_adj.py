#!/usr/bin/python_curr
# coding=utf-8

import pkg_sca_autocorr.mod_global_param as g
import pkg_sca_autocorr.mod_use_exception as e
import sqlalchemy as sy
import os
import io
import csv
import re

def trim_bracket(t_ori_str) :
    
    tmp_str = t_ori_str.strip()
    if (tmp_str[0]!='[') or (tmp_str[-1]!=']') :
        e.g_exp.raise_exp_data('EI00007')
    return tmp_str[1:-1]

class ClsOptAdj(object) :

    def __init__(self, t_dump_log_id) :
    
        self.m_dump_log_id = t_dump_log_id
        self.m_engine_str = ('mysql+pymysql://%s:%s@%s/%s?charset=%s' %
                (g.g_sca.CfgDatabaseConnection.DatabaseUser,g.g_sca.CfgDatabaseConnection.DatabasePass,
                g.g_sca.CfgDatabaseConnection.DatabaseHost,g.g_sca.CfgDatabaseConnection.DatabaseName,
                g.g_sca.CfgDatabaseConnection.DatabaseCharset))
        self.m_engine = sy.create_engine(self.m_engine_str)
        self.m_conn = self.m_engine.connect()
        self.m_meta = sy.MetaData()
        self.m_tab_meas_dump_log = sy.Table('msca_meas_res_file_dump_log', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_res_type = sy.Table('sca_meas_res_type_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_res_field_alias = sy.Table('sca_meas_res_key_field_alias', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_res_grp = sy.Table('sca_meas_res_grp_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_res_grp_detail = sy.Table('sca_meas_res_grp_detail_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_data_atom = sy.Table('sca_meas_data_atom_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_rule_detail = sy.Table('sca_meas_data_corr_rule_detail_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_grp_op = sy.Table('sca_grp_op_adj_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        self.m_tab_meas_delta_val = sy.Table('sca_meas_res_value_delta_def', self.m_meta, autoload=True, autoload_with=self.m_engine)
        
        tmp_sql = sy.sql.select([self.m_tab_meas_dump_log]).where(self.m_tab_meas_dump_log.c.dump_log_id == self.m_dump_log_id)
        tmp_rp = self.m_conn.execute(tmp_sql)
        tmp_row_res = tmp_rp.first()
        self.m_meas_res_type_id = tmp_row_res['meas_res_type_id']
        self.m_tab_data_file = sy.Table(tmp_row_res['full_db_tab_name'], self.m_meta, autoload=True, autoload_with=self.m_engine)

    def opt_res_grp(self, t_res_grp_id) :

        tmp_sql = (sy.sql.select([self.m_tab_meas_res_grp_detail])
                   .where(self.m_tab_meas_res_grp_detail.c.res_grp_id == t_res_grp_id)
                   .order_by(self.m_tab_meas_res_grp_detail.c.res_grp_detail_id))
        tmp_bind_param = sy.sql.bindparam('d_key_str',type_=sy.types.String)
        tmp_alias_sql = (sy.sql.select([self.m_tab_meas_res_field_alias])
                        .where(sy.and_(
                                       self.m_tab_meas_res_field_alias.c.meas_res_type_id == self.m_meas_res_type_id,
                                       sy.or_(
                                              self.m_tab_meas_res_field_alias.c.key_field_data == tmp_bind_param,
                                              self.m_tab_meas_res_field_alias.c.key_field_alias == tmp_bind_param)))
                        )
        tmp_rp = self.m_conn.execute(tmp_sql)
        meas_grp_var_dict = {}
        for tmp_rec in tmp_rp :
            tmp_sig_row = {}
            tmp_sig_rp = self.m_conn.execute(tmp_alias_sql, d_key_str=trim_bracket(tmp_rec.key_field_item))
            tmp_alias_row = tmp_sig_rp.first()
            tmp_sig_row['key_field_alias'] = tmp_alias_row['key_field_alias']
            tmp_sig_row['key_field_data'] = tmp_alias_row['key_field_data']
            tmp_sig_row['key_field_opt_weight'] = tmp_rec.key_field_opt_weight
            meas_grp_var_dict[tmp_rec.res_grp_detail_id] = tmp_sig_row
        return meas_grp_var_dict
