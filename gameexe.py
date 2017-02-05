import os

class Gameexe:
    def __init__(self):
        pass

    def load(self, lines):
        namae = {}
        for line in lines:
            line = line.strip()
            if(line[:6] == "#NAMAE"):
                params = line.split("=")[1].strip().split(",")
                params = [param.strip().strip('"') for param in params[:2]]
                namae[params[0]] = params[1]
        self.namae = namae
