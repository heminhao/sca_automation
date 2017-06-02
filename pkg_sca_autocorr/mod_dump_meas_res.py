#!/usr/bin/python_curr
# coding=utf-8

import pkg_sca_autocorr.mod_global_param
import pkg_sca_autocorr.mod_use_exception
import sqlalchemy as sy

class ClsDumpMeas(object) :

    def __init__(self, t_meas_res_file_grp_id) :
    
        self.m_meas_res_file_grp_id = t_meas_res_file_grp_id
