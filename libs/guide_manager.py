# guide_manager.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import matlab.engine
import os
import copy
import csv
import numpy as np


'''
This is a one class program which performs all operations associated with
the guide file.

interactions is a list of dictionaries
Each dictionary is called an "interaction", so the list of interactions
is naturally called the "interaction list".

Each interaction describes single plot on a single graph. The dictionary contains all of the properties of a plot.
'''

class guide_manager:
    def __init__(self, file_path=None):
        if file_path:
            self.read_csv(file_path)
        self.interactions = []

    def read_csv(self, file_path):
        if os.path.isabs(file_path):
            in_path = file_path
        else:
            in_path = 'guide' + os.sep + os.path.splitext(file_path)[0] + '.csv'

        if os.path.isfile(in_path):
            with open(in_path, 'rb') as input_file:
                self.interactions = []
                dict_reader = csv.DictReader(input_file)
                for row in dict_reader:
                    self.interactions.append(row)
        else:
            print "could not find file"
   
    def to_csv(self, filepath):
        if os.path.isabs(filepath):
            out_path = filepath
        else:
            out_path = 'guide'+os.sep+os.path.splitext(filepath)[0]+'.csv'
        directory = os.path.dirname(os.path.abspath(out_path))
        if not os.path.exists(directory):
            os.makedirs(directory)
        keys = self.interactions[0].keys()
        with open(out_path, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.interactions)

    def build_interactions(self, plot_count, sNp_paths, occurrences):
        self.interactions = []
        for iP in range(plot_count):
            for sNp_path in sNp_paths:
                for iO in range(occurrences[iP][sNp_path]):
                    new_interaction = {'plot': iP, 'sNp_path': sNp_path, 'occurrence': iO}
                    self.interactions.append(new_interaction)

    def add(self, dictionary, conditions=None):
        if not conditions:
            conditions = {}
        for i, interaction in enumerate(self.interactions):
            if all(k in interaction.keys() and interaction[k] == v for k, v in conditions.items()):
                self.interactions[i].update(dictionary)

    def find(self, dictionary):
        dictionary = copy.deepcopy(dictionary)
        interactions = copy.deepcopy(self.interactions)
        found_interactions = []
        for interaction in interactions:
            if all(k in interaction.keys() for k in dictionary.keys()):
                if all(interaction[key] == dictionary[key] for key in dictionary.keys()):
                    found_interactions.append(interaction)
        return found_interactions

    def get_commonalities(self, list_of_dicts):
        '''
        accepts a list of interactions and returns a dictionary where key, value pairs are the same for all
        :param list_of_dicts:
        :return:
        '''
        list_of_dicts = copy.deepcopy(list_of_dicts)
        intersection = dict(set.intersection(*(set(d.iteritems()) for d in list_of_dicts)))
        return intersection

    def set_xy(self):
        self.eng = matlab.engine.start_matlab()
        for interaction in self.interactions:
            interaction['x'], interaction['y'] = self.get_values(interaction)
        self.eng.quit()

    def get_values(self, interaction):
        '''
        gather y values and add them to the dictionary in the guide_manager instance
        do the same for x so you have { ..., 'x': [0,1,2,3,...], y: [0,1,2,3,...] }
        '''

        self.eng.eval("touchstone_filename = '"+interaction['sNp_path']+"';", nargout=0)
        self.eng.eval("s_obj = sparameters(touchstone_filename);", nargout=0)
        self.eng.eval("x = s_obj.Frequencies./1e9;", nargout=0)

        port_map = interaction['port_map']

        if interaction['single/diff'] == 'd':
            self.eng.eval("s_raw = s2sdd(s_obj.Parameters,"+port_map+");", nargout=0)
        else:
            self.eng.eval("s_raw = s_obj.Parameters;", nargout=0)
        Sxx = interaction['s_parameter'].split("_")[0]
        Syy = interaction['s_parameter'].split("_")[1]
        self.eng.eval("s_plot = squeeze(s_raw("+Sxx+","+Syy+",:));", nargout=0)

        if interaction['mag/deg'] == 'd':
            self.eng.eval("y = (180./pi).*(angle(s_plot));", nargout=0)
        else:
            self.eng.eval("y = 20 * log10(abs(s_plot));", nargout=0)

        x = np.array(self.eng.workspace['x']).T[0]
        y = np.array(self.eng.workspace['y']).T[0]

        return x, y

    def plot_list(self):
        '''
        :return plots: a list of the plot numbers as ints
        '''
        interactions = copy.deepcopy(self.interactions)
        plots = sorted(list({i['plot'] for i in interactions}))
        return plots

    def add_paths_and_names(self):
        '''
        goes through each interaction and gives it properties:
            sNp_name: string
            plot_name: string
            plot_path: string
        :return:
        '''
        # add plot paths
        for interaction in self.interactions:
            interaction['plot_path'] = "images"+os.sep+str(interaction['plot'])+".png"

        # add names to plots
        for plot in self.plot_list():
            interactions = self.find({'plot': plot})
            plot_name_list = list(self.get_commonalities(interactions).iteritems())
            plot_name = ""
            for element in plot_name_list:
                if element[0] not in ['plot_path', 'x', 'y', 'occurrence']:
                    if len(plot_name + str(element[0])+":"+str(element[1])+", ") <= 60:
                        plot_name += str(element[0])+":"+str(element[1])+", "
            plot_name = plot_name[:-2]
            for interaction in self.interactions:
                if interaction['plot'] == plot:
                    interaction['plot_name'] = plot_name

        # add names for sNp file
        for interaction in self.interactions:
            interaction['sNp_name'] = ".".join(os.path.split(interaction['sNp_path'])[-1].split('.')[:-1])

    def gen_plots(self):

        '''
        generates plots in the images folder
        :return:
        '''
        for p in self.plot_list():
            interactions = self.find({'plot': p})
            plt.clf()
            plots_arr = []
            for i in interactions:
                plots_arr.append(plt.plot(i['x'], i['y'], label=i['sNp_name']))
                plt.title(i['plot_name'])
            plt.xlabel('Frequency (GHz)')
            if all("m" == i['mag/deg'] for i in interactions):
                plt.ylabel('Magnitude (dB)')
            elif all("d" == i['mag/deg'] for i in interactions):
                plt.ylabel('Phase (deg)')
            else:
                plt.ylabel('Magnitude (dB) | Phase (deg)')
            leg = plt.legend(loc='lower right', prop={'size': 8})
            leg.get_frame().set_alpha(0.5)
            plt.savefig("images" + os.sep + str(p))



