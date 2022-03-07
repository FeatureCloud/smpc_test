import numpy as np
from FeatureCloud.engine.app import app, app_state, AppState, Role, SMPCOperation
from FeatureCloud.api.http_ctrl import api_server
from FeatureCloud.api.http_web import web_server
from bottle import Bottle

SMPC = False


@app_state('initial', Role.BOTH)
class Client(AppState):
    def register(self):
        self.register_transition('Aggregation', Role.COORDINATOR)
        self.register_transition('terminal', Role.PARTICIPANT)

    def run(self) -> str or None:
        x = np.random.rand(50, 10)
        y = np.random.rand(40, 9)
        z = np.random.rand(30, 6)
        if SMPC:
            x = x.tolist()
            y = y.tolist()
            z = z.tolist()
        # self.send_data_to_coordinator(data=[x, y, z], use_smpc=SMPC)
        self.send_back_to_back(x, y, z, smpc_use=SMPC)
        if self.is_coordinator:
            return 'Aggregation'
        return 'terminal'

    def send_back_to_back(self, x, y, z, smpc_use=False):
        self.send_data_to_coordinator(data=x, use_smpc=smpc_use)
        self.send_data_to_coordinator(data=y, use_smpc=smpc_use)
        self.send_data_to_coordinator(data=z, use_smpc=smpc_use)


@app_state('Aggregation', Role.COORDINATOR)
class Aggregation(AppState):
    def register(self):
        self.register_transition('terminal', Role.COORDINATOR)

    def run(self) -> str or None:
        # x, y, z = self.aggregate_data(SMPCOperation.ADD, use_smpc=SMPC)
        x, y, z = self.aggregate_separate(smpc_use=SMPC)

        np.save("/mnt/output/x.npy", x)
        np.save("/mnt/output/y.npy", y)
        np.save("/mnt/output/z.npy", z)

        return 'terminal'

    def aggregate_separate(self, smpc_use):
        x = self.aggregate_data(SMPCOperation.ADD, use_smpc=smpc_use)
        print(np.shape(x))
        y = self.aggregate_data(SMPCOperation.ADD, use_smpc=smpc_use)
        print(np.shape(y))
        z = self.aggregate_data(SMPCOperation.ADD, use_smpc=smpc_use)
        print(np.shape(z))
        return x,y,z



def run(host='localhost', port=5000):
    """ run the docker container on specific host and port.

    Parameters
    ----------
    host: str
    port: int

    """

    app.register()
    server = Bottle()
    server.mount('/api', api_server)
    server.mount('/web', web_server)
    server.run(host=host, port=port)


if __name__ == '__main__':
    run()
