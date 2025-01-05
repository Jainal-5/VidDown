from util import downloader
import os

class BaseSite:
    def __init__(self):
        self.sessions = None

    def printInterface(self):
        print(f"\nYou have {len(self.sessions.sessions)} session")
        
        print("\t0 - Back")
        print(f"\t1 - Continue at index 0 with a title of {self.sessions.sessions[0].title}")
        print("\t2 - Find and download by title")
        print("\t3 - Find and download by index")
        print("\t4 - Set Episodes names")
        print("\t5 - Add new session")

        validC = [0,1,2,3,4,5]

        while True:
            try:
                choice = int(input("Enter Option: "))
            except ValueError as e:
                print(f"Value Error: {choice} is not a digit")

            if choice in validC:
                return choice
            else:
                print("Invalid input")

    def download(self, index=0):
        while len(self.sessions.sessions) > 0:
            try:
                currentSession = self.sessions.sessions[index]
            except IndexError:
                print(f"IndexError: No element at index {index}")
                print(f"There are {len(self.sessions.sessions)} element in Sessions.")
                break

            if type(currentSession.url) == type(list()):
                currentSession = self.listDownload(index)
            elif type(currentSession.url) == type(dict()):
                currentSession = self.dictionaryDownload(index)
            else:
                print("Error: url have different type")
                self.main()

            self.sessions.sessions.remove(currentSession)
            self.sessions.saveSessions()
            if index != 0:
                index = 0
        print("All sessions download finish")
        os.system("termux-vibrate -d 5000")


    def findByTitle(self):
        title = input("Enter Title: ")

        index = self.sessions.searchSessions(self.fm.cleanName(title))

        if index:
            print(f"Found {title} at index {index-1}")
            return index
        else:
            print(f"No title matching {title}")
            return False

    def yesNo(self):
        while(True):
            choice = input("Y/n:")

            if choice.lower() == "y":
                return True
            elif choice.lower() == "n":
                return False
            else:
                print("Invalid Input")

    def main(self):
        from main import chooseSite
        self.sessions.loadSessions()

        if self.sessions.sessions != None and len(self.sessions.sessions) > 0:
            choice = self.printInterface()

            if choice == 0:
                chooseSite()
            elif choice == 1:
                self.download()
            elif choice == 2:
                index = self.findByTitle()
                
                if index:
                    self.download(index - 1)
                else:
                    self.main()
            elif choice == 3:
                index = self.findByIndex()

                if index == None:
                    print("Index is None")
                    self.main()
                else:
                    self.download(index)
            elif choice == 4:
                self.setEpisodesTitle()
            elif choice == 5:
                self.getLinks()
                print("Session has been added")
                self.main()
            else:
                print("Invalid input!")
                self.main()
        else:
            self.getLinks()
            self.download()


    def findByIndex(self):
        index = None

        while True:
            try:
                index = int(input("Enter Index: "))
            except ValueError as e:
                print("ValueError")
                continue

            if len(self.sessions.sessions) >= index:
                print(f"Found session at index {index} with title {self.sessions.sessions[index].title}")
                return index
            else:
                return None

    def setTitle(self,index,title,starting_episode):

        session_to_be_change = self.sessions.sessions[index]

        url_with_title = {}

        for link in session_to_be_change.url:
            url_with_title[self.fm.cleanName(title + str(starting_episode))] = link

            starting_episode += 1

        session_to_be_change.url = url_with_title
        self.sessions.saveSessions()


    def setEpisodesTitle(self):
        print("Sometimes the title given by ytdlp doesn't say anything about the video. You can set it here")

        title = input("Enter your title: ")

        while True:
            try:
                starting_episode = int(input("Enter starting episode: "))
                break
            except ValueError as e:
                print("ValueError: please enter a number only")

        print("Please select the where to apply this title.")

        print("\t0 - Find by title")
        print("\t1 - Find by inddex")
        print("\t3 - Back")

        while True:
            try:
                choice = int(input("Option: "))
            except ValueError as e:
                print("Value error")

            if choice == 0:
                index = self.findByTitle()

                if index:
                    print(f"Set {title} as title to {self.sessions.sessions[index-1].title}?")

                    if self.yesNo():
                        self.setTitle(index-1,title,starting_episode)
                    else:
                        continue

                else: continue
            elif choice == 2:
                index = self.findByIndex()

                if index == None:
                    print("Index out of range")
                else:
                    print(f"Set {title} as title to {self.sessions.sessions[index]}?")

                    if self.yesNo():
                        self.setTitle(index,title,starting_episode)
                    else:
                        continue
            elif choice == 3:
                self.main()
            else:
                print("Invalid Input")
                    


