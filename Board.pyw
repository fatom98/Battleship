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
        self.clicked = list()
        self.grid = list()
        self.tcp()
        self.board()

    def tcp(self):

        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect(("127.0.0.1" , 54321))
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

        frame3 = Frame(self)
        frame3.pack(side = LEFT, fill = BOTH, expand = True)

        Label(frame1, text = "Battle Ship", font = "ComicSans 16 bold", fg = "white", bg = "#4267B2").pack(fill = X)

        for i in range(10):

            inner = list()
            for j in range(10):
                button = Button(frame2, height = 1, width = 3)
                button.grid(row = i, column = j)
                button.bind("<ButtonRelease-1>", lambda event, position = (i, j): self.pressed(position))
                inner.append(button)

            self.grid.append(inner)

        self.ready = Button(frame3, text = "Ready", command = self.start)
        self.ready.grid(row = 0, column = 0)

        Grid.rowconfigure(frame3, 0, weight = 1)

    def pressed(self, position):
        i, j = position[0], position[1]
        current = self.grid[i][j]

        if not self.started:

            if (i, j) not in self.clicked:
                if self.shipCount > 0:
                    self.clicked.append((i, j))
                    current.configure(bg="blue", state = DISABLED)
                    self.shipCount -= 1

            else:
                current.configure(bg = self.color, state = NORMAL)
                self.clicked.remove((i, j))
                self.shipCount += 1

        else:
            self.send_msg(f",{i},{j}")


    def start(self):

        if self.shipCount > 0:
            showerror("Error", "You need to place all ships to start")
        else:
            self.started = 1
            self.connected += 1

            if self.connected == 2:
                self.ready.destroy()
                root.geometry("350x300+350+150")

            else:
                showinfo("Info", "Waiting for the opponent")

            self.send_msg("ready")


    def listen(self, so):
        thread = threading.Thread(target=self.receive, args=(so,))
        thread.start()

    def receive(self, so):

        while True:
            buffer = so.recv(1024).decode("utf-8")
            print(buffer)

            if buffer == "ready":
                self.connected += 1

                if self.connected == 2:
                    self.ready.destroy()
                    root.geometry("320x300+350+150")

            elif "," in buffer:
                cond, i, j = buffer.split(",")
                try:
                    button = self.grid[int(i)][int(j)]
                except ValueError:
                    button = i = j = 0

                if cond == "":
                    if (int(i), int(j)) in self.clicked:
                        button["state"] = NORMAL
                        button["bg"] = "yellow"
                        button["state"] = DISABLED
                        self.hit += 1

                        if self.hit == 17:
                            showerror("Lost", "Unfortunately You lost :(")
                            self.send_msg(f"done,,")
                            root.destroy()
                        else:
                            self.send_msg(f"hit, {i}, {j}")

                    else:
                        self.send_msg(f"miss, {i}, {j}")

                else:
                    if cond == "hit":
                        button["state"] = NORMAL
                        button["bg"] = "green"
                        button["state"] = DISABLED
                    elif cond == "miss":
                        button["state"] = NORMAL
                        button["bg"] = "red"
                        button["state"] = DISABLED

                    else:
                        showinfo("Win", "You won. Congratulations :)")
                        root.destroy()

    def send_msg(self, msg):
        self.soc.send(msg.encode("utf-8"))

if __name__ == '__main__':
    root = Tk()
    app = GUI(root)
    root.title("Battle Ship")
    root.geometry("400x300+350+150")
    root.mainloop()