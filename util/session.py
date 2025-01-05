import json

class Sessions:
    def __init__(self,path):
        self.path = path
        self.sessions = None

    def loadSessions(self):
        sessions = []

        try:
            with open(self.path,"r") as f:
                data = json.load(f)

            for s in data["sessions"]:
                session = SessionInfo()
                session.url = s["url"]
                session.title = s["title"]
                session.quality = s["quality"]
                session.downloadPath = s["path"]
                sessions.append(session)
        except KeyError as e:
            print("KeyError")
        except json.JSONDecodeError as e:
            print("Error decoding json")
        except FileNotFoundError as e:
            print(f"File not found at {self.path}")

        self.sessions = sessions
        return sessions

    def add(self, sessionInfo):
        self.sessions.append(sessionInfo)

    def to_dict(self):
        return {"sessions":[d.to_dict() for d in self.sessions]}

    def saveSessions(self):
        with open(self.path,"w") as f:
            json.dump(self.to_dict(),f)

    def searchSessions(self,title):
        index = 1;
        for s in self.sessions:
            if s.title != None and title.lower() in s.title.lower():
                return index

            index = index + 1

        return False

class SessionInfo:
    def __init__(self):
        self.title = None
        self.url = None
        self.quality = None
        self.downloadPath = None

    def to_dict(self):
        return {"path":self.downloadPath,
                "title":self.title,
                "url":self.url,
                "quality":self.quality
                }
