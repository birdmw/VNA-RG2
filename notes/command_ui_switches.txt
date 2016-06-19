# command_ui.py generates reports using command line switches
#
# METHOD:
# python comamnd_ui.py -switch1 value1 -switch2 value2 -switch3 value3
#
# YOU MUST PROVIDE EITHER A -guide SWITCH OR A -plot SWITCH AT THE BARE MINIMUM
# IF YOU PROVIDE A -guide SWITCH, THE FOLLOWING SWITCHES ARE IGNORED: sNp, plot, port_map, single
#
#                        MANDATORY
#
# ====================== guide switch ======================
# guide switch is a path to a guide file.
#  -guide <file_path>
#   ex: -guide c:\guide_dir\guide.csv
#   default: None
#
#                            OR
#
# ====================== sNp switch ======================
# sNp switch is a path to a directory. This directory will be harvested non-recursively for sNp files to be used.
#  -sNp <dir_path>
#   ex: -sNp c:\sNp_dir
#   default: ~\sNp
#
# ====================== plot switch ======================
# plot switch is a string of text describing plots and their range as either magnitude(m) or phase in degrees(d).
#   -plot <string>
#   ex: -plot 1_1m,1_1d,2_1m,2_1d
#   default: 1_1m,1_1d,2_1m,2_1d,2_1m,2_1d,2_2m,2_2d
#
#                          OPTIONAL
#
# ====================== port map switch ======================
# port map switch determines the style of port_map for differential pairs. Google "Matlab s2sdd" to see what 1,2,3 mean.
#   -port_map <int>
#   ex: -port_map 1
#   default: 1
#
# ====================== single switch ======================
# single switch inhibits the port_map conversion from single to differential across all sNp files.
#   -single <bool>
#   ex: -single True
#   default: False
#
# ====================== template switch ======================
# template switch provides a path to a template file.
#   -template <file_path>
#   ex: -template c:\template_dir\template.docx
#   default: ~\template\template.docx
#
# ====================== info switch ======================
# info switch provides a path to a info file.
#   -info <file_path>
#   ex: -info c:\info_dir\info.docx
#   default: ~\info\info.docx
#
# ====================== output switch ======================
# output switch provides a path to a output file.
#   -output <file_path>
#   ex: -output c:\output_dir\report.docx
#   default: ~\reports\report<data_time>.docx