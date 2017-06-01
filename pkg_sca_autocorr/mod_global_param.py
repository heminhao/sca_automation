#!/usr/bin/python_curr
# coding=utf-8

import sys
import os
import io
import yaml

class SCA(object) :
    pass

global_yaml_config_file = 'sca_global_config.yaml'
g_sca = None

def gen_sca_param_obj(t_dict_param) :

    if type(t_dict_param).__name__ == 'dict' :
        new_sca_obj = SCA()
        for i_name in t_dict_param :
            if type(i_name).__name__ != 'str' :
                a_name = 'S' + str(i_name)
            else :
                a_name = i_name
            setattr(new_sca_obj, a_name, gen_sca_param_obj(t_dict_param[i_name]))
    else :
        new_sca_obj = t_dict_param
    return new_sca_obj

def print_sca_param_obj(t_sca_obj, t_prefix_name) :
    
    if type(t_sca_obj).__name__ != 'SCA' :
        print(t_prefix_name + ' = ' + str(t_sca_obj))
    else :
        for i_name in t_sca_obj.__dict__ :
            print_sca_param_obj(getattr(t_sca_obj, i_name), t_prefix_name + '.' + i_name)

def read_param() :

    global g_sca
    
    # 通过__file__内建属性获得当前文件路径
    this_file_dir = os.path.split(os.path.realpath(__file__))[0]
    # 通过当前文件路径和预定义的配置文件名称获得配置文件的全路径
    cfg_file_full_name = os.path.join(this_file_dir,global_yaml_config_file)
    
    f = io.open(cfg_file_full_name, 'r', encoding='utf-8')
    doc_obj = yaml.load(f)
    g_sca = gen_sca_param_obj(doc_obj)
    f.close


if sys.version_info < (3,5,1):
    raise RuntimeError('At least Python 3.5.1 is required')
read_param()

# 该模块仅用于import引入，当单独执行时会进入如下测试模式
if __name__ == '__main__' :
    print('This module is used only for being imported.')
    print()
    print('Enter testing mode...')
    print()
    print_sca_param_obj(g_sca, 'g_sca')
    print()
