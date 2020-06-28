#TO-DO
#TODO remove hit crosses

from tkinter import *
from tkinter.messagebox import *
import socket, threading

class GUI(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.started = 0
        self.shipCount = 17
        self.connected = 0
        self.hit = 0
        self.state = "enable"
        self.ships = list()
        self.grid = list()
        self.clicked = list()
        self.turn = StringVar()
        self.tcp()
        self.board()

    def tcp(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect(("192.168.1.46" , 54321))
        self.connection = "TCP"

        self.listen(self.soc)

    def board(self):
        self.pack(fill = BOTH, expand = True)

        b = Button(self)
        self.color = b.cget("background")
        b.destroy()

        frame1 = Frame(self)
        frame1.pack(fill = X)

        frame2 = Frame(self)
        frame2.pack(fill = BOTH, expand = True, padx = 5, side = LEFT, pady = 5)

        self.frame3 = Frame(self)
        self.frame3.pack(side = LEFT, fill = BOTH, expand = True)

        Label(frame1, text = "Battleship", font = "ComicSans 16 bold", fg = "white", bg = "#4267B2").pack(fill = X)

        for i in range(15):

            inner = list()
            for j in range(15):
                button = Button(frame2, height = 1, width = 3)
                button.grid(row = i, column = j)
                button.bind("<ButtonRelease-1>", lambda event, position = (i, j): self.pressed(position))
                inner.append(button)

            self.grid.append(inner)

        self.ready = Button(self.frame3, text = "Ready", command = self.start)
        self.ready.grid(row = 0, column = 0)

        Grid.rowconfigure(self.frame3, 0, weight = 1)

    def start(self):
        if self.shipCount > 0:
            showerror("Error", "You need to place all ships to start")

        else:
            self.started = 1
            self.connected += 1
            self.ready.destroy()

            if self.connected == 2:
                self.ready.destroy()
                self.turn.set("Opponent")
                self.state = "disable"
                self.turnLabel = Label(self.frame3, text = f"Turn: {self.turn.get()}, Hit: {self.hit}", fg = "OrangeRed3")
                self.turnLabel.pack(side = LEFT)
                self.disable()

            else:
                self.turn.set("You")
                showinfo("Info", "Waiting for the opponent")

            self.send_msg("ready")

    def pressed(self, position):
        if self.state == "enable":
            i, j = position[0], position[1]
            current = self.grid[i][j]

            if not self.started:

                if (i, j) not in self.ships:
                    if self.shipCount > 0:
                        self.ships.append((i, j))
                        current.configure(bg = "blue", font = "ComicSans 9", state = DISABLED)
                        self.shipCount -= 1

                else:
                    current.configure(bg = self.color, state = NORMAL)
                    self.ships.remove((i, j))
                    self.shipCount += 1

            else:
                if (i,j) not in self.clicked and self.connected == 2:
                    self.send_msg(f",{i},{j}")
                    self.clicked.append((i,j))

    def listen(self, so):
        thread = threading.Thread(target=self.receive, args=(so,))
        thread.start()

    def receive(self, so):
        while True:
            buffer = so.recv(1024).decode("utf-8")

            if buffer == "ready":
                self.connected += 1

                if self.connected == 2:
                    self.ready.destroy()
                    self.turnLabel = Label(self.frame3, text = f"Turn: {self.turn.get()}, Hit: {self.hit}", fg = "OrangeRed3")
                    self.turnLabel.pack(side = LEFT)

            elif "," in buffer:
                cond, i, j = buffer.split(",")
                button = self.grid[int(i)][int(j)]

                if cond == "":
                    if (int(i), int(j)) in self.ships:
                        button["state"] = NORMAL
                        button["bg"] = "red"
                        button["font"] = "ComicSans 9 bold"
                        button["state"] = DISABLED
                        self.hit += 1

                        self.turn.set("Opponent")
                        self.turnLabel["text"] = f"Turn: {self.turn.get()}, Hit: {self.hit}"
                        self.send_msg(f"hit, {i}, {j}")

                        if self.hit == 17:
                            self.send_msg(f"done,0,0")
                            showerror("Lost", "Unfortunately You lost :(")
                            root.destroy()

                    else:
                        self.turn.set("You")
                        self.turnLabel["text"] = f"Turn: {self.turn.get()}, Hit: {self.hit}"
                        self.send_msg(f"miss, {i}, {j}")
                        self.enable()
                        self.state = "enable"

                else:
                    if cond == "hit":
                        self.turn.set("You")
                        self.turnLabel["text"] = f"Turn: {self.turn.get()}, Hit: {self.hit}"

                        if (int(i), int(j)) not in self.ships:
                            color = "green"
                        else:
                            color = "yellow"

                        button["state"] = NORMAL
                        button["bg"] = color
                        button["state"] = DISABLED

                    elif cond == "miss":
                        self.turn.set("Opponent")
                        self.turnLabel["text"] = f"Turn: {self.turn.get()}, Hit: {self.hit}"

                        button["state"] = NORMAL
                        button["text"] = "X"
                        button["fg"] = "black"
                        button["font"] = "ComicSans 9 bold"
                        button["state"] = DISABLED
                        self.disable()
                        self.state = "disable"

                    elif "done" in cond:
                        showinfo("Win", "You won. Congratulations :)")
                        root.destroy()

                    else:
                        print(buffer)

    def send_msg(self, msg):
        self.soc.send(msg.encode("utf-8"))

    def disable(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                self.grid[i][j]["state"] = DISABLED

    def enable(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if (i, j) not in self.ships:
                    self.grid[i][j]["state"] = NORMAL

if __name__ == '__main__':
    root = Tk()
    app = GUI(root)
    root.title("Battle Ship")
    root.geometry("620x435+350+120")
    root.mainloop()
