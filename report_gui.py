'''
report_gui takes in from the user, info, template, and guide paths
'''

import os
import easygui as eg
from libs import report_manager


class gui:
    def __init__(self):
        self.guide = self.question1("Guide", "Select guide file")
        self.info = self.question1("Info", "Select info file")
        self.template = self.question1("Template", "Select template file")
        self.output = self.question2("Output", "Report Filename:")
        self.rm = report_manager.report_manager(self.guide, self.info, self.template, self.output)

    def question1(self, msg, title):
        '''
        questions1: Select file from dropdown
        :return: string
        '''
        filetypes = "*.*"
        file = eg.fileopenbox(title, msg, filetypes=filetypes)
        return file

    def question2(self, msg, title):
        '''
        question2: Enter a report name
        :return:
        '''
        report_title = eg.enterbox(title, msg)
        if report_title[-5:] != ".docx":
            report_title += ".docx"
        return "reports" + os.sep + report_title

if __name__ == "__main__":
    g = gui()
