#!/usr/bin/python3.5.1
# coding=utf-8

import pkg_sca_autocorr.mod_global_param as gp
import sys
import os
import io
import yaml
import re

global_yaml_exp_file_prefix = 'sca_exception_def'
global_exp_code_reg_pattern = 'E.\d\d\d\d\d'

g_exp = None

class ClsExpData(object) :
    
    def __init__(self) :
    
        # 通过__file__内建属性获得当前文件路径
        this_file_dir = os.path.split(os.path.realpath(__file__))[0]
        # 通过全局参数获得语言信息，生成异常配置文件名
        lang_code = gp.g_sca.DefaultLangCode
        exp_file_abbr = eval("gp.g_sca.LanguageCodeDef.S" + str(lang_code) + ".Abbr")
        global_yaml_exp_file = global_yaml_exp_file_prefix + "_" + exp_file_abbr + ".yaml"
        # 通过当前文件路径和预定义的配置文件名称获得配置文件的全路径
        exp_file_full_name = os.path.join(this_file_dir,global_yaml_exp_file)
        
        f = io.open(exp_file_full_name, 'r', encoding='utf-8')
        doc_obj = yaml.load(f)
        f.close
        
        self.m_all_exps = {}
        self.m_exp_code_pat = re.compile(global_exp_code_reg_pattern)

        self.read_exp(doc_obj, '')

    def read_exp(self, t_exp_dict, t_prefix_name) :
        
        if type(t_exp_dict).__name__ == 'dict' :
            
            for i_name in t_exp_dict :
                if self.m_exp_code_pat.fullmatch(str(i_name)) is not None :
                    exp_data = t_prefix_name + ' : ' + self.read_exp_all_info(t_exp_dict[i_name])
                    self.m_all_exps[i_name] = exp_data
                else :
                    if t_prefix_name=='' :
                        pre_dot_str = ''
                    else :
                        pre_dot_str = '.'
                    self.read_exp(t_exp_dict[i_name], t_prefix_name + pre_dot_str + str(i_name))

    def read_exp_all_info(self, t_exp_dict) :
        
        if type(t_exp_dict).__name__ == 'dict' :
            ret_str = '{'
            for i_name in t_exp_dict :
                ret_str = ret_str + ' /' + str(i_name) + ' : ' + read_exp_all_info(self,t_exp_dict[i_name]) + '/ '
            ret_str = ret_str + '}'
        else :
            ret_str = str(t_exp_dict)
        return ret_str

    def raise_exp_data(self, t_exp_code) :
        
        exp_desc = t_exp_code + ' : ' + self.m_all_exps[t_exp_code]
        raise RuntimeError(exp_desc)

def read_all_exps() :

    global g_exp
    
    g_exp = ClsExpData()
    
def print_all_exps(t_exp_obj) :
    
    for i_name in t_exp_obj.m_all_exps :
        print(i_name + ' : ' + t_exp_obj.m_all_exps[i_name])


if sys.version_info < (3,5,1):
    raise RuntimeError('At least Python 3.5.1 is required')

read_all_exps()


# 该模块仅用于import引入，当单独执行时会进入如下测试模式
if __name__ == '__main__' :
    print('This module is used only for being imported.')
    print()
    print('Enter testing mode...')
    print_all_exps(g_exp)
