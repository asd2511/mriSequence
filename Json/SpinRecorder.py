import json

class SpinRecorder:
    def __init__(self, NRep, NEvent, event_time, flip, gradient, sz):
        """[SpinRecorder init function]

        Args:
            NRep ([int]): Number of repitation
            NEvent ([int]): Number of event per repitation
            event_time ([torch.array]): All of event time
            flip ([torch.array]): All of flip
            gradient ([torch.array]): All of gradient
            sz ([tuple]): size of the image
        """

        # init a dict structure, set param into dict
        self.file = {}
        # init 1 st level
        self.file["param"] = {  "#Rep": NRep.tolist(),
                                "#Event": NEvent.tolist(),
                                "size": sz.tolist()
                                }

        self.file["sequence"] = {}
        self.file["spin"] = {}
        # init 2 nd level
        self.file["sequence"]["flip"] = {}.fromkeys(range(NRep),{})
        self.file["sequence"]["gradient"] = {}.fromkeys(range(NRep),{})
        # init 3 nd level
        self.file["spin"]["x"] = {}.fromkeys(range(NRep),{})
        self.file["spin"]["y"] = {}.fromkeys(range(NRep),{})
        self.file["spin"]["z"] = {}.fromkeys(range(NRep),{})
        self.file["spin"]["t"] = {}.fromkeys(range(NRep),{})


        self.size = sz
        self.event_time = event_time.numpy()
        self.flip = flip.numpy()
        self.gradient = gradient.numpy()

    def addSpin(self, r, t, data):
        self.file["spin"]["x"][r][t] = data[:,0].reshape(self.size).tolist()
        self.file["spin"]["y"][r][t] = data[:,1].reshape(self.size).tolist()
        self.file["spin"]["z"][r][t] = data[:,2].reshape(self.size).tolist()
        self.file["spin"]["t"][r][t] = self.event_time[t][r].tolist()
        self.file["sequence"]["flip"][r][t] = self.flip[t][r].tolist()
        self.file["sequence"]["gradient"][r][t] = self.gradient[t].tolist()

    def printOut(self,path="..\\..\\",fileName="Sequence"):
        with open(path+fileName+".json","w") as write_f:
            json.dump(self.file,write_f,indent=4,ensure_ascii=False)















