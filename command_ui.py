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
#
import os
import sys
import glob
import datetime
import collections
from libs import guide_manager
from libs import report_manager


class UI:
    def __init__(self):
        self.now_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        self.switches = self.switch_to_dict(sys.argv)
        if "guide" in self.switches:
            self.guide = self.switches['guide']
        else:  # no guide provided
            if "plot" not in self.switches:
                sys.exit("You must provide either a -guide <file_path> or a -plot <parameters> switch")
            self.guide = "command_guides" + os.sep + "command_guide" + self.now_time + ".csv"
            self.gm = guide_manager.guide_manager()
            self.plot_count = len(self.switches['plot'].split(","))
            self.sNp_paths = self.sNp(self.switches)
            self.occurrences = collections.defaultdict(dict)
            for pc in range(self.plot_count):
                for sp in self.sNp_paths:
                    self.occurrences[pc][sp] = 1
            self.gm.build_interactions(self.plot_count, self.sNp_paths, self.occurrences)
            self.gm.add(self.ports(self.switches))
            self.plots_and_parameters(self.switches)
            self.gm.add_paths_and_names()
            self.gm.to_csv(self.guide)
        self.info = self.get_info(self.switches)
        self.template = self.get_template(self.switches)
        self.output = self.get_output(self.switches)
        self.rm = report_manager.report_manager(self.guide, self.info, self.template, self.output)

    def __str__(self):
        return str(self.switches)

    def switch_to_dict(self, switch_list):
        switches = {}
        for i, arg in enumerate(switch_list):
            if arg[0] == "-":
                if len(switch_list) > i + 1 and switch_list[i + 1][0] != "-":
                    switches[arg[1:]] = switch_list[i + 1]
                else:
                    switches[arg[1:]] = ""
        return switches

    def sNp(self, switches):
        if "sNp" in switches:
            return glob.glob(switches['sNp']+os.sep+"*.s*p")
        else:  # default sNp folder
            return glob.glob("sNp"+os.sep+"*.s*p")

    def ports(self, switches):
        # ['s_parameter', 'single/diff', 'mag/deg', 'port_map']
        if "single" in switches and switches["single"]:
                return {'single/diff': 's', 'port_map': 0}
        else:  # default differential
            if 'port_map' in switches:
                return {'single/diff': 'd', 'port_map': int(switches['port_map'])}
            else:  # default port_map 1
                return {'single/diff': 'd', 'port_map': 1}

    def plots_and_parameters(self, switches):
        plot_params = switches['plot'].split(',')
        print "len", len(plot_params)
        for plot, parameters in enumerate(plot_params):
            print "plot", plot
            print "params", str(parameters)[:-1]
            print "mag/deg", str(parameters)[-1]
            print "===="
            conditions = {'plot': plot}
            dictionary = {'s_parameter': parameters[:-1], 'mag/deg': parameters[-1]}
            self.gm.add(dictionary, conditions)

    def get_info(self, switches):
        if "info" in switches:
            return switches['info']
        else:
            return "info" + os.sep + "info.csv"

    def get_template(self, switches):
        if "template" in switches:
            return switches['template']
        else:
            return "template" + os.sep + "template.docx"

    def get_output(self, switches):
        if "output" in switches:
            return switches['output']
        else:
            return "reports" + os.sep + "report" + self.now_time + ".docx"

if __name__ == "__main__":
    u = UI()
