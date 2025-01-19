import os
import random
import copy
import math
from itertools import groupby
import time
import keyboard
import asyncio

continuous = lambda x,y: list(range(x,x+y)) #:: Int -> Int -> [Int]
intersect = lambda x,y: list(set(x) & set(y)) #:: [Int] -> [Int] -> [Int]

class State:
    def __init__(self, turn, char):
        self.turn = turn
        self.char = char

    def applicate(self):
        pass
        

class Creature:
    def __init__(self, name = "unnamed", lvl = 0, hp = [10,10], str = [2,2], arm = [0,0], int = 5, spd = [5, 5], len = 1, cnd = [], pos = [0,0]):
        self.name = name
        self.lvl = lvl
        self.hp = hp #体力[現在の体力,最大体力]
        self.str = str #筋力[現在の筋力,最大筋力]
        self.arm = arm #防御[現在の防御,最大防御]
        self.int = int #知力（固定）=> 会心
        self.spd = spd #速度 => 回避
        self.len = len #射程
        self.cnd = cnd #状態異常（バフ、デバフ）
        self.pos = pos #[Int]
        self.turn = 1

    def display(self):
        print(f"{self.name} | hp:{self.hp[0]}/{self.hp[1]} | str:{self.str[0]}/{self.str[1]} | arm:{self.arm[0]}/{self.arm[1]} | int:{self.int} | spd:{self.spd[0]}/{self.spd[1]} | len:{self.len} | cnd:{[c.name for c in self.cnd]}")

    def action(self, floor):
        pass
        # if self.hp <= 0:
        #     return
        
        # for c in self.cnd:
        #     c.applicate()

        # self.display()
        # e = keyboard.read_event()
        # while(e.event_type == keyboard.KEY_UP):
        #     e = keyboard.read_event()

        # print(e.name)

    def move(self, dx, dy):
        self.pos[0] += dx
        self.pos[1] += dy

    def attack(self, tar = []):
        for t in tar:
            int = min(0, self,int - t.int) #::Int
            critical = random.choice[range(1,101)] #::Int
            damage = max(0,self.str[0] - t.arm[0]) # :: Int
            if(critical <= int) : damage = max(damage, math.floor(t.hp[1]/2))
            t.hp[0] -= damage
            if(t.hp <= 0): print(f"{t.name}was dead")

class Player(Creature):
    def __init__(self, name):
        super().__init__("@"+name)
        self.san = 100
        self.point = 0
        self.storage = []

    def display(self):
        print(f"{self.name[1:]} | hp:{self.hp[0]}/{self.hp[1]} | str:{self.str[0]}/{self.str[1]} | arm:{self.arm[0]}/{self.arm[1]} | int:{self.int} | spd:{self.spd[0]}/{self.spd[1]} | len:{self.len} | cnd:{[c.name for c in self.cnd]} | san:{self.san}")  

    async def action(self, floor):
        # loop = asyncio.get_event_loop()
        # print("Enter something: ")
        # # 非同期でブロッキングなinput()を実行
        # user_input = await loop.run_in_executor(None, input)
        # print(f"You entered: {user_input}")

        e = keyboard.read_event()
        while(e.event_type == keyboard.KEY_UP):
            e = keyboard.read_event()

        past = copy.deepcopy(self.pos)
        key = e.name
        match(key):
            case "left": self.pos[0]-=1
            case "right": self.pos[0]+=1
            case "up": self.pos[1]-=1
            case "down": self.pos[1]+=1

        char = floor.field[self.pos[1]][self.pos[0]]
        if(not char in [".", "+", "#", "%"]):
            print("hit")
            self.pos = past
            # self.action(floor)

        return key

class Enemy(Creature):
    def __init__(self, name, lvl, len = 1):
        super().__init__(self, name)
        self.hasTargerted = False #プレイヤーにターゲットしているか。
        self.isLoaded = False #ロード済みか

        self.len = len
        self.lvl = lvl


    def enhance(self, adv = []):
         for i in range(self.lvl):
            s = random.choice(adv)   
            match s:
                case "hp" : 
                    for i in range(2) : self.hp[i] += 2
                case "str" : 
                    for i in range(2) : self.str[i] += 2
                case "arm" : 
                    for i in range(2) : self.arm[i] += 2
                case "int" : self.int += 2
                case "spd" : 
                    for i in range(2) : self.spd[i] += 2 

class Kestrel(Enemy):
    def __init__(self, lvl = 0):
        super().__init__("Kestrel", lvl, 1)
        super().enhance(["hp","spd"])

class Room: 
    def __init__(self, id,pos = (1,1), size = (10,5)):
        self.id = id #:: Int
        self.position = pos #:: (Int, Int)
        self.size = size #:: (Int, Int)
        #self.connection = None #:: [Room] //degfault is None, this will be [Room] after do connect 
        self.connection = None #//degfault is None, this will be [(Room, Int, [Int])] after do connect. This touple is (Room, Direction, Range)

    def range(self,op=0):
        return continuous(self.position[op],self.size[op]) #::[Int]

    def connect(self, room): #//接続可能な部屋を総て取得する
        if not self.connection == None:
            return self.connection
        
        self.connection = [] #:: [Room]
        temp = [] #[(Room, Int, Int, Int)] //Room, Distance, Direction(i), Position(j)
        room = list(filter(lambda r: not r == self, room)) #:: [Room]
        for i in [0,1]:
            #candidate = list(filter(lambda r: len(intersect(r.range(i),self.range(i))) != 0,room)) #:: [Room]
            #print(self.range(i))
            for j in self.range(i):
                candidate = list(filter(lambda r: j in r.range(i),room)) #:: [Room]
                dif = list(map(lambda r: (r, r.position[(i+1)%2] - self.position[(i+1)%2]),candidate)) #:: [(Room, Int)]
                upper = list(map(lambda x: (x[0], x[1] - self.size[(i+1)%2]), list(filter(lambda x: x[1] > 0,dif)))) #:: [(Room, Int)]
                lower = list(map(lambda x: (x[0], x[1] + x[0].size[(i+1)%2]), (list(filter(lambda x: x[1] < 0,dif))))) #:: [(Room, Int)]
                if len(upper) > 0:
                    n = min(upper, key = lambda x: x[1])
                    #if not n in temp:
                    temp.append((n[0], n[1], int(not i), j)) #:: [(Room, Int, Int, Int)]
                if len(lower) > 0:
                    n = max(lower, key = lambda x: x[1])
                    #if not n in temp:
                    temp.append((n[0], n[1], int(not i), j)) #:: [(Room, Int, Int, Int)]

        #temp = list(map(lambda x: (x[0],abs(x[1])),temp)) #:: [(Room, Int)]
        temp = sorted(temp, key = lambda x: abs(x[1])) #:: [(Room, Int, Int, Int)]
        temp = sorted(temp, key = lambda x: x[0].id) #:: [(Room, Int, Int, Int)]
        temp = [list(group) for key, group in groupby(temp, key=lambda x: x[0].id)] #:: [[(Room, Int, Int, Int)]]
        temp = list(map(lambda a: (a[0][0], a[0][1], a[0][2], list([e[3] for e in a[1:-1]])), temp)) #:: [(Room, Int, Int, [Int])]
        temp = list(filter(lambda x: len(x[3]) > 0, temp)) #:: [(Room, Int, Int, [Int])]
        temp = sorted(temp, key=lambda a: -1*len(a[3])) #:: [(Room, Int, Int, [Int])] //room, distance, direction, range[]
        #temp = list(map(lambda x: x[0],temp)) #:: [Room]
        self.connection += temp

        return self.connection

    def road(self, rooms, end, passed = []):
        rest = list(filter(lambda r: not r == self, rooms)) #:: [Room]
        rest = list(filter(lambda r: not r in passed, rest)) #:: [Room]
        candidate = self.connect(rooms) #:: [(Room, Int, Int, [Int])]
        candidate = list(map(lambda x: x[0], candidate)) #:: [Room]
        candidate = list(filter(lambda r: not r in passed, candidate)) #:: [Room]
        if len(candidate) == 0:
            return False
        if candidate == [end]:
            if len(rest) == 1:
                return [self,end]
            else:
                return False  

        candidate = list(filter(lambda r: not r == end, candidate)) #:: [Room]  
        for c in candidate:
            road = c.road(rooms,end,passed + [self]) #:: [Room]
            if not road == False:
                return [self] + road 
        
        return False

class Floor:
    def __init__(self, player, size = (100,50),numRooms = 8):
        #self.field = "" #:: String
        self.size = size #:: (Int, Int)
        self.rooms = [] #:: [Room]
        self.field = [[" " for x in range(self.size[0])] for y in range(self.size[1])] #:: [[Char]]
        self.road = [] #::[(Int, Int)] 
        self.char = [] #::[Creature]

        self.sector = [[0,0]+list(size)] #:: [[Int, Int, Int, Int]] //ix iy sx sy
        for i in range(numRooms-1):
            index = max(range(len(self.sector)), key=lambda x: self.sector[x][2]*self.sector[x][3]) #:: Int
            sector = self.sector[index] #:: [Int, Int, Int, Int]
            axis = 0 #:: Int
            if sector[2] == sector[3]*2:
                axis = math.floor(random.random()*2) #:: Int
            else:
                temp = [sector[2],sector[3]*2] #:: [Int, Int]
                axis = max(range(2), key = lambda x: temp[x]) #:: Int

            split = math.floor(random.uniform(0.4,0.6)*sector[axis+2]) #:: Int
            newSector = copy.deepcopy(sector) #:: [Int, Int, Int, Int]
            newSector[axis] += split #:: Int
            newSector[axis+2] -= split #:: Int
            self.sector.append(newSector)
            sector[axis+2] = split #:: Int

        for s in self.sector:
            sx = int(random.uniform(0.7,0.9)*s[2]) #:: Int
            sy = int(random.uniform(0.7,0.9)*s[3]) #:: Int
            ix = int(random.random()*(s[2]-sx)) #:: Int
            iy = int(random.random()*(s[3]-sy)) #:: Int
            self.rooms.append(Room(chr(len(self.rooms) + 97),(s[0]+ix,s[1]+iy),(sx,sy)))

        sr = min(self.rooms, key = lambda r: r.position[0] + self.size[1] - (r.position[1]+r.size[1])) #:: Room
        #er = min(self.rooms, key = lambda r: self.size[0] - (r.position[0] + r.size[0]) + r.position[1]) #:: Room
        er = min(sr.connect(self.rooms), key = lambda x: abs(x[1])*2 if x[2] == 1 else abs(x[1]))[0]
        #print(e.id)
        #print(sr.id, er.id)
        # print(er.near(filter(lambda r: r.id != er.id, self.rooms),3).id)

        self.ent = [random.choice(sr.range(0)[1:-1]),random.choice(sr.range(1)[1:-1])] #::[Int]
        self.ext = [random.choice(er.range(0)[1:-1]),random.choice(er.range(1)[1:-1])] #::[Int]

        player.pos = self.ent
        self.char.append(player)

        roads = sr.road(self.rooms,er) #:: [Room]
        #print(road)
        if not roads:
            print("no road")
        else :
            for i in range(len(roads)):
                #print(roads[i].id, end=" ")
                continue

            #print()

        for r in self.rooms:
            con = r.connect(self.rooms)
            con = list(map(lambda x: (x[0].id, x[1], x[2], x[3]), con))
            #print(r.id, con)

        #make road
        if(not roads) : return
        for i in range(len(roads) - 1):
            road = []
            r = roads[i] #::Room
            to = roads[i+1] #::Room
            con = r.connect(self.rooms)
            con = list(filter(lambda e: e[0] == to, con))[0] #::Room
            dir = con[2] #::Int
            dis = con[1] #::Int
            start = list(r.position) #::[Int,Int]
            start[not dir] = random.choice(con[3])
            arr = None
            if dis > 0:
                start[dir] += r.size[dir] - 1
                arr = list(range(dis+2))
            else :
                start[dir] += 0
                arr = list(map(lambda e: e*-1 ,(list(range(abs(dis) + 2)))))

            #print(arr)
            for i in arr:
                temp = copy.deepcopy(start)
                temp[dir] += i
                #print(temp)
                road.append(temp)

            #print(road)
            self.road.append(road)

        #print(self.road)
            
 
    def display(self):
        os.system('cls')

        for r in self.rooms:
            for y in range(r.size[1]):
                for x in range(r.size[0]):
                    # if any(map(lambda e: e == [r.position[0] + x,r.position[1] + y], self.road)):
                    #     self.field[r.position[1] + y][r.position[0] + x] = "+"
                    #     continue

                    if y == 0 or y == r.size[1] - 1:
                        self.field[r.position[1] + y][r.position[0] + x] = "T" if x == 0 or x == r.size[0] - 1 else "-" #:: Char
                    elif x == 0 or x == r.size[0] - 1:
                        self.field[r.position[1] + y][r.position[0] + x] = "|" #:: Char
                    else:
                        self.field[r.position[1] + y][r.position[0] + x] = "." #:: Char
                        #self.field[r.position[1] + y][r.position[0] + x] = r.id

        for r in self.road:
            for e in [r[0], r[-1]]:
                self.field[e[1]][e[0]] = "+"

            for e in r[1:-1]:
                self.field[e[1]][e[0]] = "#"

        for d in [self.ext]:
            self.field[d[1]][d[0]] = "%"

        for c in self.char:
            pos = c.pos
            self.field[pos[1]][pos[0]] = c.name[0]

        for y in range(self.size[1]):
            for x in range(self.size[0]):
                print(self.field[y][x], end="")
            print()

class System:
    def __init__(self, player, flrNum):
        self.field = [] #::[String]
        self.floor = Floor(player) #::Floor
        self.order = [] #::[Creature]
        self.player = player #::Player
        self.floor.display()
        self.player.display()

        asyncio.run(self.main_loop())

    async def main_loop(self):
        # while (not tuple(self.player.pos) == tuple(self.floor.ext)) :
        #     for c in self.order:
        #         res =  await c.action()
        #         #await asyncio.sleep(0.5)

        while (not tuple(self.player.pos) == tuple(self.floor.ext)) :
            res = await self.player.action(self.floor)

            self.floor.display()
            print(res)
                


class Main:
    def __init__(self):
        name = ""
        while(name.strip() == ""):
            name = input("the name of missing person is ")
        
        name = name.replace(" ", "")
        self.player = Player(name)
        self.floor = 1

        while self.player.hp[0] > 0:
            System(self.player, self.floor)
            
            
helix = Main()
# flr = Floor()
# flr.display()