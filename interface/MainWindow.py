from tkinter import *
import tkinter.filedialog as fdialog
import textwrap
import os
from math import *
from tkinter.messagebox import showinfo




class Graph:
    def __init__(self):
        self.al = {}

    def addVertice(self,x,y):
        if any (v.intersectMe (x, y) for v in self.al.keys()):
            return None
        v = Vertice (x, y, len(self.al.keys())+1)
        self.al[v]=[]
        return v

    def getVertice(self, x, y):
        for v in self.al.keys():
            if v.isMe(x,y):
                return v
        return None

    def addEdge(self,v1,v2):
        e=Edge(v1, v2)
        self.al[v1].append(e)
        return e



class Vertice:
    radius = 25
    width=4
    color='blue'
    font='Arial 8'
    def __init__(self, x, y, number):
        self.x, self.y, self.number  =x, y, number

    def  draw(self, canvas):
        self.circle=canvas.create_oval (self.x-Vertice.radius, self.y-Vertice.radius, self.x+Vertice.radius, self.y+Vertice.radius, outline=Vertice.color, width=Vertice.width)
        self.text=canvas.create_text (self.x, self.y, font=Vertice.font, fill="black", text=str(self.number))

    def getTouchPoint(self, xt, yt):
        t=(yt-self.y)/(xt-self.x)
        a=atan(t)
        k=1
        if xt<self.x:
            k=-1
        x=k*cos(a)*Vertice.radius+self.x
        y=k*sin(a)*Vertice.radius+self.y
        return x,y

    def intersectMe(self, x, y):
        l=sqrt(pow(self.x-x, 2)+pow(self.y-y, 2))
        if l<3*Vertice.radius:
          return True
        else:
            return False

    def isMe(self, x,y):
        l = sqrt (pow (self.x - x, 2) + pow (self.y - y, 2))
        if l>Vertice.radius:
          return False
        return True

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Edge:
    width = 4
    color = 'black'
    def __init__(self, v1, v2):
        self.v1, self.v2 = v1, v2
    def  draw(self, canvas):
        x1,y1=self.v1.getTouchPoint(self.v2.x,self.v2.y)
        x2,y2=self.v2.getTouchPoint(self.v1.x, self.v1.y)
        self.line=canvas.create_line (x1, y1, x2, y2, fill=Edge.color, width=Edge.width)




class MainFrame(Frame):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.CreateMenu(root)
        self.root=root
        self.frames=self.CreateFrames()
        self.FillToolbar()
        self.FillWorkTable()
        self.AllRowColFlexible()
        #filds
        self.dragX=0
        self.dragY = 0
        self.lineDraging=None
        self.graph=Graph()


    def CreateMenu(self, root):
        #basement
        menu=Menu(root)
        #first level
        self.test_menu=testmenu=Menu(menu, tearoff=0)
        aboutmenu = Menu(menu, tearoff=0)
        #second level
        menu.add_cascade(label='Тест', menu=testmenu)
        menu.add_cascade(label='Про програму', menu=aboutmenu)
        testmenu.add_command(label='Запамʼятати граф', command=self.SaveFileMenu, state=DISABLED)
        testmenu.add_command(label='Вихід', command=root.quit)
        aboutmenu.add_command(label='Інформація', command=self.InfoDialog)
        root.config(menu=menu)


    def CreateFrames(self):
        tb = Frame(self, bd=1, relief=SUNKEN)
        tb.grid(row=0, column=0,  sticky=(N,S,E,W))
        gr = Frame(self, bd=1, relief=SUNKEN)
        gr.grid(row=0, column=1, sticky=(N,S,E,W))
        return {'toolbar' : tb, 'graph' : gr}


    def FillToolbar(self):
        path=os.path.dirname(os.path.abspath(__file__))
        self.photo1 = PhotoImage(file=os.path.join(path, "img/circle.png"))
        self.photo2 = PhotoImage (file=os.path.join(path, "img/edge.png"))
        self.photo3 = PhotoImage(file=os.path.join(path, "img/line.png"))
        self.bt1 = Button (self.frames['toolbar'], image=self.photo1, height=60, width=60, command=lambda: self.switchButtons(1))
        self.bt1.grid(column=0, row=0, sticky=(N, W, E))
        self.bt2 = Button (self.frames['toolbar'], image=self.photo2, height=60, width=60, command=lambda: self.switchButtons(2))
        self.bt2.grid (column=0, row=1, sticky=(N, W, E))
        self.bt3 = Button (self.frames['toolbar'], image=self.photo3, height=60, width=60, command=lambda: self.switchButtons(3))
        self.bt3.grid (column=0, row=2, sticky=(N, W, E))


    def FillWorkTable(self):
        self.c = Canvas (self.frames['graph'])
        self.c.grid(row=0, column=0, sticky=(N,S,W,E))
        self.c.bind('<Button-3>', self.popupMenu)


    def popupMenu(self, event):
        v=self.graph.getVertice(event.x, event.y)
        if v:
            showinfo ('Нашли!', v.number)


    def AllRowColFlexible(self, *frames):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=(N, S, W, E))
        self.grid_rowconfigure (0, weight=1)
        self.grid_columnconfigure (0, weight=0)
        self.grid_columnconfigure (1, weight=1)
        self.frames['toolbar'].grid_rowconfigure (0, weight=0)
        self.frames['toolbar'].grid_rowconfigure (1, weight=0)
        self.frames['toolbar'].grid_rowconfigure (2, weight=0)
        self.frames['graph'].grid_rowconfigure (0, weight=1)
        self.frames['graph'].grid_columnconfigure (0, weight=1)



    def SaveFileMenu(self):
        file = fdialog.asksaveasfile(filetypes=[('Txt files', '.txt')], title='Обрати файл з результатом')
        if file:
            with file:
                self.Save(file)



    def Save(self, file):
        if self.save: self.save(self, file)

    def InfoDialog(self):
        text='''
        Используйте для рисования направленного или 
        ненаправленного графа, а также для обхода его 
        вершин методом поиска "в глубину" или "ширину" 
        '''
        text=textwrap.dedent(text)  #get rid of left indent it the text
        top = Toplevel(self)        #show dialog - copied from stackoferflow
        x, y = self.root.winfo_x(), self.root.winfo_y()
        top.geometry("+{}+{}".format(x + 280, y + 120)) # put it slightly right and down from root
        top.title("Про програму...")
        Message(top, text=text, justify=LEFT, anchor=NW, width=600).grid(row=0, column=0, columnspan=2, padx=30)
        Button(top, text="Вихiд".center(14, ' '), command=top.destroy).grid(row=1, column=1, pady=10, padx=40)


    def addVertice(self, event):
        v=self.graph.addVertice(event.x, event.y)
        if v:
            v.draw(self.c)


    def dNdMode(self, switch=True):
        if switch:
            self.c.bind ("<ButtonPress-1>", self.onDragstart)
            self.c.bind ("<B1-Motion>", self.onDraging)
            self.c.bind ("<ButtonRelease-1>", self.onDropAddEdge)
        else:
            self.c.unbind ('<ButtonPress-1>')
            self.c.unbind ('<B1-Motion>')
            self.c.unbind ('<ButtonRelease-1>')

    def onDragstart(self, event):
        self.dragX=event.x
        self.dragY = event.y

    def onDraging(self, event):
        self.c.delete(self.lineDraging)
        self.lineDraging = self.c.create_line(self.dragX, self.dragY, event.x, event.y, fill='gray', width=3)

    def onDropAddEdge(self, event):
        self.c.delete (self.lineDraging)
        v1=self.graph.getVertice(self.dragX,self.dragY)
        v2=self.graph.getVertice(event.x,event.y)
        if v1 and v2:
            e=self.graph.addEdge(v1,v2)
            if e:
                e.draw(self.c)

    def switchButtons(self, n):
        if n==1:
            self.dNdMode(False)
            self.c.bind ("<Button-1>", self.addVertice)
            self.bt1.config (relief=SUNKEN)
            self.bt2.config (relief=RAISED)
            self.bt3.config (relief=RAISED)
        elif n==2:
            self.c.unbind ("<Button-1>")
            self.dNdMode()
            self.bt1.config (relief=RAISED)
            self.bt2.config (relief=SUNKEN)
            self.bt3.config (relief=RAISED)
            self.bt3.config (state="disabled")
        elif n==3:
            self.c.unbind ("<Button-1>")
            self.dNdMode()
            self.bt1.config (relief=RAISED)
            self.bt2.config (relief=RAISED)
            self.bt3.config (relief=SUNKEN)
            self.bt2.config (state="disabled")



if __name__=='__main__':
    window = Tk ()
    window.title ("Welcome to Graph creator")
    MainFrame(window)
    window.geometry('1200x800')
    window.mainloop ()




