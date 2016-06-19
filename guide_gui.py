# GUI.py
'''
this GUI uses easygui to ask a series of questions to the user and will build an interaction dictionary from it

'''
import os
import easygui as eg
from libs import guide_manager

class gui:
    def __init__(self):
        self.keys = ['s_parameter', 'single/diff', 'mag/deg', 'port_map']
        self.field_names = ['s_parameter (ex: \'5_16\')',
                            'single/diff (ex: \'s\' or \'d\')',
                            'mag/deg (ex: \'m\' or \'d\')',
                            'port_map (ex: \'1\', \'2\', or \'3\')']
        self.gm = guide_manager.guide_manager()
        self.guide_name, self.plot_count = self.question1()
        self.sNp_paths = self.question2()   
        self.occurrences = self.question3()
        self.gm.build_interactions(self.plot_count, self.sNp_paths, self.occurrences)
        self.gm.add(self.question4())
        self.single_to_port()
        for iP in range(self.plot_count):
            dictionary, conditions = self.question5(iP)
            self.gm.add(dictionary, conditions)
            self.single_to_port()
        for sNp_path in self.sNp_paths:
            dictionary, conditions = self.question6(sNp_path)
            self.gm.add(dictionary, conditions)
            self.single_to_port()
        for interaction in self.gm.interactions:
            dictionary, conditions = self.question7(interaction)
            self.gm.add(dictionary, conditions)
            self.single_to_port()
        self.gm.add_paths_and_names()
        self.gm.to_csv(self.guide_name)

    def single_to_port(self):
        for interaction in self.gm.interactions:
            if "single/diff" in interaction:
                if interaction["single/diff"] == "s":
                    interaction["port_map"] = 0
        return False
 
    def question1(self):
        '''
        question1: guide file name, how many plots
        :return:
        '''
        msg = "Please answer some basic questions to get started"
        title = "Basic Questions"
        field_names = ['What is the name of the guide file?', 'How many plots would you like?']

        field_values = eg.multenterbox(msg, title, field_names)
        field_values[1] = int(field_values[1])
        
        return field_values

    def question2(self):
        '''
        questions2: select sNp files
        :return: list
        '''
        msg = "Please select ALL sNp files you wish to use"
        title = "Select sNp files"
        filetypes = "*.*"
        multiple = True
        files = eg.fileopenbox(msg, title, filetypes=filetypes, multiple=multiple)
        return files

    def question3(self):
        '''
        questions3: enter occurrences
        :returns: a dict[plot_number][sNp_path] = occurrences
        '''
        global_occurrences = {}
        for iP in range(self.plot_count):
            occurance_dict = {}
            msg = "How many times should each file occur in plot " + str(iP+1)
            title = "Plot " + str(iP+1) + " graphs"
            field_names = [os.path.split(path)[-1] for path in self.sNp_paths]
            occurrences = eg.multenterbox(msg, title, field_names)
            occurrences = [0 if o == '' else int(o) for o in occurrences]
            for i, path in enumerate(self.sNp_paths):
                occurance_dict[path] = occurrences[i]
            global_occurrences[iP] = occurance_dict
        return global_occurrences

    def question4(self):
        '''
        question4: Universal Properties
        :return:
        '''
        msg = "Please enter any properties that are completely universal"
        title = "Universal Questions"
        field_names = list(self.field_names)
        field_values = eg.multenterbox(msg, title, field_names)
        keys = self.keys
        dictionary = {keys[i]: value for i, value in enumerate(field_values) if value and len(value) > 0}
        return dictionary

    def question5(self, iP):
        '''
        question5: Plot Properties
        :return:
        '''
        msg = "Please enter any properties that are universal for just plot " + str(iP+1)
        title = "Plot Questions"
        keys = list(self.keys)
        field_names = list(self.field_names)
        interactions = self.gm.find({'plot': iP})
        remove_indices = []
        for ik, key in enumerate(keys):
            if all(key in i.keys() for i in interactions):
                remove_indices.append(ik)
        keys = [k for i, k in enumerate(keys) if i not in remove_indices]
        field_names = [k for i, k in enumerate(field_names) if i not in remove_indices]
        if len(field_names) >= 1:
            field_values = eg.multenterbox(msg, title, field_names)
        else:
            field_values = []
        dictionary = {keys[i]: value for i, value in enumerate(field_values) if len(value) > 0}
        conditions = {'plot': iP}
        return dictionary, conditions

    def question6(self, sNp_path):
        '''
        question6: sNp file properties
        :return:
        '''
        msg = "Please enter any properties that are universal for just sNp " + os.path.split(sNp_path)[-1]
        title = "sNp Questions"
        keys = list(self.keys)
        field_names = list(self.field_names)
        interactions = self.gm.find({'sNp_path': sNp_path})
        remove_indices = []
        for ik, key in enumerate(keys):
            if all(key in i.keys() for i in interactions):
                remove_indices.append(ik)
        keys = [k for i, k in enumerate(keys) if i not in remove_indices]
        field_names = [k for i, k in enumerate(field_names) if i not in remove_indices]
        if len(field_names) >= 1:
            field_values = eg.multenterbox(msg, title, field_names)
        else:
            field_values = []
        dictionary = {keys[i]: value for i, value in enumerate(field_values) if len(value) > 0}
        conditions = {'sNp_path': sNp_path}
        return dictionary, conditions

    def question7(self, interaction):
        '''
        question7: any remaining unanswered properties
        :return:
        '''
        msg = "Please enter any properties that are universal for interaction \n" + str(interaction)
        title = "Interaction Questions"
        keys = list(self.keys)
        field_names = list(self.field_names)
        interactions = list([interaction])
        remove_indices = []
        for ik, key in enumerate(keys):
            if all(key in i.keys() for i in interactions):
                remove_indices.append(ik)
        keys = [k for i, k in enumerate(keys) if i not in remove_indices]
        field_names = [k for i, k in enumerate(field_names) if i not in remove_indices]
        if len(field_names) >= 1:
            field_values = eg.multenterbox(msg, title, field_names)
        else:
            field_values = []
        dictionary = {keys[i]: value for i, value in enumerate(field_values) if len(value) > 0}
        conditions = interaction
        return dictionary, conditions

if __name__ == "__main__":
    g = gui()
