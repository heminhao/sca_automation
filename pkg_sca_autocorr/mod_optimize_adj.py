#!/usr/bin/python_curr
# coding=utf-8

import pkg_sca_autocorr.mod_global_param as g
import pkg_sca_autocorr.mod_use_exception as e
import sqlalchemy as sy
import os
import io
import csv
import re

from sympy import symbols


def trim_bracket(t_ori_str) :
    
    tmp_str = t_ori_str.strip()
    if (tmp_str[0]!='[') or (tmp_str[-1]!=']') :
        e.g_exp.raise_exp_data('EI00007')
    return tmp_str[1:-1]

def text_to_float(t_ori_str) :
    
    if t_ori_str is None :
        return None
    if type(t_ori_str) is not str :
        e.g_exp.raise_exp_data('EI00008')
    tmp_str = t_ori_str.strip()
    if tmp_str :
        return float(tmp_str)
    else :
        return None

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
        tmp_sql = sy.sql.select([self.m_tab_meas_res_type]).where(self.m_tab_meas_res_type.c.meas_res_type_id == self.m_meas_res_type_id)
        tmp_rp = self.m_conn.execute(tmp_sql)
        tmp_row_res = tmp_rp.first()
        self.m_key_field_col_id = tmp_row_res['key_field_col_id']
        self.m_act_field_id = tmp_row_res['act_field_id']
        self.m_nom_field_id = tmp_row_res['nom_field_id']
        self.m_lowertol_field_id = tmp_row_res['lowertol_field_id']
        self.m_uppertol_field_id = tmp_row_res['uppertol_field_id']
        self.m_diff_field_id = tmp_row_res['diff_field_id']
        self.m_exceed_field_id = tmp_row_res['exceed_field_id']
        
    def find_det_id(self, t_rule_str) :
        
        tmp_str = trim_bracket(str(t_rule_str))
        for tmp_det_key in self.meas_grp_var_dict :
            if str(self.meas_grp_var_dict[tmp_det_key]['key_field_alias']).strip() == tmp_str :
                return tmp_det_key
        return 0
    
    def replace_rule_var(self, t_rule_str) :
        
        
    def del_default_rule(self, t_rule_detail_type, t_rule_str) :
        
        tmp_grp_det_id = find_det_id(self, t_rule_str)
        if tmp_grp_det_id == 0 :
            e.g_exp.raise_exp_data('EN00004')
        if t_rule_detail_type=='R' :
            self.meas_grp_var_dict[tmp_grp_det_id]['restrict_bit'] = 0
        elif t_rule_detail_type=='D' :
            self.meas_grp_var_dict[tmp_grp_det_id]['opt_bit'] = 0
        else :
            e.g_exp.raise_exp_data('EI00009')

    def add_new_rule(self, t_rule_detail_id, t_rule_detail_type, t_rule_str) :
        
        if t_rule_detail_type=='R' :
            self.restrict_add_rule_dict[t_rule_detail_id] = replace_rule_var(self, str(t_rule_str))
        elif t_rule_detail_type=='D' :
            self.opt_add_rule_dict[t_rule_detail_id] = replace_rule_var(self, str(t_rule_str))
        
    def opt_res_grp(self, t_res_grp_id) :

        tmp_sql = (sy.sql.select([self.m_tab_meas_res_grp_detail])
                   .where(self.m_tab_meas_res_grp_detail.c.res_grp_id == t_res_grp_id)
                   .order_by(self.m_tab_meas_res_grp_detail.c.res_grp_detail_id))
        tmp_bind_str = sy.sql.bindparam('d_key_str',type_=sy.String)
        tmp_bind_id = sy.sql.bindparam('d_key_id',type_=sy.String)
        tmp_alias_sql_str = (sy.sql.select([self.m_tab_meas_res_field_alias])
                             .where(sy.and_(
                                            self.m_tab_meas_res_field_alias.c.meas_res_type_id == self.m_meas_res_type_id,
                                            self.m_tab_meas_res_field_alias.c.key_field_alias == tmp_bind_str)))
        tmp_data_sql = (sy.sql.select([self.m_tab_data_file])
                        .where(sy.and_(
                                       self.m_tab_data_file.c.dump_log_id == self.m_dump_log_id,
                                       sy.sql.literal_column(self.m_key_field_col_id, sy.String) == tmp_bind_id)))
        tmp_rp = self.m_conn.execute(tmp_sql)
        self.meas_grp_var_dict = {}
        for tmp_rec in tmp_rp :
            tmp_sig_row = {}
            tmp_sig_rp = self.m_conn.execute(tmp_alias_sql, d_key_str=trim_bracket(tmp_rec.key_field_item))
            tmp_alias_row = tmp_sig_rp.first()
            if tmp_alias_row is None :
                e.g_exp.raise_exp_data('EN00002')
            tmp_data_rp = self.m_conn.execute(tmp_data_sql, d_key_id=tmp_alias_row['key_field_data'])
            tmp_data_row = tmp_data_rp.first()
            if tmp_data_row is None :
                e.g_exp.raise_exp_data('EN00003')
            tmp_sig_row['key_field_alias'] = tmp_alias_row['key_field_alias']
            tmp_sig_row['key_field_data'] = tmp_alias_row['key_field_data']
            tmp_sig_row['key_field_opt_weight'] = tmp_rec.key_field_opt_weight
            tmp_sig_row['act_field_value'] = text_to_float(tmp_data_row[self.m_act_field_id])
            tmp_sig_row['nom_field_value'] = text_to_float(tmp_data_row[self.m_nom_field_id])
            tmp_sig_row['lowertol_field_value'] = text_to_float(tmp_data_row[self.m_lowertol_field_id])
            tmp_sig_row['uppertol_field_value'] = text_to_float(tmp_data_row[self.m_uppertol_field_id])
            tmp_sig_row['diff_field_value'] = text_to_float(tmp_data_row[self.m_diff_field_id])
            tmp_sig_row['exceed_field_value'] = text_to_float(tmp_data_row[self.m_exceed_field_id])
            tmp_sig_row['symbols_act'] = symbols('x' + str(tmp_rec.res_grp_detail_id) + 'act')
            tmp_sig_row['symbols_nom'] = symbols('x' + str(tmp_rec.res_grp_detail_id) + 'nom')
            tmp_sig_row['symbols_low'] = symbols('x' + str(tmp_rec.res_grp_detail_id) + 'low')
            tmp_sig_row['symbols_upp'] = symbols('x' + str(tmp_rec.res_grp_detail_id) + 'upp')
            tmp_sig_row['symbols_dif'] = symbols('x' + str(tmp_rec.res_grp_detail_id) + 'dif')
            tmp_sig_row['symbols_exc'] = symbols('x' + str(tmp_rec.res_grp_detail_id) + 'exc')
            self.meas_grp_var_dict[tmp_rec.res_grp_detail_id] = tmp_sig_row
        
        self.restrict_rule_dict = {}
        self.opt_rule_dict = {}
        for tmp_det_key in self.meas_grp_var_dict :
            tmp_rule_str = ''
            if self.meas_grp_var_dict[tmp_det_key]['lowertol_field_value'] is not None :
                tmp_rule_str = ( '(' + self.meas_grp_var_dict[tmp_det_key]['symbols_act'].name + ' > ('
                                + self.meas_grp_var_dict[tmp_det_key]['symbols_nom'].name + ' + '
                                + self.meas_grp_var_dict[tmp_det_key]['symbols_low'].name + '))' )
            if self.meas_grp_var_dict[tmp_det_key]['uppertol_field_value'] is not None :
                if tmp_rule_str :
                    tmp_rule_str = tmp_rule_str + ' & '
                tmp_rule_str = tmp_rule_str + (
                                   '(' + self.meas_grp_var_dict[tmp_det_key]['symbols_act'].name + ' < ('
                                    + self.meas_grp_var_dict[tmp_det_key]['symbols_nom'].name + ' + '
                                    + self.meas_grp_var_dict[tmp_det_key]['symbols_upp'].name + '))' )
            if tmp_rule_str :
                self.meas_grp_var_dict[tmp_det_key]['restrict_bit'] = 1
                self.restrict_rule_dict[tmp_det_key] = tmp_rule_str
            else :
                self.meas_grp_var_dict[tmp_det_key]['restrict_bit'] = 0
                
            if self.meas_grp_var_dict[tmp_det_key]['key_field_opt_weight'] is not None :
                if ((self.meas_grp_var_dict[tmp_det_key]['lowertol_field_value'] is not None) and
                    (self.meas_grp_var_dict[tmp_det_key]['uppertol_field_value'] is not None)) :
                        tmp_rule_str = ( '(' + self.meas_grp_var_dict[tmp_det_key]['symbols_act'].name
                                        + ' - ((' + self.meas_grp_var_dict[tmp_det_key]['symbols_nom'].name
                                        + ' + ' + self.meas_grp_var_dict[tmp_det_key]['symbols_low'].name
                                        + ') + (' + self.meas_grp_var_dict[tmp_det_key]['symbols_upp'].name
                                        + ' - ' + self.meas_grp_var_dict[tmp_det_key]['symbols_low'].name
                                        + ')/2))**2' )
                else :
                    tmp_rule_str = ( '(' + self.meas_grp_var_dict[tmp_det_key]['symbols_act'].name
                                    + ' - ' + self.meas_grp_var_dict[tmp_det_key]['symbols_nom'].name
                                    + ')**2' )
                self.meas_grp_var_dict[tmp_det_key]['opt_bit'] = 1
                self.opt_rule_dict[tmp_det_key] = tmp_rule_str
            else :
                self.meas_grp_var_dict[tmp_det_key]['opt_bit'] = 0
                
        tmp_sql = (sy.sql.select([self.m_tab_meas_rule_detail])
                   .where(sy.and_(
                                  self.m_tab_meas_rule_detail.c.meas_res_type_id == self.m_meas_res_type_id,
                                  self.m_tab_meas_rule_detail.c.res_grp_id == t_res_grp_id))
                   .order_by(self.m_tab_meas_rule_detail.c.rule_detail_id))
        tmp_rp = self.m_conn.execute(tmp_sql)
        for tmp_rec in tmp_rp :
            tmp_exp_str = str(tmp_rec.except_bit).strip()
            if tmp_exp_str == 'E' :
                del_default_rule(self, str(tmp_rec.rule_detail_type).strip(), tmp_rec.rule_detail_expr_str)
            elif tmp_exp_str :
                e.g_exp.raise_exp_data('EI00009')
            else :
                add_new_rule(self, tmp_rec.rule_detail_id, str(tmp_rec.rule_detail_type).strip(), tmp_rec.rule_detail_expr_str)
        
        return self.meas_grp_var_dict
