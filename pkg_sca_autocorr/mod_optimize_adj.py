#!/usr/bin/python_curr
# coding=utf-8

import pkg_sca_autocorr.mod_global_param as g
import pkg_sca_autocorr.mod_use_exception as e
import sqlalchemy as sy
import collections as cl
import os
import io
import csv
import re

import numpy
import scipy.optimize as sciopt
from sympy.utilities import lambdify
from sympy.utilities.iterables import flatten
from sympy import symbols
from sympy.core.sympify import kernS


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

    def find_op_adj_id(self, t_rule_str) :
        
        tmp_str = trim_bracket(str(t_rule_str))
        for tmp_adj_key in self.op_adj_dict :
            if str(self.op_adj_dict[tmp_adj_key]['op_code_str']).strip() == tmp_str :
                return tmp_adj_key
        return 0
    
    def replace_rule_var(self, t_rule_str) :
        
        curr_rule_str = str(t_rule_str)
        datatype_list = ('DIFF', 'EXCEED', 'ACT', 'NOM', 'UPPER', 'LOWER')
        rep_str_list = ('symbols_dif', 'symbols_exc', 'symbols_act', 'symbols_nom', 'symbols_upp', 'symbols_low')
        for i,tmp_dt in enumerate(datatype_list) :
            var_pattern = r'\[[a-zA-Z0-9_]*\]\.' + tmp_dt
            all_vars = re.findall(var_pattern, curr_rule_str)
            for tmp_var in all_vars :
                tmp_sig = str(tmp_var).rstrip('.' + tmp_dt)
                tmp_det_id = self.find_det_id(tmp_sig)
                if tmp_det_id == 0 :
                    e.g_exp.raise_exp_data('EN00005')
                curr_rule_str.replace(tmp_var, self.meas_grp_var_dict[tmp_det_id][rep_str_list[i]].name, 1)
        return curr_rule_str
        
    def del_default_rule(self, t_rule_detail_type, t_rule_str) :
        
        tmp_grp_det_id = self.find_det_id(t_rule_str)
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
            self.restrict_add_rule_dict[t_rule_detail_id] = self.replace_rule_var(str(t_rule_str))
        elif t_rule_detail_type=='D' :
            self.opt_add_rule_dict[t_rule_detail_id] = self.replace_rule_var(str(t_rule_str))

    def add_pre_var(self, t_delta_str) :
        
        tmp_delta_str = str(t_delta_str)
        for tmp_op_adj_key in self.op_adj_dict :
            tmp_var_name = str(self.op_adj_dict[tmp_op_adj_key]['symbols_adj'].name)
            if tmp_delta_str.find(tmp_var_name)>=0 :
                tmp_exist_bit = 0
                for tmp_id in self.pre_var :
                    if str(self.pre_var[tmp_id].name) == tmp_var_name :
                        tmp_exist_bit = 1
                        break
                if tmp_exist_bit == 0 :
                    self.pre_var[self.pre_var_num] = self.op_adj_dict[tmp_op_adj_key]['symbols_adj']
                    self.pre_var_num = self.pre_var_num + 1

    def add_rule_con_var(self, t_rule_str) :
        
        tmp_rule_str = str(t_rule_str)
        all_con_vars = re.findall(r'(x)([0-9]*)(act|nom|low|upp|dif|exc)', tmp_rule_str)
        val_name_dict = {}
        val_name_dict['act'] = 'act_field_value'
        val_name_dict['nom'] = 'nom_field_value'
        val_name_dict['low'] = 'lowertol_field_value'
        val_name_dict['upp'] = 'uppertol_field_value'
        val_name_dict['dif'] = 'diff_field_value'
        val_name_dict['exc'] = 'exceed_field_value'
        for tmp_con_var in all_con_vars :
            tmp_var = tmp_con_var[0] + tmp_con_var[1] + tmp_con_var[2]
            tmp_det_id = int(tmp_con_var[1])
            tmp_sym_name = 'symbols_' + tmp_con_var[2]
            tmp_sym_val = val_name_dict[tmp_con_var[2]]
            tmp_exist_bit = 0
            for tmp_id in self.pre_con_var :
                if str(self.pre_con_var[tmp_id]['sym_obj'].name) == tmp_var :
                    tmp_exist_bit = 1
                    break
            if tmp_exist_bit == 0 :
                tmp_sig_data = {}
                tmp_sig_data['sym_obj'] = self.meas_grp_var_dict[t_det_key][tmp_sym_name]
                tmp_sig_data['sym_val'] = self.meas_grp_var_dict[t_det_key][tmp_sym_val]
                self.pre_con_var[self.pre_con_var_num] = tmp_sig_data
                self.pre_con_var_num + self.pre_con_var_num + 1

    def scan_default_con(self, t_det_key, t_rule_expr) :
        
        tmp_rule_expr = str(t_rule_expr)
        tmp_delta_str = str(self.meas_grp_var_dict[t_det_key]['delta_op_adj_expr'])
        self.add_pre_var(tmp_delta_str)
        new_act_var = '(' + self.meas_grp_var_dict[t_det_key]['symbols_act'].name + ' + (' + tmp_delta_str + '))'
        tmp_rule_expr.replace(self.meas_grp_var_dict[t_det_key]['symbols_act'].name, new_act_var, 1)
        tmp_sig_data = {}
        tmp_sig_data['sym_obj'] = self.meas_grp_var_dict[t_det_key]['symbols_act']
        tmp_sig_data['sym_val'] = self.meas_grp_var_dict[t_det_key]['act_field_value']
        self.pre_con_var[self.pre_con_var_num] = tmp_sig_data
        self.pre_con_var_num = self.pre_con_var_num + 1
        if tmp_rule_expr.find(self.meas_grp_var_dict[t_det_key]['symbols_low'].name)>=0 :
            tmp_sig_data = {}
            tmp_sig_data['sym_obj'] = self.meas_grp_var_dict[t_det_key]['symbols_low']
            tmp_sig_data['sym_val'] = self.meas_grp_var_dict[t_det_key]['lowertol_field_value']
            self.pre_con_var[self.pre_con_var_num] = tmp_sig_data
            self.pre_con_var_num = self.pre_con_var_num + 1
        if tmp_rule_expr.find(self.meas_grp_var_dict[t_det_key]['symbols_upp'].name)>=0 :
            tmp_sig_data = {}
            tmp_sig_data['sym_obj'] = self.meas_grp_var_dict[t_det_key]['symbols_upp']
            tmp_sig_data['sym_val'] = self.meas_grp_var_dict[t_det_key]['uppertol_field_value']
            self.pre_con_var[self.pre_con_var_num] = tmp_sig_data
            self.pre_con_var_num = self.pre_con_var_num + 1
        return tmp_rule_expr

    def scan_default_opt(self, t_det_key, t_rule_expr) :
        
        tmp_rule_str = str(t_rule_expr)
        tmp_delta_str = str(self.meas_grp_var_dict[t_det_key]['delta_op_adj_expr'])
        self.add_pre_var(tmp_delta_str)
        new_act_var = '(' + self.meas_grp_var_dict[t_det_key]['symbols_act'].name + ' + (' + tmp_delta_str + '))'
        tmp_rule_str.replace(self.meas_grp_var_dict[t_det_key]['symbols_act'].name, new_act_var, 1)
        self.add_rule_con_var(tmp_rule_str)
        return '(' + str(self.meas_grp_var_dict[t_det_key]['key_field_opt_weight']) + '*(' + tmp_rule_str + '))'

    def scan_custom_rule(self, t_rule_expr) :
        
        curr_rule_str = str(t_rule_expr)
        tmp_rule_str = ''
        tmp_ma_obj = re.search(r'(x)([0-9]*)(act)', curr_rule_str)
        while tmp_ma_obj is not None :
            beg_pos = tmp_ma_obj.span()[0]
            end_pos = tmp_ma_obj.span()[1]
            tmp_det_id = int(tmp_ma_obj.group(2))
            if self.meas_grp_var_dict[tmp_det_id].has_key('delta_op_adj_expr') :
                tmp_new_act = ( '(' + self.meas_grp_var_dict[tmp_det_id]['symbols_act'].name
                               + ' + (' + self.meas_grp_var_dict[tmp_det_id]['delta_op_adj_expr'] + '))' )
            else :
                tmp_new_act = tmp_ma_obj.group(0)
            tmp_rule_str = tmp_rule_str + curr_rule_str[0:beg_pos] + tmp_new_act
            curr_rule_str = curr_rule_str[end_pos:]
            tmp_ma_obj = re.search(r'(x)([0-9]*)(act)', curr_rule_str)
        tmp_rule_str = tmp_rule_str + curr_rule_str
        self.add_rule_con_var(tmp_rule_str)
        self.add_pre_var(tmp_rule_str)
        return '(' + tmp_rule_str + ')'

    def opt_res_grp(self, t_res_grp_id) :

        tmp_sql = (sy.sql.select([self.m_tab_meas_res_grp_detail])
                   .where(self.m_tab_meas_res_grp_detail.c.res_grp_id == t_res_grp_id)
                   .order_by(self.m_tab_meas_res_grp_detail.c.res_grp_detail_id))
        tmp_bind_str = sy.sql.bindparam('d_key_str',type_=sy.String)
        tmp_bind_id = sy.sql.bindparam('d_key_id',type_=sy.String)
        tmp_alias_sql = (sy.sql.select([self.m_tab_meas_res_field_alias])
                             .where(sy.and_(
                                            self.m_tab_meas_res_field_alias.c.meas_res_type_id == self.m_meas_res_type_id,
                                            self.m_tab_meas_res_field_alias.c.key_field_alias == tmp_bind_str)))
        tmp_data_sql = (sy.sql.select([self.m_tab_data_file])
                        .where(sy.and_(
                                       self.m_tab_data_file.c.dump_log_id == self.m_dump_log_id,
                                       sy.sql.literal_column(self.m_key_field_col_id, sy.String) == tmp_bind_id)))
        tmp_rp = self.m_conn.execute(tmp_sql)
        self.meas_grp_var_dict = cl.OrderedDict()
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
            tmp_rule_dict = {}
            self.meas_grp_var_dict[tmp_det_key]['restrict_bit'] = 0
            if self.meas_grp_var_dict[tmp_det_key]['lowertol_field_value'] is not None :
                self.meas_grp_var_dict[tmp_det_key]['restrict_bit'] = 1
                tmp_rule_dict[0] = ( '(' + self.meas_grp_var_dict[tmp_det_key]['symbols_act'].name + ' - ('
                                   + self.meas_grp_var_dict[tmp_det_key]['symbols_nom'].name + ' + '
                                   + self.meas_grp_var_dict[tmp_det_key]['symbols_low'].name + '))' )
            if self.meas_grp_var_dict[tmp_det_key]['uppertol_field_value'] is not None :
                self.meas_grp_var_dict[tmp_det_key]['restrict_bit'] = 1
                tmp_rule_dict[1] = ( '((' + self.meas_grp_var_dict[tmp_det_key]['symbols_nom'].name + ' + '
                                   + self.meas_grp_var_dict[tmp_det_key]['symbols_upp'].name + ') - '
                                   + self.meas_grp_var_dict[tmp_det_key]['symbols_act'].name + ')' )
            if self.meas_grp_var_dict[tmp_det_key]['restrict_bit'] == 1 :
                self.restrict_rule_dict[tmp_det_key] = tmp_rule_dict

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
        self.restrict_add_rule_dict = cl.OrderedDict()
        self.opt_add_rule_dict = cl.OrderedDict()
        for tmp_rec in tmp_rp :
            tmp_exp_str = str(tmp_rec.except_bit).strip()
            if tmp_exp_str == 'E' :
                self.del_default_rule(str(tmp_rec.rule_detail_type).strip(), tmp_rec.rule_detail_expr_str)
            elif tmp_exp_str != 'None' :
                e.g_exp.raise_exp_data('EI00009')
            else :
                self.add_new_rule(tmp_rec.rule_detail_id, str(tmp_rec.rule_detail_type).strip(), tmp_rec.rule_detail_expr_str)
                
        tmp_sql = (sy.sql.select([self.m_tab_meas_grp_op])
                   .where(sy.and_(
                                  self.m_tab_meas_grp_op.c.meas_res_type_id == self.m_meas_res_type_id,
                                  self.m_tab_meas_grp_op.c.res_grp_id == t_res_grp_id))
                   .order_by(self.m_tab_meas_grp_op.c.op_adj_id))
        tmp_rp = self.m_conn.execute(tmp_sql)
        self.op_adj_dict = cl.OrderedDict()
        for tmp_rec in tmp_rp :
            tmp_sig_row['op_adj_id'] = tmp_rec.op_adj_id
            tmp_sig_row['op_code_str'] = tmp_rec.op_code_str
            tmp_sig_row['op_detail_type'] = tmp_rec.op_detail_type
            tmp_sig_row['op_prg_id'] = tmp_rec.op_prg_id
            tmp_sig_row['op_prg_pos_tag'] = tmp_rec.op_prg_pos_tag
            tmp_sig_row['coordinates_id'] = tmp_rec.coordinates_id
            tmp_sig_row['dest_axis_direction'] = tmp_rec.dest_axis_direction
            tmp_sig_row['symbols_adj'] = symbols('op' + str(tmp_rec.op_adj_id) + 'adj')
            self.op_adj_dict[tmp_rec.op_adj_id] = tmp_sig_row
            
        tmp_sql = (sy.sql.select([self.m_tab_meas_delta_val])
                   .where(sy.and_(
                                  self.m_tab_meas_delta_val.c.meas_res_type_id == self.m_meas_res_type_id,
                                  self.m_tab_meas_delta_val.c.res_grp_id == t_res_grp_id))
                   .order_by(self.m_tab_meas_delta_val.c.meas_delta_def_id))
        tmp_rp = self.m_conn.execute(tmp_sql)
        for tmp_rec in tmp_rp :
            tmp_delta_str = str(tmp_rec.delta_key_field_item)
            tmp_det_id = self.find_det_id(re.sub(r'(D)(\[[a-zA-Z0-9_]*\])',r'\2',tmp_delta_str))
            tmp_delta_expr = str(tmp_rec.delta_rely_op_str)
            all_op_vars = re.findall(r'(D)(\[[a-zA-Z0-9_]*\])', tmp_delta_expr)
            for tmp_op_var in all_op_vars :
                tmp_op_adj_id = self.find_op_adj_id(tmp_op_var[1])
                tmp_delta_expr.replace(tmp_op_var[0]+tmp_op_var[1], self.op_adj_dict[tmp_op_adj_id]['symbols_adj'].name, 1)
            self.meas_grp_var_dict[tmp_det_id]['delta_op_adj_expr'] = tmp_delta_expr
        
        # 优化约束条件字典
        self.pre_res_con = cl.OrderedDict()
        self.pre_res_con_num = 0
        # 优化变量字典
        self.pre_var = cl.OrderedDict()
        self.pre_var_num = 0
        # 优化常量（即测量文件中已有数值的）字典
        self.pre_con_var = cl.OrderedDict()
        self.pre_con_var_num = 0
        # 优化目标字符串表达式
        self.total_opt_str = ''
        for tmp_det_key in self.meas_grp_var_dict :
            if self.meas_grp_var_dict[t_det_key].has_key('delta_op_adj_expr') :
                if self.meas_grp_var_dict[tmp_det_key]['restrict_bit'] == 1 :
                    if self.restrict_rule_dict[tmp_det_key].has_key(0) :
                        self.pre_res_con[self.pre_res_con_num] = self.scan_default_con(tmp_det_key, self.restrict_rule_dict[tmp_det_key][0])
                        self.pre_res_con_num = self.pre_res_con_num + 1
                    if self.restrict_rule_dict[tmp_det_key].has_key(1) :
                        self.pre_res_con[self.pre_res_con_num] = self.scan_default_con(tmp_det_key, self.restrict_rule_dict[tmp_det_key][1])
                        self.pre_res_con_num = self.pre_res_con_num + 1
                if self.meas_grp_var_dict[tmp_det_key]['opt_bit'] == 1 :
                    if not(self.total_opt_str) :
                        self.total_opt_str = self.total_opt_str + ' + '
                    self.total_opt_str = self.total_opt_str + self.scan_default_opt(tmp_det_key, self.opt_rule_dict[tmp_det_key])
        for tmp_rule_detail_id in self.restrict_add_rule_dict :
            self.pre_res_con[self.pre_res_con_num] = self.scan_custom_rule(self.restrict_add_rule_dict[tmp_rule_detail_id])
            self.pre_res_con_num = self.pre_res_con_num + 1
        for tmp_rule_detail_id in self.opt_add_rule_dict :
            if not(self.total_opt_str) :
                self.total_opt_str = self.total_opt_str + ' + '
            self.total_opt_str = self.total_opt_str + self.scan_custom_rule(self.opt_add_rule_dict[tmp_rule_detail_id])

        self.vars_list = []
        for i in range(0,self.pre_var_num) :
            self.vars_list.append(self.pre_var[i])
        for i in range(0,self.pre_con_var_num) :
            self.vars_list.append(self.pre_con_var[i]['sym_obj'])
        self.total_opt_expr = kernS(self.total_opt_str)
        self.func_opt_expr = lambdify(flatten(self.vars_list), self.total_opt_expr, 'numpy')
        self.func_con_list = []
        for i in range(0,self.pre_res_con_num) :
            tmp_expr = kernS(self.pre_res_con[i])
            tmp_func = lambdify(flatten(self.vars_list), tmp_expr, 'numpy')
            self.func_con_list.append(tmp_func)

        opt_cons = []
        for i in range(0,self.pre_res_con_num) :
            tmp_dyn_func_str = '''
def tmp_g(X) :
    RX = X
    for j in range(0,self.pre_con_var_num) :
        RX.append(self.pre_con_var[j]['sym_val'])
    return self.func_con_list[''' + str(i) +'](*flatten(RX))\n'
            exec(tmp_dyn_func_str)
            exec('tmp_sig_con = dict(type=\'ineq\', fun=tmp_g)')
            exec('opt_cons.append(tmp_sig_con)')
            
        def tmp_f(X) :
            RX = X
            for j in range(0,self.pre_con_var_num) :
                RX.append(self.pre_con_var[j]['sym_val'])
            return self.func_opt_expr(*flatten(RX))

        init_val = []
        for i in range(0,self.pre_var_num) :
            init_val.append(0)
        self.opt_res = sciopt.minimize(tmp_f, init_val, method='SLSQP', constraints=opt_cons)

        return 0
