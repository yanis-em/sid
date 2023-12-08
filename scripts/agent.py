__author__ = "Aybuke Ozturk Suri, Johvany Gustave"
__copyright__ = "Copyright 2023, IN512, IPSA 2023"
__credits__ = ["Aybuke Ozturk Suri", "Johvany Gustave"]
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

from network import Network
from my_constants import *
import heapq
import time



from threading import Thread
import numpy as np


class Agent:
    """ Class that implements the behaviour of each agent based on their perception and communication with other agents """
    def __init__(self, server_ip):
        #TODO: DEINE YOUR ATTRIBUTES HERE
        self.owner = 99
        #DO NOT TOUCH THE FOLLOWING INSTRUCTIONS
        self.network = Network(server_ip=server_ip)
        self.agent_id = self.network.id
        self.running = True
        self.network.send({"header": GET_DATA})
        env_conf = self.network.receive()
        self.x, self.y = env_conf["x"], env_conf["y"]   #initial agent position
        self.w, self.h = env_conf["w"], env_conf["h"]   #environment dimensions
        cell_val = env_conf["cell_val"] #value of the cell the agent is located in
        Thread(target=self.msg_cb, daemon=True).start()
        

    def msg_cb(self): 
        """ Method used to handle incoming messages """
        while self.running:
            msg = self.network.receive()
            self.handle_message(msg)
            

    def handle_message(self, msg):
        """ Handle incoming messages based on their headers """
        print(msg)
        # TODO: Implement logic to handle different message headers
        if msg["header"] == MOVE:
              self.update_position(msg["x"],msg["y"])

        elif msg["header"]== GET_ITEM_OWNER:
            self.owner = msg["owner"]

        if msg["header"] == BROADCAST_MSG:
            if msg["Msg type"] == KEY_DISCOVERED:
                if msg["owner"] == self.agent_id:
                    grid = np.zeros((self.h, self.w))
                    path = self.astar(grid,msg["position"])
                    print(path)
                    cmds = {"header":MOVE}                 
                    for moves in path:
                        cmds["direction"]= moves
                        self.network.send(cmds)
                        msg = self.network.receive()
                        self.handle_message(msg)  
                        time.sleep(1) 
                        




    def heuristic(self,pos_r,pos_e):
    # Fonction heuristique (distance euclidienne)
        return ((pos_r[0] - pos_e[0]) ** 2 + (pos_r[1]  - pos_e[1]) ** 2) ** 0.5

    def astar(self,grid, end):
        start = (self.x,self.y)
        rows, cols = len(grid), len(grid[0])
        directions = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

        open_set = []
        heapq.heappush(open_set, (0, start, []))  # (f, position, path)

        closed_set = set()

        while open_set:
            current_f, current_position, current_path = heapq.heappop(open_set)

            if current_position == end:
                move_dire=[]
                for moves in current_path:
                    for dire in range(len(directions)):
                        if moves==directions[dire]:
                            move_dire.append(dire)
                            
                return move_dire

            if current_position in closed_set:
                continue

            closed_set.add(current_position)

            for dx, dy in directions:
                new_x, new_y = current_position[0] + dx, current_position[1] + dy

                if 0 <= new_x < rows and 0 <= new_y < cols:
                    new_position = (new_x, new_y)
                    new_g = len(current_path) + 1
                    new_h = self.heuristic(new_position, end)
                    new_f = new_g + new_h

                    heapq.heappush(open_set, (new_f, new_position, current_path + [(dx, dy)]))

        return None

    def update_position(self,x,y):
        self.x=x
        self.y=y
  
                        
    
        


if __name__ == "__main__":
    from random import randint
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--server_ip", help="Ip address of the server", type=str, default="localhost")
    args = parser.parse_args()

    agent = Agent(args.server_ip)
    try:    #Manual control test
        while True:
            cmds = {"header": int(input("0 <-> Broadcast msg\n1 <-> Get data\n2 <-> Move\n3 <-> Get nb connected agents\n4 <-> Get nb agents\n5 <-> Get item owner\n"))}
            if cmds["header"] == BROADCAST_MSG:
                cmds["Msg type"] = int(input("0 <-> Send Position \n1 <-> Key discovered\n2 <-> Box discovered\n3 <-> Completed\n"))
                cmds["position"] = (agent.x, agent.y)
                cmds["owner"] = agent.owner # TODO: specify the owner of the item
            elif cmds["header"] == MOVE:
                cmds["direction"] = int(input("0 <-> Stand\n1 <-> Left\n2 <-> Right\n3 <-> Up\n4 <-> Down\n5 <-> UL\n6 <-> UR\n7 <-> DL\n8 <-> DR\n"))
            agent.network.send(cmds)
    except KeyboardInterrupt:
        pass




