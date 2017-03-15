#!/usr/bin/python3.5.1
# coding=utf-8

import pkg_sca_autocorr.mod_global_param as gp
import sys
import os
import io
import yaml
import re

global_yaml_exp_file = 'sca_exception_def.yaml'
global_exp_code_reg_pattern = 'E.\d\d\d\d\d'

g_exp = None

class ClsExpData(object) :

    def __init__(self) :
    
        # 通过__file__内建属性获得当前文件路径
        this_file_dir = os.path.split(os.path.realpath(__file__))[0]
        # 通过当前文件路径和预定义的配置文件名称获得配置文件的全路径
        exp_file_full_name = os.path.join(this_file_dir,global_yaml_exp_file)
        
        f = io.open(exp_file_full_name, 'r', encoding='utf-8')
        doc_obj = yaml.load(f)
        f.close
        
        self.m_all_exps = {}
        self.m_exp_code_pat = re.compile(global_exp_code_reg_pattern)

        read_exp(self, doc_obj, '')

        self.m_internal_exps = doc_obj['ScaInternalExceptions']
        self.m_normal_exps = doc_obj['ScaNormalExceptions']
        
    def read_exp(self, t_exp_dict, t_prefix_name) :
        
        if type(t_exp_dict).__name__ == 'dict' :
            
            for i_name in t_exp_dict :
                if self.m_exp_code_pat.fullmatch(str(i_name)) is not None :
                    dddd
                read_exp(self, t_exp_dict[i_name], t_prefix_name + str(i_name))
    
    def raise_exp_data(self, t_exp_code) :
        
        if t_exp_code.startswith("EI") :
            exp_desc = self.m_internal_exps[t_exp_code][g.G_DEFAULT_LANG_CODE]
        elif t_exp_code.startswith("EN") :
            exp_desc = self.m_normal_exps[t_exp_code][g.G_DEFAULT_LANG_CODE]
        else :
            exp_desc = t_exp_code + "exp code head not found !"
        
        raise RuntimeError(exp_desc)

def _read_all_exps() :

    global G_CLS_EXP_DATA_OBJ
    
    G_CLS_EXP_DATA_OBJ = ClsExpData()


if sys.version_info < (3,5,1):
    raise RuntimeError('At least Python 3.5.1 is required')

_read_all_exps()


# 该模块仅用于import引入，当单独执行时会进入如下测试模式
if __name__ == '__main__' :
    print('This module is used only for being imported.')
    print()
    print('Enter testing mode...')
    print('G_CLS_EXP_DATA_OBJ = ')
    print(G_CLS_EXP_DATA_OBJ)
    print('G_CLS_EXP_DATA_OBJ.m_internal_exps = ')
    print(G_CLS_EXP_DATA_OBJ.m_internal_exps)
    print('G_CLS_EXP_DATA_OBJ.m_normal_exps = ')
    print(G_CLS_EXP_DATA_OBJ.m_normal_exps)
    