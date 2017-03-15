
create database demo_autocorr default character set utf8 collate utf8_unicode_ci;
use demo_autocorr;

##################################################
#
#  ������������ӳ����Զ������ñ�ʵ����
#
##################################################
#
#  ��ʷ�޸ļ�¼��
#      V7.0 --
#              ģ�ͳ��塣
#      V8.0 --
#              1.�ı�ģ�ͳߴ��Ż����巽ʽ��
#                ����ԭ�еĳߴ���������ͼ�Ķ��巽ʽ��
#                ���ò������������delta�仯�ĺ�����
#                ����ʾ���ղ����ߴ��delta�仯��
#                �߼���Ϊ����������������ѧ�ϵ��Ż���
#              2.Ϊ������ÿɶ��Լ�������⣬���ֳߴ�
#                �����ò���ʹ��alias_id��������key_field_item��
#              3.����res_grp_code�����ֶΣ���ǿ
#                ���ÿɶ��ԣ�
#              4.���е�����desc�ֶ����䵽500�ַ���
#              5.�����˲���ע�͡�
#      V9.0 --
#              1.��Ӳ�������ļ�Ⱥ�鼰�����־ʵ�����塣
#
##################################################


##################################################
#
#  ����Ϊ���ñ���
#  ���ñ��������Ͼ���sca_��ͷ
#
##################################################

# �����豸���Ͷ������ñ�
# ˵����
#      һ�����ܻ������ڲ�������Ҫ���ֲ�ͬ�Ĳ����豸��
# �Ա��ڴӸ��ֽǶȲ������ֻ�������Ķ��ֳߴ硣��ͬ
# �����̼���ͬ�ͺŵĲ����豸�����в�ͬ����;��������
# �����ñ����ڶ���ÿһ�ֲ�ͬ����Ĳ����豸��������
CREATE TABLE `sca_measuring_device_type` (
  `mea_device_type_id` int(11) NOT NULL, #�����豸����ID
  `mea_device_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����豸��������
  `mea_manufacturer_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����豸����������
  `mea_device_model_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����豸�ͺ�����
  `eff_date` datetime DEFAULT NULL, #�豸������Чʱ��
  `eff_year` int(11) DEFAULT NULL, #�豸���ͱ�׼ʹ������
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #�豸����״̬��"S"Ϊ��Ч״̬��"W"Ϊ��Ч״̬
  PRIMARY KEY (`mea_device_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# �����豸���Ͷ������ñ�
# ˵����
#      һ�����ܻ������ڲ���Ҫ�ж��ֲ�ͬ�ļӹ��豸���ͣ�
# ��Щ�豸���Ϳ����ɲ�ͬ������������������в�ͬ���ͺš�
# ���磺�ض��ļӹ����ģ�cnc�豸�������س����������豸����
# �����ñ����ڶ���ÿһ�ֲ�ͬ����Ļ����豸��
CREATE TABLE `sca_op_device_type` (
  `op_device_type_id` int(11) NOT NULL, #�����豸����ID
  `op_device_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����豸��������
  `op_manufacturer_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����豸����������
  `op_device_model_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����豸�ͺ�����
  `eff_date` datetime DEFAULT NULL, #�豸������Чʱ��
  `eff_year` int(11) DEFAULT NULL, #�豸���ͱ�׼ʹ������
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #�豸����״̬��"S"Ϊ��Ч״̬��"W"Ϊ��Ч״̬
  PRIMARY KEY (`op_device_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ������Ͷ������ñ�
# ˵����
#      ������Ҫ�������������͵����������ÿһ�ֲ��ϡ�
# ��״���ߴ粻ͬ���������������Ϊһ��������͡�
# ��Ҫע����ǣ����������һ�ֶ��壬����ʵ�е������
# ��һ��ʵ��������ں���ʵ�����ж��塣ͬһ���������
# ���ݲ������������ܶ��Ӧ�����ʵ������Щ���ʵ����
# ������ͬ������������ϡ���״���ߴ�ȣ���
# Ϊ�˼�㲢���ǵ�ʵ��Ӧ�ã�Ŀǰû�а�������͵Ĳ��ϡ�
# ��״���ߴ������������Ӧ�ֶΣ�������δ����Ҫ��ʱ��
# �����ӡ�
# ��Ȼ������ͻ���Ҫ�ٷ��࣬���磺��������������ͣ�
# ����ת�����������͵ȵȣ����ں��������ܹ��������
# �����ơ�
CREATE TABLE `sca_component_type` (
  `component_type_id` int(11) NOT NULL, #�������ID
  `component_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����������
  `component_model_no` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL, #����ͺŴ���
  `component_cat_id` int(11) DEFAULT NULL, #������ͷ���ID�����ֶ��ݲ��ã�Ԥ��
  `eff_date` datetime DEFAULT NULL, #���������Чʱ��
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #�������״̬��"S"Ϊ��Ч״̬��"W"Ϊ��Ч״̬
  PRIMARY KEY (`component_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# �ӹ��������Ͷ������ñ�
# ˵����
#      �ӹ������ǻ��ӹ��豸Ϊ�ӹ������ʹ�õĹ������ߣ�
# ��������Ͷ�����ָ�ض��ͺš��ض������ĵ��ߵ�һЩ�ձ����ԣ�
# ������ָһ�ѵ��ľ��������
CREATE TABLE `sca_op_tool_type` (
  `tool_type_id` int(11) NOT NULL, #�ӹ���������ID
  `tool_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�ӹ�������������
  `tool_type_num` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #�ӹ����ߺ���
  `tool_type_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #�ӹ����ߴ���
  `std_tool_size` double DEFAULT NULL, #��׼���߳ߴ�
  `std_tool_precision` double DEFAULT NULL, #��׼���߼ӹ�����
  `std_tool_life` int(11) DEFAULT NULL, #��׼��������
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #��������״̬��"S"Ϊ��Ч״̬��"W"Ϊ��Ч״̬
  PRIMARY KEY (`tool_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# �ӹ�����Ⱥ�����Ͷ����
# ˵����
#      �˱����˼ӹ����ߵ�Ⱥ�顣
CREATE TABLE `sca_op_tool_grp_def` (
  `tool_grp_id` int(11) NOT NULL, #�ӹ�����Ⱥ��ID
  `tool_grp_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�ӹ�����Ⱥ������
  PRIMARY KEY (`tool_grp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# �ӹ����ߺ�Ⱥ���ϵӳ���
# ˵����
#      �˱����˼ӹ�����Ⱥ��͵������͵�ӳ���ϵ��
CREATE TABLE `sca_op_tool_grp_map` (
  `tool_grp_map_id` int(11) NOT NULL, #����Ⱥ��ӳ��ID
  `tool_grp_id` int(11) NOT NULL, #�ӹ�����Ⱥ��ID
  `tool_type_id` int(11) NOT NULL, #�ӹ���������ID
  PRIMARY KEY (`tool_grp_map_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# �������������ñ�
# ˵����
#      �����������ڲ������ض��Ĳ����豸�ϣ����ض���
# ������ͽ��м��ĳ����������������Ҳ����Ϊ
# ���ñ�����ʵ������Ҫ���ǲ����������һ����ͨ���ͣ�
# �����÷�Χ���豸���͡����������أ����;�����һ��
# �豸����һ������޹ء�
CREATE TABLE `sca_meas_prg_def` (
  `meas_prg_id` int(11) NOT NULL, #��������ID
  `meas_prg_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #������������
  `meas_prg_name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #������������
  `mea_device_type_id` int(11) DEFAULT NULL, #���õĲ����豸����ID
  `component_type_id` int(11) DEFAULT NULL, #���õ��������ID
  `eff_date` datetime DEFAULT NULL, #������Чʱ��
  `prg_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #����״̬��"S"Ϊ��Ч״̬��"W"Ϊ��Ч״̬
  PRIMARY KEY (`meas_prg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ���ӳ��������ñ�
# ˵����
#      ���ӳ������ڲ������ض��Ļ����豸�ϣ����ض���
# ������ͽ��мӹ��ĳ�����������ӳ���Ҳ����Ϊ
# ���ñ�����ʵ������Ҫ���ǻ��ӳ������һ����ͨ���ͣ�
# �����÷�Χ�ͻ����豸���͡����������أ����;�����һ��
# �豸����һ������޹ء�
CREATE TABLE `sca_op_prg_def` (
  `op_prg_id` int(11) NOT NULL, #���ӳ���ID
  `op_prg_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #���ӳ�������
  `op_prg_name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #���ӳ�������
  `op_device_type_id` int(11) DEFAULT NULL, #���õĻ����豸����ID
  `component_type_id` int(11) DEFAULT NULL, #���õ��������ID
  `eff_date` datetime DEFAULT NULL, #������Чʱ��
  `prg_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #����״̬��"S"Ϊ��Ч״̬��"W"Ϊ��Ч״̬
  PRIMARY KEY (`op_prg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ����������Ͷ������ñ�
# ˵����
#      ��ͬ�Ĳ�����������һ�㶼���ض��Ľ����ʽ��
# �˱����˲�������ĸ�ʽID���������Զ����ӳ������
# ��Ҫ�õ��Ĺؼ��ֶ�ID��
CREATE TABLE `sca_meas_res_type_def` (
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `meas_res_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #���������������
  `meas_res_format_id` int(11) DEFAULT NULL, #���������ʽID��Ŀǰ����1��������tab�ָ��Ĵ������е��ļ�
  `meas_prg_id` int(11) DEFAULT NULL, #��������ID
  `key_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #������Ŀ�ֶ�ID
  `lowertol_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #�¹����ֶ�ID
  `uppertol_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #�Ϲ����ֶ�ID
  `diff_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #�����ֶ�ID
  `exceed_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #�����ֶ�ID
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #�����������״̬��"S"Ϊ��Ч״̬��"W"Ϊ��Ч״̬
  PRIMARY KEY (`meas_res_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ������Ŀ�����������ñ�
# ˵����
#      �ñ�Բ�ͬ�Ĳ����������ID�������˸�������Ŀ��
# ԭʼ����������Ż�����Ķ�Ӧ��ϵ����Ż������Ҫ����
# �򻯺��������е����á�
CREATE TABLE `sca_meas_res_key_field_alias` (
  `alias_id` int(11) NOT NULL, #����ID
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `key_field_data` varchar(500) COLLATE utf8_unicode_ci NOT NULL, #������Ŀ����
  `key_field_id` int(11) NOT NULL, #������Ŀ��ţ���ͬһ������������Ͷ��ԣ�������Ŀ��Ŵ�1��ʼ����
  `key_field_alias` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL, #������Ŀ���������������ں����������
  PRIMARY KEY (`alias_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ����������͹���Ⱥ�����ñ�
# ˵����
#      �����������һ���Ƕ�ĳһ���ض�����Ķ෽��ߴ�Ĳ�����
# ��ĳ�������˵����һ���������������Ŀ��ͬ�����ݡ�
# �˱��ض�����Ķ෽��ĳߴ綨���һ��Ⱥ�飬���ں����Ż���
CREATE TABLE `sca_meas_res_grp_def` (
  `res_grp_id` int(11) NOT NULL, #Ⱥ��ID
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #Ⱥ����룬��ͬһ��meas_res_type_id��Ӧ��Ψһ
  `res_grp_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #Ⱥ������
  PRIMARY KEY (`res_grp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ����������͹���Ⱥ����ϸ���ñ�
# ˵����
#      �����������һ���Ƕ�ĳһ���ض�����Ķ෽��ߴ�Ĳ�����
# ��ĳ�������˵����һ���������������Ŀ��ͬ�����ݡ�
# �˱���key_field_item�������Բ�����Ŀ���ݷ����Ⱥ����ϸ�����ں����Ż���
CREATE TABLE `sca_meas_res_grp_detail_def` (
  `res_grp_detail_id` int(11) NOT NULL, #Ⱥ����ϸ����ID
  `res_grp_id` int(11) NOT NULL, #Ⱥ��ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #Ⱥ����룬����һ�������ֶΣ�������ǿ���ÿɶ���
  # ���²�����Ŀ��ʶ����[key_field_id]����[key_field_alias]����ʽ���Ա������ú����
  `key_field_item` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #������Ŀ��ʶ
  # �����ֶ��ǲ�����Ŀ�Ż�Ŀ��Ȩ�أ��ⶨ�����Ż�ʱ�ؼ��ߴ��Ȩ�أ�
  # �Ż�Ŀ�꺯��Ϊ��w1*abs(�ߴ�1����)+w2*abs(�ߴ�2����)+...
  # �����Ż�Ŀ��Ϊ�����Ż�Ŀ�꺯��ȡ����Сֵ��
  # ���Ϊ����óߴ���Ĭ�Ϲ����в���Ϊ�Ż�Ŀ�ꣻ
  # ����óߴ�����¹���û��ȫ�����壬��óߴ�Ҳ����ΪĬ���Ż�Ŀ�꣬�����ֶ���Ч��
  `key_field_opt_weight` int(11) DEFAULT NULL, #������Ŀ�Ż�Ŀ��Ȩ��
  PRIMARY KEY (`res_grp_detail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ��������������ݹ���ԭ��ֵ�����
CREATE TABLE `sca_meas_data_atom_def` (
  `atom_def_id` int(11) NOT NULL, #ԭ��ֵ����ID
  `atom_def_code` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #ԭ��ֵ�������
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `res_grp_id` int(11) NOT NULL, #Ⱥ��ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #Ⱥ����룬����һ�������ֶΣ�������ǿ���ÿɶ���
  # ԭ�ӷ���ֵ������ʽ����ʹ�������е�ƫ��ͳ�������ݼ��㷵��ֵ
  # ���ʽ��������Ⱥ���ڲ�����Ŀ����ID���������ϳɸ�����ѧ���ʽ��
  # ���õĸ�ʽ���£�
  # [key_field_id].datatype��[key_field_alias].datatype
  # ���е�datatype��ȡ����ֵ֮һ��
  # DIFF,EXCEED,ACT,NOM,UPPER,LOWER,MIDDLE
  # DIFF����ƫ�����ݣ�EXCEED���������ݣ�
  # ACT����ʵ�����ݣ�NOM�����������ݣ�
  # UPPER�����Ϲ��LOWER�����¹��MIDDLE�������¹�����м�ֵ
  # ���磺abs([1].ACT-[1].NOM)���������Ŀ����IDΪ1��ʵ�����ݼ�ȥ�������ݵ�ֵ�ľ�������
  `atom_expr_str` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL, #ԭ�ӷ���ֵ������ʽ
  PRIMARY KEY (`atom_def_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ������������Զ������ӳ�������������ϸ�����
# ˵����
#      �˱������ض�Ⱥ��ID�ķ�Ĭ���Ż�����
#      ��Ҫע����ǣ����µ�Ĭ�Ϲ����ǲ���Ҫ����ģ�
#
#      Ĭ�����ƹ�����ͬһȺ�������еĳߴ綼Ҫ�������¹���Ҫ��
#          ������ļ���û�����¹���ĳ��⣬�����Ϲ��������¹���Ҳ��Ҫ���㣩
#      Ĭ��Ŀ�������ͬһȺ�������еĳߴ�������ֵ��Ҫ����key_field_opt_weight�����Ȩ���ۼӣ�
#          �ߴ������ָʵ�ʳߴ�����¹�����м�ֵ�Ĳ��죬
#          �Ż�Ŀ��Ϊ���ϼ�Ȩֵ��С����
#         �����key_field_opt_weightΪ�յĳ��⣬��������Ϲ��������¹���Ҳ���⣩
#      Ĭ��Ԥ�������ǿգ��������δ������Ԥ��
#      ����Ĭ�Ϲ����ǲ���Ҫ�ڴ˹�����ж���ģ�Ĭ�϶�����Ч�ģ��������Ƕ�����
#          ����Ĭ�Ϲ���
CREATE TABLE `sca_meas_data_corr_rule_detail_def` (
  `rule_detail_id` int(11) NOT NULL, #������ϸID
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `res_grp_id` int(11) NOT NULL, #Ⱥ��ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #Ⱥ����룬����һ�������ֶΣ�������ǿ���ÿɶ���
  # ֧�����¹�����ϸ����
  # R�����ƹ��򣬱�ʾ��Ҫ�������������
  # D��Ŀ����򣬱�ʾ����������Ŀ��
  # A��Ԥ�����򣬱�ʾ����ʱ����ƫ�����о����ˣ�������Ҫ���֣��ܹ��Զ��澯
  `rule_detail_type` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #������ϸ����
  `except_bit` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL, #��������־��������ֶ�ΪE�������˹���Ϊ����Ĭ�Ϲ���
  # ����rule_detail_type��except_bit�Ĳ�ͬ��ϣ�����Ĺ�����ϸ������ʽ���в�ͬ����ʽ�ͺ��壺
  # ���裨rule_detail_type,except_bit��Ϊ����ֵ��
  # ��R��E�������ʽ����ʽΪ[key_field_id]��[key_field_alias]����ʾ�ض��Ĳ�����Ŀ����Ĭ�����ƹ���ִ��
  # ��D��E�������ʽ����ʽΪ[key_field_id]��[key_field_alias]����ʾ�ض��Ĳ�����Ŀ����Ĭ��Ŀ�����ִ��
  # ��A��E�����������������������
  # ��R���գ������ʽ����ʽΪ��[key_field_id].datatype��[key_field_alias].datatype��[atom_def_code]��ɵ��������ʽ
  #            ���磺abs([key_field_alias].ACT-[key_field_alias].MIDDLE)<2
  # ��D���գ������ʽ����ʽΪ��[key_field_id].datatype��[key_field_alias].datatype��[atom_def_code]��ɵ��������ʽ��
  #            �Ż�Ŀ��Ϊ���������ʽ�ﵽ��Сֵ��
  #            ���磺abs([key_field_alias].ACT-[key_field_alias].MIDDLE)��
  #                  ����Ϊʵ��ֵ�����¹����м�ֵ�Ĳ�ľ���ֵҪ�ﵽ��Сֵ������Ĭ��Ŀ���������ͬ��
  # ��A���գ������ʽ����ʽΪ��[key_field_id].datatype��[key_field_alias].datatype��[atom_def_code]��ɵ��������ʽ
  #            ���磺abs([key_field_alias1].ACT-[key_field_alias2].ACT)<2
  #                  ����Ϊ�����ߴ��ʵ��ֵ֮���಻�ܹ��󣬷����Ҫ�澯
  `rule_detail_expr_str` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL, #������ϸ������ʽ
  # ���¹����Ż�Ŀ��Ȩ���ֶν���Ŀ���������D��Ч����ʾ�ù��������յ��Ż�Ŀ����ʽ�е�Ȩ��ϵ��
  `rule_opt_weight` int(11) DEFAULT NULL, #�����Ż�Ŀ��Ȩ��
  PRIMARY KEY (`rule_detail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ���ӳ�����豸״̬�Ż����������
# ˵����
#      �˱�������Ϊ����ߴ���Ż���������res_grp_id�У�
# ��������������ʱ��ȡ�ĵ����������������ӳ���ĵ�����
# ����ϵ�ĵ����ȵȡ�
CREATE TABLE `sca_grp_op_adj_def` (
  `op_adj_id` int(11) NOT NULL, #��������ID
  `op_code_id` int(11) DEFAULT NULL, #����������ţ��������������ߴ�Ͳ�����ϵ���ʽʱ���ã���һ���Ż�Ⱥ��res_grp_id�ڣ�ӦΨһ
  `op_code_str` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #���������ִ���ͬ����Ҫ�����ã���Ⱥ��res_grp_id��ӦΨһ
  `op_code_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #������������
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `res_grp_id` int(11) NOT NULL, #Ⱥ��ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #Ⱥ����룬����һ�������ֶΣ�������ǿ���ÿɶ���
  # ���²�����ϸ���Ͷ����˵�����ʩ���������£�
  # P�����ӳ��������op_prg_id��op_prg_pos_tag��Ч
  # C������ϵ������coordinates_id��Ч
  `op_detail_type` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #������ϸ����
  `op_prg_id` int(11) DEFAULT NULL, #���ӳ���ID
  `op_prg_pos_tag` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL, #���ӳ���λ�ñ�ʶ����Ҫ�޸ĵ�����λ�ڸñ�ʶ����һ�У�
  `coordinates_id` int(11) DEFAULT NULL, #����ϵID
  `dest_axis_direction` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL, #�ߴ���������᷽��������X��Y��Z��
  `tool_grp_id` int(11) DEFAULT NULL, #�ӹ�����Ⱥ��ID�������������ID��Ӧ�ĸ��൶�ߵļ��ϣ������ּӹ��������ӹ�����
  PRIMARY KEY (`op_adj_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ����������ͳߴ�䶯���Ż�������ֵ��ϵ�����
# ˵����
#      �˱����˲�����������йؼ������ߴ���Ż�������ֵ֮��������ϵ��
# ��ĳһ���ӹ���������ʱ���ܿ�����صĶ���ߴ綼���ܵ�Ӱ�졣
CREATE TABLE `sca_meas_res_value_delta_def` (
  `meas_delta_def_id` int(11) NOT NULL, #�ߴ�䶯����ID
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `res_grp_id` int(11) NOT NULL, #Ⱥ��ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #Ⱥ����룬����һ�������ֶΣ�������ǿ���ÿɶ���
  # ���²��������Ŀ��ʶ����D[key_field_id]����D[key_field_alias]����ʽ���Ա������ú����
  `delta_key_field_item` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #���������Ŀ��ʶ
  # ���±��ʽ�������ض��ߴ�ͼӹ���������֮��Ĺ�ϵ��һ��������µ���ʽ��
  # ��D[op_code_id]��D[op_code_str]��ɵ���ѧ���ʽ������ӹ������������µĳߴ�仯��
  `delta_rely_op_str` varchar(1000) COLLATE utf8_unicode_ci NOT NULL, #����仯�ļ�����ʽ
  PRIMARY KEY (`meas_delta_def_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ��������ϵ�����
CREATE TABLE `sca_op_coordinates_def` (
  `coordinates_id` int(11) NOT NULL, #����ϵID
  `coordinates_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #����ϵ����
  PRIMARY KEY (`coordinates_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


##################################################
#
#  ����Ϊʵ������
#  ʵ�����������Ͼ���msca_��ͷ
#
##################################################

# ��������ļ�Ⱥ����λ��ʵ����
# ˵����
#      �˱������ض��Ĳ�������ļ����ļ�ϵͳ�еĴ��λ�ã�
# �Լ�ϵͳ����Զ���ȡ��������ʽ����Ϣ��һ��ģ�
# �������ͬһ���ļ�ϵͳĿ¼�е�ͬһ�ֲ�������ļ�����Ϊ
# һ����������ļ�Ⱥ�飬�Ҷ�Ӧ��Ψһ��meas_res_type_id��
CREATE TABLE `msca_meas_res_file_grp_store` (
  `meas_res_file_grp_id` int(11) NOT NULL, #��������ļ�Ⱥ��ID
  `meas_res_file_grp_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #��������ļ�Ⱥ������
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `file_loc_dir` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #�����ļ���ŵ�Ŀ¼
  `filename_re_pattern` varchar(500) COLLATE utf8_unicode_ci NOT NULL, #Ѱ�Ҵ����ļ���������ʽ
  `db_tab_prefix_str` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #��Ⱥ���ļ��������ݿ�����ַ�����ʵ�ʱ���Ϊ��"m" + meas_res_file_grp_id + "_" + db_tab_prefix_str
  `scan_delay` int(11) NOT NULL, #��ȡɨ���������룩
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #Ⱥ������״̬��"S"Ϊ��Ч״̬��"W"Ϊ�ر�״̬
  PRIMARY KEY (`meas_res_file_grp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# ��������ļ������־��
# ˵����
#      �˱��¼�������Ĳ�������ļ���־��
# ϵͳ�����Զ�ɨ���ļ�ϵͳĿ¼���Է���Ҫ����ļ�������⴦��
# ����Ҫ�жϸ��ļ��Ƿ�������������⣨֧�ֲ��д�������ʵ��ʱ
# ��Ҫ�������ݿ������ԭ���ԣ���
CREATE TABLE `msca_meas_res_file_dump_log` (
  `dump_log_id` int(11) NOT NULL, #��־��¼ID
  `meas_res_file_grp_id` int(11) NOT NULL, #��������ļ�Ⱥ��ID
  `meas_res_type_id` int(11) NOT NULL, #�����������ID
  `full_file_name` varchar(1000) COLLATE utf8_unicode_ci NOT NULL, #��������·�����ļ�����
  `full_db_tab_name` varchar(1000) COLLATE utf8_unicode_ci NOT NULL, #���������ݿ�洢����
  `eff_date` datetime NOT NULL, #���ļ���������ں�ʱ��
  `dump_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #����״̬��"S"Ϊ�ɹ���"E"Ϊʧ��
  `dump_err_msg` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL, #���������Ϣ���ڵ���ʧ��ʱ��д
  `column_cnt` int(11) DEFAULT NULL, #�����ļ��м���
  `row_cnt` int(11) DEFAULT NULL, #�����ļ��м���
  PRIMARY KEY (`dump_log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
