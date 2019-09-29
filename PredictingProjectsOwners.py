# MP5 Start 10.05.19
from Tkinter import *
import urllib2
from bs4 import BeautifulSoup
import docclass


class FacultyMember:  # Creating the class for faculty members.

    def __init__(self, name, profile_url, publications):
        self.name = name
        self.profile_url = profile_url
        self.publications = publications


class ResearchProject:  # Creating the class for research projects.

    def __init__(self, title, summary, PI):
        self.title = title
        self.summary = summary
        self.PI = PI


class Predictor:  # Creating the class for predictor.

    def __init__(self, classifier):

        self.myclassifier = docclass.naivebayes(
            docclass.getwords)  # Calling the classifier from docclass.py by creating a classifier object
        self.faculty_members = {}
        self.research_projects = {}

    def fetch_members(self, link):  # Parsing the members

        self.members_url = []

        urlsource = urllib2.urlopen(link)
        contents = urlsource.read()

        raw_data = BeautifulSoup(contents, features="html.parser")

        h4_tags = raw_data.find_all("h4")

        for i in h4_tags:
            a_tag = i.find("a")
            self.members_url.append(a_tag.attrs["href"])

        for member in self.members_url:
            linkk = link.split("/en")[0]
            member_link = linkk + member

            member_url = urllib2.urlopen(member_link)
            member_content = member_url.read()
            self.member_data = BeautifulSoup(member_content, features="html.parser")

            name_tag = self.member_data.find("h3")

            n = name_tag.text.strip().split(" ")[0]
            s = name_tag.text.strip().split(" ")[-1]
            member_name = n + " " + s # splitting and reuniting the name and surname because there are some members with middle name

            member_publications = self.fetch_publications() # Calling the function to fetching the publications and it will return and list of publications.

            member_name = FacultyMember(member_name, member_link, member_publications) # Creating the FacultyMember object

            self.faculty_members[s] = member_name # Adding object to dict


    def fetch_publications(self): # Fetching the publications
        list_publications = []

        publication_tag = self.member_data.find_all("div")
        for p in publication_tag:
            try:
                if p.attrs[u"id"] == "flat":
                    pub = p.find_all("li")

                    for pp in pub:
                        ppp = pp.text.strip()
                        pppp = ppp.split("\n")[1]
                        list_publications.append(pppp)

            except:
                pass

        return list_publications

    def fetch_projects(self, link): # Fetching the projects.

        urlsource = urllib2.urlopen(link)
        contents = urlsource.read()

        raw_data = BeautifulSoup(contents, features="html.parser")

        research_tags = raw_data.find_all("li")

        for i in research_tags:

            try:
                if i.attrs[u"class"] == [u'list-group-item']:

                    principal_investigator = i.find_all("a")[1].text.strip()
                    project_name = i.find("h4").text.strip()

                    ptags = i.find_all("p")
                    for i in ptags:
                        try:
                            if i.attrs[u'class'] == [u'gap']:
                                summary = i.text.strip()
                        except:
                            pass

                    members = [self.faculty_members[i].name for i in self.faculty_members]
                    if principal_investigator in members:
                        project_name_obj = ResearchProject(project_name, summary, principal_investigator)

                        self.research_projects[project_name.strip()] = project_name_obj
            except:
                pass

    def train_classifier(self): # Training the data with publications and members as category

        for prof in self.faculty_members:
            catt = self.faculty_members[prof].name
            for pblction in self.faculty_members[prof].publications:
                self.myclassifier.train(pblction, catt)

    def predict_PI(self, content, PI):

        prediction_result = self.myclassifier.classify(content) # Predicting the research project

        if prediction_result == PI:
            return (1, prediction_result) # If our prediction is correct then we will return tuple with our prediction and 1
        else:
            return (0, prediction_result) # If our prediction is wrong then we will return tuple with our prediction and 0


class ESTIMATOR_GUI(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        self.PredictorObj = Predictor("none")

    def initUI(self):
        self.pack(fill=X)
        self.frame0 = Frame(self)
        self.frame1 = Frame(self.frame0)
        self.frame2 = Frame(self.frame0)

        self.header = Label(self, text="PI Estimator Tool for SEHIR CS Projects", bg="lightseagreen", fg="white",
                            height=1, font=("Calibri", 25, "bold"))

        self.firstURL = Entry(self, width=90)
        self.secondURL = Entry(self, width=90)
        self.fetchButton = Button(self, text="Fetch", font=("Calibri", 11, "bold"), width=8, command=self.fetchButtonC)

        # Frame1
        self.v_scroolbar = Scrollbar(self.frame1, orient=VERTICAL)

        self.projectsLabel = Label(self.frame1, text="Projects", font=("Calibri", 25))
        self.projectsListbox = Listbox(self.frame1, width=90, height=10, yscrollcommand=self.v_scroolbar.set)
        self.projectsListbox.bind("<<ListboxSelect>>", self.selectResearch)
        self.v_scroolbar.config(command=self.projectsListbox.yview)

        # Frame2

        self.predictionLabel = Label(self.frame2, text="Prediction", font=("Calibri", 25))
        self.predictionResult = Label(self.frame2, text="")

        self.header.pack(fill=X, pady=(0, 8))

        self.firstURL.pack(pady=4)
        self.secondURL.pack(pady=(4, 6))
        self.fetchButton.pack()

        self.frame0.pack(fill=X, padx=(50, 0))
        self.frame1.pack(side=LEFT, fill=BOTH)
        self.frame2.pack(fill=BOTH)

        self.projectsLabel.pack()
        self.predictionLabel.pack()
        self.projectsListbox.pack(side=LEFT)
        self.v_scroolbar.pack(side=RIGHT, fill=Y)
        self.predictionResult.pack(pady=(30, 0))

    def fetchButtonC(self):
        try:
            membersUrl = self.firstURL.get()
            projectUrl = self.secondURL.get()

            self.PredictorObj.fetch_members(membersUrl)       # Calling the functions to fetch
            self.PredictorObj.fetch_projects(projectUrl)      # Calling the functions to fetch

            projects = []                                                                     # Filling the projects listbox
                                                                                              # Filling the projects listbox
            for project in self.PredictorObj.research_projects:                               # Filling the projects listbox
                projects.append(self.PredictorObj.research_projects[project].title)           # Filling the projects listbox
            projects.sort()                                                                   # Filling the projects listbox
                                                                                              # Filling the projects listbox
            for project in projects:                                                          # Filling the projects listbox
                self.projectsListbox.insert(END, project.strip())                             # Filling the projects listbox
            self.PredictorObj.train_classifier()                                              # Filling the projects listbox
        except:
            pass

    def selectResearch(self, event):
        try:
            researchTitle = self.projectsListbox.get(self.projectsListbox.curselection())
            for project in self.PredictorObj.research_projects:
                if researchTitle == self.PredictorObj.research_projects[project].title:
                    object = self.PredictorObj.research_projects[project]
                    PI = self.PredictorObj.research_projects[project].PI
                    title = self.PredictorObj.research_projects[project].title
                    summary = self.PredictorObj.research_projects[project].summary
                    content = title + " " + summary

            result = self.PredictorObj.predict_PI(content, PI)

            if result[0] == 1: # If the first item of our tuple which was returned by prediction function then our prediction is correct!
                self.predictionResult.config(text=result[1], bg="green", font=("Calibri", 25, "bold"))
            else:
                self.predictionResult.config(text=result[1], bg="red", font=("Calibri", 25, "bold"))

        except:
            pass
def main():
    root = Tk()
    root.title("ESTIMATOR")
    root.geometry("1000x380+290+50")
    app = ESTIMATOR_GUI(root)
    root.mainloop()


main()