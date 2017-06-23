
create database demo_autocorr default character set utf8 collate utf8_unicode_ci;
use demo_autocorr;

##################################################
#
#  零件测量及机加程序自动化配置表及实例表
#
##################################################
#
#  历史修改记录：
#      V7.0 --
#              模型初稿。
#      V8.0 --
#              1.改变模型尺寸优化定义方式，
#                舍弃原有的尺寸依赖有向图的定义方式，
#                改用操作调整步骤的delta变化的函数，
#                来表示最终测量尺寸的delta变化，
#                逻辑更为清晰合理，更利于数学上的优化；
#              2.为提高配置可读性及便于理解，部分尺寸
#                的引用不再使用alias_id，而改用key_field_item；
#              3.增加res_grp_code冗余字段，增强
#                配置可读性；
#              4.所有的描述desc字段扩充到500字符；
#              5.完善了部分注释。
#      V9.0 --
#              1.添加测量结果文件群组及入库日志实例表定义。
#      V10.0 --
#              1.添加sequence控制表；
#              2.添加生成seq的函数。
#
##################################################


##################################################
#
#  以下为配置表定义
#  配置表在命名上均以sca_开头
#
##################################################

# 测量设备类型定义配置表
# 说明：
#      一个智能化工厂内部可能需要各种不同的测量设备，
# 以便于从各种角度测量各种机加零件的多种尺寸。不同
# 制造商及不同型号的测量设备往往有不同的用途和特征。
# 此配置表用于定义每一种不同种类的测量设备的特征。
CREATE TABLE `sca_measuring_device_type` (
  `mea_device_type_id` int(11) NOT NULL, #测量设备类型ID
  `mea_device_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #测量设备类型描述
  `mea_manufacturer_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #测量设备制造商描述
  `mea_device_model_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #测量设备型号描述
  `eff_date` datetime DEFAULT NULL, #设备类型生效时间
  `eff_year` int(11) DEFAULT NULL, #设备类型标准使用年限
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #设备类型状态："S"为有效状态，"W"为无效状态
  PRIMARY KEY (`mea_device_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 机加设备类型定义配置表
# 说明：
#      一个智能化工厂内部需要有多种不同的加工设备类型，
# 这些设备类型可能由不同的制造商生产，或具有不同的型号。
# 例如：特定的加工中心（cnc设备）、数控车床或其它设备类型
# 此配置表用于定义每一种不同种类的机加设备。
CREATE TABLE `sca_op_device_type` (
  `op_device_type_id` int(11) NOT NULL, #机加设备类型ID
  `op_device_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #机加设备类型描述
  `op_manufacturer_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #机加设备制造商描述
  `op_device_model_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #机加设备型号描述
  `eff_date` datetime DEFAULT NULL, #设备类型生效时间
  `eff_year` int(11) DEFAULT NULL, #设备类型标准使用年限
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #设备类型状态："S"为有效状态，"W"为无效状态
  PRIMARY KEY (`op_device_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 零件类型定义配置表
# 说明：
#      工厂需要生产出各种类型的零件，对于每一种材料、
# 形状、尺寸不同的零件特征，定义为一个零件类型。
# 需要注意的是，零件类型是一种定义，而现实中的零件则
# 是一个实例，这会在后续实例表中定义。同一个零件类型
# 根据产量会生产出很多对应的零件实例，这些零件实例都
# 具有相同的特征（如材料、形状、尺寸等）。
# 为了简便并考虑到实际应用，目前没有把零件类型的材料、
# 形状、尺寸等特性纳入相应字段，可以再未来需要的时候
# 再增加。
# 当然零件类型还需要再分类，比如：发动机的零件类型，
# 还是转向轴的零件类型等等，这在后续的智能工厂设计中
# 逐步完善。
CREATE TABLE `sca_component_type` (
  `component_type_id` int(11) NOT NULL, #零件类型ID
  `component_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #零件类型描述
  `component_model_no` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL, #零件型号代码
  `component_cat_id` int(11) DEFAULT NULL, #零件类型分类ID，此字段暂不用，预留
  `eff_date` datetime DEFAULT NULL, #零件类型生效时间
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #零件类型状态："S"为有效状态，"W"为无效状态
  PRIMARY KEY (`component_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 加工刀具类型定义配置表
# 说明：
#      加工刀具是机加工设备为加工零件而使用的工作刀具，
# 这里的类型定义是指特定型号、特定参数的刀具的一些普遍特性，
# 而不是指一把刀的具体情况。
CREATE TABLE `sca_op_tool_type` (
  `tool_type_id` int(11) NOT NULL, #加工刀具类型ID
  `tool_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #加工刀具类型描述
  `tool_type_num` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #加工刀具号码
  `tool_type_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #加工刀具代码
  `std_tool_size` double DEFAULT NULL, #标准刀具尺寸
  `std_tool_precision` double DEFAULT NULL, #标准刀具加工精度
  `std_tool_life` int(11) DEFAULT NULL, #标准刀具寿命
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #刀具类型状态："S"为有效状态，"W"为无效状态
  PRIMARY KEY (`tool_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 加工刀具群组类型定义表
# 说明：
#      此表定义了加工刀具的群组。
CREATE TABLE `sca_op_tool_grp_def` (
  `tool_grp_id` int(11) NOT NULL, #加工刀具群组ID
  `tool_grp_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #加工刀具群组描述
  PRIMARY KEY (`tool_grp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 加工刀具和群组关系映射表
# 说明：
#      此表定义了加工刀具群组和刀具类型的映射关系。
CREATE TABLE `sca_op_tool_grp_map` (
  `tool_grp_map_id` int(11) NOT NULL, #刀具群组映射ID
  `tool_grp_id` int(11) NOT NULL, #加工刀具群组ID
  `tool_type_id` int(11) NOT NULL, #加工刀具类型ID
  PRIMARY KEY (`tool_grp_map_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量程序定义配置表
# 说明：
#      测量程序用于部署在特定的测量设备上，对特定的
# 零件类型进行检测的程序。这里，将测量程序也定义为
# 配置表，而非实例表，主要考虑测量程序具有一定的通用型，
# 其适用范围和设备类型、零件类型相关，但和具体哪一个
# 设备、哪一个零件无关。
CREATE TABLE `sca_meas_prg_def` (
  `meas_prg_id` int(11) NOT NULL, #测量程序ID
  `meas_prg_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #测量程序描述
  `meas_prg_name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #测量程序名称
  `mea_device_type_id` int(11) DEFAULT NULL, #适用的测量设备类型ID
  `component_type_id` int(11) DEFAULT NULL, #适用的零件类型ID
  `eff_date` datetime DEFAULT NULL, #程序生效时间
  `prg_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #程序状态："S"为有效状态，"W"为无效状态
  PRIMARY KEY (`meas_prg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 机加程序定义配置表
# 说明：
#      机加程序用于部署在特定的机加设备上，对特定的
# 零件类型进行加工的程序。这里，将机加程序也定义为
# 配置表，而非实例表，主要考虑机加程序具有一定的通用型，
# 其适用范围和机加设备类型、零件类型相关，但和具体哪一个
# 设备、哪一个零件无关。
CREATE TABLE `sca_op_prg_def` (
  `op_prg_id` int(11) NOT NULL, #机加程序ID
  `op_prg_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #机加程序描述
  `op_prg_name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #机加程序名称
  `op_device_type_id` int(11) DEFAULT NULL, #适用的机加设备类型ID
  `component_type_id` int(11) DEFAULT NULL, #适用的零件类型ID
  `eff_date` datetime DEFAULT NULL, #程序生效时间
  `prg_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #程序状态："S"为有效状态，"W"为无效状态
  PRIMARY KEY (`op_prg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量结果类型定义配置表
# 说明：
#      不同的测量程序的输出一般都有特定的结果格式，
# 此表定义了测量结果的格式ID，及后续自动机加程序调整
# 所要用到的关键字段ID。
CREATE TABLE `sca_meas_res_type_def` (
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `meas_res_type_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #测量结果类型描述
  `meas_res_format_id` int(11) DEFAULT NULL, #测量结果格式ID，目前先填1，代表以tab分隔的带标题行的文件
  `meas_prg_id` int(11) DEFAULT NULL, #测量程序ID
  `key_field_col_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #测量条目字段ID
  `act_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #实测值字段ID
  `nom_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #名义值字段ID
  `lowertol_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #下公差字段ID
  `uppertol_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #上公差字段ID
  `diff_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #差异字段ID
  `exceed_field_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #超差字段ID
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #测量结果类型状态："S"为有效状态，"W"为无效状态
  PRIMARY KEY (`meas_res_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量条目别名定义配置表
# 说明：
#      该表对不同的测量结果类型ID，定义了各测量条目的
# 原始内容与其序号或别名的对应关系。序号或别名主要用于
# 简化后续配置中的引用。
CREATE TABLE `sca_meas_res_key_field_alias` (
  `alias_id` int(11) NOT NULL, #别名ID
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `key_field_data` varchar(500) COLLATE utf8_unicode_ci NOT NULL, #测量条目内容
  `key_field_id` int(11) NOT NULL, #测量条目序号，对同一个测量结果类型而言，测量条目序号从1开始递增
  `key_field_alias` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL, #测量条目别名，别名可用于后续定义规则
  PRIMARY KEY (`alias_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量结果类型关联群组配置表
# 说明：
#      测量结果类型一般是对某一类特定零件的多方面尺寸的测量，
# 对某种零件来说，其一般包含多条测量条目不同的数据。
# 此表将特定零件的多方面的尺寸定义成一个群组，便于后续优化。
CREATE TABLE `sca_meas_res_grp_def` (
  `res_grp_id` int(11) NOT NULL, #群组ID
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #群组代码，在同一个meas_res_type_id中应该唯一
  `res_grp_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #群组描述
  PRIMARY KEY (`res_grp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量结果类型关联群组明细配置表
# 说明：
#      测量结果类型一般是对某一类特定零件的多方面尺寸的测量，
# 对某种零件来说，其一般包含多条测量条目不同的数据。
# 此表以key_field_item定义了以测量条目内容分组的群组明细，便于后续优化。
CREATE TABLE `sca_meas_res_grp_detail_def` (
  `res_grp_detail_id` int(11) NOT NULL, #群组明细定义ID
  `res_grp_id` int(11) NOT NULL, #群组ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #群组代码，这是一个冗余字段，用于增强配置可读性
  # 以下测量条目标识采用[key_field_id]或者[key_field_alias]的形式，以便于配置和理解
  `key_field_item` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #测量条目标识
  # 以下字段是测量条目优化目标权重，这定义了优化时关键尺寸的权重，
  # 优化目标函数为：w1*abs(尺寸1差异)+w2*abs(尺寸2差异)+...
  # 总体优化目标为上述优化目标函数取得最小值。
  # 如果为空则该尺寸在默认规则中不作为优化目标；
  # 如果该尺寸的上下公差没有全部定义，则该尺寸也不作为默认优化目标，以下字段无效。
  `key_field_opt_weight` int(11) DEFAULT NULL, #测量条目优化目标权重
  PRIMARY KEY (`res_grp_detail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量结果类型数据规则原子值定义表
CREATE TABLE `sca_meas_data_atom_def` (
  `atom_def_id` int(11) NOT NULL, #原子值定义ID
  `atom_def_code` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #原子值定义代码
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `res_grp_id` int(11) NOT NULL, #群组ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #群组代码，这是一个冗余字段，用于增强配置可读性
  # 原子返回值定义表达式允许使用数据中的偏差和超差等数据计算返回值
  # 表达式可以引用群组内测量条目内容ID或别名来组合成各种数学表达式，
  # 引用的格式如下：
  # [key_field_id].datatype或[key_field_alias].datatype
  # 其中的datatype可取如下值之一：
  # DIFF,EXCEED,ACT,NOM,UPPER,LOWER,MIDDLE
  # DIFF代表偏差数据；EXCEED代表超差数据；
  # ACT代表实测数据；NOM代表名义数据；
  # UPPER代表上公差；LOWER代表下公差；MIDDLE代表上下公差的中间值
  # 例如：abs([1].ACT-[1].NOM)代表测量条目内容ID为1的实测数据减去名义数据的值的绝对数。
  `atom_expr_str` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL, #原子返回值定义表达式
  PRIMARY KEY (`atom_def_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量结果类型自动化机加程序修正规则明细定义表
# 说明：
#      此表定义了特定群组ID的非默认优化规则。
#      需要注意的是，如下的默认规则是不需要定义的：
#
#      默认限制规则是同一群组内所有的尺寸都要满足上下公差要求
#          （结果文件中没有上下公差的除外，仅有上公差或仅有下公差也需要满足）
#      默认目标规则是同一群组内所有的尺寸差异绝对值都要按照key_field_opt_weight定义的权重累加，
#          尺寸差异是指实际尺寸和上下公差的中间值的差异，
#          优化目标为以上加权值最小化。
#         （如果key_field_opt_weight为空的除外，如果仅有上公差或仅有下公差也除外）
#      默认预警规则是空，如果后续未定义则不预警
#      以上默认规则是不需要在此规则表中定义的，默认都是生效的，除非我们定义了
#          除外默认规则。
CREATE TABLE `sca_meas_data_corr_rule_detail_def` (
  `rule_detail_id` int(11) NOT NULL, #规则明细ID
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `res_grp_id` int(11) NOT NULL, #群组ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #群组代码，这是一个冗余字段，用于增强配置可读性
  # 支持以下规则明细类型
  # R：限制规则，表示需要满足的限制条件
  # D：目标规则，表示修正的最终目标
  # A：预警规则，表示测量时发生偏差，例如夹具歪了，这里需要体现，能够自动告警
  `rule_detail_type` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #规则明细类型
  `except_bit` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL, #除外规则标志，如果此字段为E，则代表此规则为除外默认规则
  # 根据rule_detail_type和except_bit的不同组合，下面的规则明细定义表达式具有不同的形式和含义：
  # 假设（rule_detail_type,except_bit）为如下值：
  # （R，E）：表达式的形式为[key_field_id]或[key_field_alias]，表示特定的测量条目内容默认限制规则不执行
  # （D，E）：表达式的形式为[key_field_id]或[key_field_alias]，表示特定的测量条目内容默认目标规则不执行
  # （A，E）：不允许，不存在这种组合
  # （R，空）：表达式的形式为由[key_field_id].datatype、[key_field_alias].datatype、[atom_def_code]组成的条件表达式
  #            例如：abs([key_field_alias].ACT-[key_field_alias].MIDDLE)<2
  # （D，空）：表达式的形式为由[key_field_id].datatype、[key_field_alias].datatype、[atom_def_code]组成的算术表达式，
  #            优化目标为该算术表达式达到极小值。
  #            例如：abs([key_field_alias].ACT-[key_field_alias].MIDDLE)，
  #                  含义为实测值和上下公差中间值的差的绝对值要达到极小值，即与默认目标规则含义相同。
  # （A，空）：表达式的形式为由[key_field_id].datatype、[key_field_alias].datatype、[atom_def_code]组成的条件表达式
  #            例如：abs([key_field_alias1].ACT-[key_field_alias2].ACT)<2
  #                  含义为两个尺寸的实测值之间差距不能过大，否则就要告警
  `rule_detail_expr_str` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL, #规则明细定义表达式
  # 以下规则优化目标权重字段仅对目标规则类型D生效，表示该规则在最终的优化目标表达式中的权重系数
  `rule_opt_weight` int(11) DEFAULT NULL, #规则优化目标权重
  PRIMARY KEY (`rule_detail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 机加程序或设备状态优化调整定义表
# 说明：
#      此表定义了作为零件尺寸的优化调整分组res_grp_id中，
# 允许在生产调试时采取的调整方法，包括机加程序的调整、
# 坐标系的调整等等。
CREATE TABLE `sca_grp_op_adj_def` (
  `op_adj_id` int(11) NOT NULL, #操作调整ID
  `op_code_id` int(11) DEFAULT NULL, #操作代码序号，这用于在描述尺寸和操作关系表达式时引用，在一个优化群组res_grp_id内，应唯一
  `op_code_str` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #操作代码字串，同上需要被引用，在群组res_grp_id内应唯一
  `op_code_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #操作代码描述
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `res_grp_id` int(11) NOT NULL, #群组ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #群组代码，这是一个冗余字段，用于增强配置可读性
  # 以下操作明细类型定义了调整措施的类型如下：
  # P：机加程序调整，op_prg_id、op_prg_pos_tag有效
  # C：坐标系调整，coordinates_id有效
  `op_detail_type` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #操作明细类型
  `op_prg_id` int(11) DEFAULT NULL, #机加程序ID
  `op_prg_pos_tag` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL, #机加程序位置标识符，要修改的内容位于该标识符下一行；
  `coordinates_id` int(11) DEFAULT NULL, #坐标系ID
  `dest_axis_direction` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL, #尺寸调整坐标轴方向（允许填X、Y或Z）
  `tool_grp_id` int(11) DEFAULT NULL, #加工刀具群组ID，代表这个操作ID对应的各类刀具的集合，包括粗加工刀、精加工刀等
  PRIMARY KEY (`op_adj_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量结果类型尺寸变动与优化调整数值关系定义表
# 说明：
#      此表定义了测量结果类型中关键测量尺寸对优化调整数值之间的运算关系，
# 当某一个加工参数调整时，很可能相关的多个尺寸都会受到影响。
CREATE TABLE `sca_meas_res_value_delta_def` (
  `meas_delta_def_id` int(11) NOT NULL, #尺寸变动定义ID
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `res_grp_id` int(11) NOT NULL, #群组ID
  `res_grp_code` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL, #群组代码，这是一个冗余字段，用于增强配置可读性
  # 以下差异测量条目标识采用D[key_field_id]或者D[key_field_alias]的形式，以便于配置和理解
  `delta_key_field_item` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #差异测量条目标识
  # 以下表达式定义了特定尺寸和加工操作调整之间的关系，一般采用如下的形式：
  # 由D[op_code_id]或D[op_code_str]组成的数学表达式，代表加工操作调整导致的尺寸变化量
  `delta_rely_op_str` varchar(1000) COLLATE utf8_unicode_ci NOT NULL, #差异变化的计算表达式
  PRIMARY KEY (`meas_delta_def_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 机加坐标系定义表
CREATE TABLE `sca_op_coordinates_def` (
  `coordinates_id` int(11) NOT NULL, #坐标系ID
  `coordinates_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #坐标系描述
  PRIMARY KEY (`coordinates_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


##################################################
#
#  以下为实例表定义
#  实例表在命名上均以msca_开头
#
##################################################

# 测量结果文件群组存放位置实例表
# 说明：
#      此表定义了特定的测量结果文件在文件系统中的存放位置，
# 以及系统如何自动获取的正则表达式等信息，一般的，
# 将存放在同一个文件系统目录中的同一种测量结果文件定义为
# 一个测量结果文件群组，且对应于唯一的meas_res_type_id。
CREATE TABLE `msca_meas_res_file_grp_store` (
  `meas_res_file_grp_id` int(11) NOT NULL, #测量结果文件群组ID
  `meas_res_file_grp_desc` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #测量结果文件群组描述
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `file_loc_dir` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL, #此类文件存放的目录
  `filename_re_pattern` varchar(500) COLLATE utf8_unicode_ci NOT NULL, #寻找此类文件的正则表达式
  `db_tab_prefix_str` varchar(100) COLLATE utf8_unicode_ci NOT NULL, #此群组文件入库后数据库表名字符串，实际表名为："m" + meas_res_file_grp_id + "_" + db_tab_prefix_str
  `scan_delay` int(11) NOT NULL, #读取扫描间隔（毫秒）
  `type_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #群组类型状态："S"为有效状态，"W"为关闭状态
  PRIMARY KEY (`meas_res_file_grp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 测量结果文件入库日志表
# 说明：
#      此表记录了已入库的测量结果文件日志，
# 系统将会自动扫描文件系统目录，对符合要求的文件进行入库处理，
# 并需要判断该文件是否已入库或正在入库（支持并行处理，所以实现时
# 需要考虑数据库操作的原子性）。
CREATE TABLE `msca_meas_res_file_dump_log` (
  `dump_log_id` int(11) NOT NULL, #日志记录ID
  `meas_res_file_grp_id` int(11) NOT NULL, #测量结果文件群组ID
  `meas_res_type_id` int(11) NOT NULL, #测量结果类型ID
  `full_file_name` varchar(1000) COLLATE utf8_unicode_ci NOT NULL, #包含完整路径的文件名称
  `full_db_tab_name` varchar(1000) COLLATE utf8_unicode_ci NOT NULL, #完整的数据库存储表名
  `eff_date` datetime NOT NULL, #该文件倒入的日期和时间
  `dump_status` varchar(10) COLLATE utf8_unicode_ci NOT NULL, #倒入状态："S"为成功，"E"为失败
  `dump_err_msg` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL, #倒入错误信息，在倒入失败时填写
  `column_cnt` int(11) DEFAULT NULL, #倒入文件列计数
  `row_cnt` int(11) DEFAULT NULL, #倒入文件行计数
  PRIMARY KEY (`dump_log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

##################################################
#
#  以下为控制表定义
#  控制表在命名上均以ctrl_开头
#
##################################################

# 序列号sequence控制表
# 说明：
#      此表用于生成类似oracle的唯一序列号。
CREATE TABLE `ctrl_seq_data` (
  `seq_name` varchar(200) COLLATE utf8_unicode_ci NOT NULL, #序列号名称
  `curr_value` int(11) NOT NULL, #序列号当前值
  `min_value` int(11) NOT NULL, #序列号最小值
  `max_value` int(11) NOT NULL, #序列号最大值
  `increment` int(11) NOT NULL DEFAULT 1, #序列号每次增长值
  PRIMARY KEY (`seq_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


##################################################
#
#  以下为mysql相关生成seq的函数
#
##################################################

DROP FUNCTION IF EXISTS get_seq_currval;
DELIMITER $
CREATE FUNCTION get_seq_currval(t_seq_name varchar(200))
  RETURNS int
  LANGUAGE SQL
  DETERMINISTIC
  READS SQL DATA
  SQL SECURITY DEFINER
BEGIN
  #DECLARE变量的声明必须放在开头，且在异常处理定义之前
  DECLARE v_lock_res int;
  DECLARE v_lock_timeout int;
  DECLARE v_find_bit int;
  DECLARE v_curr_val int;
  #设定找不到数据告警的处理规则
  DECLARE no_data_found CONDITION FOR 1329;
  DECLARE CONTINUE HANDLER FOR no_data_found SET v_find_bit=0;
  if t_seq_name is null then
    SIGNAL SQLSTATE 'SE003' SET MESSAGE_TEXT = '输入参数不能为空';
  end if;
  #设置锁定超时，单位为秒
  SET v_lock_timeout=5;
  select get_lock(t_seq_name,v_lock_timeout) into v_lock_res
    from dual;
  if v_lock_res!=1 then
    SIGNAL SQLSTATE 'SE001' SET MESSAGE_TEXT = '获取seq互斥锁失败';
  end if;
  SET v_find_bit=1;
  select curr_value into v_curr_val
    from ctrl_seq_data
    where seq_name=t_seq_name;
  #release_lock用户释放seq互斥锁，返回值不重要，
  #但是一定要into到一个变量，否则会报错，说是函数不能返回一个结果集。
  select release_lock(t_seq_name) into v_lock_res from dual;
  if v_find_bit!=1 then
    SIGNAL SQLSTATE 'SE002' SET MESSAGE_TEXT = '指定的seq_name不存在';
  end if;
  return v_curr_val;
END
$
DELIMITER ;


DROP FUNCTION IF EXISTS init_seq;
DELIMITER $
CREATE FUNCTION init_seq(t_seq_name varchar(200),t_init_val int,t_max_val int,t_increment int)
  RETURNS int
  LANGUAGE SQL
  DETERMINISTIC
  MODIFIES SQL DATA
  SQL SECURITY DEFINER
BEGIN
  #DECLARE变量的声明必须放在开头，且在异常处理定义之前
  DECLARE v_lock_res int;
  DECLARE v_lock_timeout int;
  DECLARE v_dup_bit int;
  #设定插入重复主键数据错误的处理
  DECLARE dup_primary_key CONDITION FOR 1062;
  DECLARE CONTINUE HANDLER FOR dup_primary_key SET v_dup_bit=1;
  if (t_seq_name is null) or (t_init_val is null) or (t_max_val is null) or (t_increment is null) then
    SIGNAL SQLSTATE 'SE003' SET MESSAGE_TEXT = '输入参数不能为空';
  end if;
  if (t_init_val<0) or (t_max_val<=0) or (t_increment<=0) or (t_init_val>=t_max_val) then
    SIGNAL SQLSTATE 'SE004' SET MESSAGE_TEXT = '输入参数不合法';
  end if;
  #设置锁定超时，单位为秒
  SET v_lock_timeout=5;
  select get_lock(t_seq_name,v_lock_timeout) into v_lock_res
    from dual;
  if v_lock_res!=1 then
    SIGNAL SQLSTATE 'SE001' SET MESSAGE_TEXT = '获取seq互斥锁失败';
  end if;
  SET v_dup_bit=0;
  insert into ctrl_seq_data(seq_name,curr_value,min_value,max_value,increment)
    values(t_seq_name,t_init_val,t_init_val,t_max_val,t_increment);
  select release_lock(t_seq_name) into v_lock_res from dual;
  if v_dup_bit!=0 then
    SIGNAL SQLSTATE 'SE005' SET MESSAGE_TEXT = '不能重复创建已经存在的seq_name';
  end if;
  return 0;
END
$
DELIMITER ;


DROP FUNCTION IF EXISTS get_seq_nextval;
DELIMITER $
CREATE FUNCTION get_seq_nextval(t_seq_name varchar(200))
  RETURNS int
  LANGUAGE SQL
  DETERMINISTIC
  MODIFIES SQL DATA
  SQL SECURITY DEFINER
BEGIN
  #DECLARE变量的声明必须放在开头，且在异常处理定义之前
  DECLARE v_lock_res int;
  DECLARE v_lock_timeout int;
  DECLARE v_find_bit int;
  DECLARE v_curr_val int;
  DECLARE v_min_value int;
  DECLARE v_max_value int;
  DECLARE v_increment int;
  #设定找不到数据告警的处理规则
  DECLARE no_data_found CONDITION FOR 1329;
  DECLARE CONTINUE HANDLER FOR no_data_found SET v_find_bit=0;
  if t_seq_name is null then
    SIGNAL SQLSTATE 'SE003' SET MESSAGE_TEXT = '输入参数不能为空';
  end if;
  #设置锁定超时，单位为秒
  SET v_lock_timeout=5;
  select get_lock(t_seq_name,v_lock_timeout) into v_lock_res
    from dual;
  if v_lock_res!=1 then
    SIGNAL SQLSTATE 'SE001' SET MESSAGE_TEXT = '获取seq互斥锁失败';
  end if;
  SET v_find_bit=1;
  select curr_value,min_value,max_value,increment
    into v_curr_val,v_min_value,v_max_value,v_increment
    from ctrl_seq_data
    where seq_name=t_seq_name;
  if v_find_bit!=1 then
    select release_lock(t_seq_name) into v_lock_res from dual;
    SIGNAL SQLSTATE 'SE002' SET MESSAGE_TEXT = '指定的seq_name不存在';
  end if;
  SET v_curr_val=v_curr_val+v_increment;
  if v_curr_val>v_max_value then
    SET v_curr_val=v_min_value;
  end if;
  update ctrl_seq_data
    set curr_value=v_curr_val
    where seq_name=t_seq_name;
  select release_lock(t_seq_name) into v_lock_res from dual;
  return v_curr_val;
END
$
DELIMITER ;

select init_seq('seq_dump_log_id',1,1000000000,1);

