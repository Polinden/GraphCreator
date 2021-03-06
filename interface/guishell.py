import collections
import os
import pickle
import textwrap
import time
import tkinter.filedialog as fdialog
import tkinter.messagebox as mbx
from math import *
from tkinter import *
from tkinter import simpledialog
from enum import Enum


class Graph:
    def __init__(self):
        self.al = {}
        self.bn = set()
        self.directed = None
        self._allEdges = None
        self.start = None
        self.finish = None
        self._allEdgesSimpleList = None

    def addVertice(self, canvas, x, y):
        if any(v.intersectMe(x, y) for v in self.al.keys()):
            return None
        n = len(self.al.keys()) + 1
        while n in self.bn:
            n += 1
        self.bn.add(n)
        v = Vertice(x, y, n)
        self.al[v] = []
        v.draw(canvas)

    def getVertice(self, x, y):
        for v in self.al.keys():
            if v.isMe(x, y):
                return v
        return None

    def renameVertice(self, canvas, v, nv):
        if nv in self.bn:
            return None
        self.bn.remove(v.number)
        self.bn.add(nv)
        v.changeNumber(canvas, nv)

    def addEdge(self, canvas, v1, v2):
        if self.connected(v1, v2):
            return None
        e = DirectedEdge(v1, v2) if self.directed else Edge(v1, v2)
        self.al[v1].append(e)
        self.allEdgesSimpleList.add(e)
        e.draw(canvas)

    def clean(self):
        self.al.clear()
        self.bn.clear()
        self._allEdgesSimpleList = None

    def deleteVertice(self, v, canvas):
        self.deleteEdges(v, canvas)
        v.erase(canvas)
        self.bn.remove(v.number)
        if v == self.start: self.start=None
        if v == self.finish: self.finish = None
        del self.al[v]

    def drawAllGraph(self, canvas):
        for v, el in self.al.items():
            v.draw(canvas)
            for e in el:
                e.draw(canvas)

    def deleteEdges(self, v, canvas):
        for el in self.al.values():
            for e in [e for e in el if self.testMyNeighbour(v, e)]:
                self.allEdgesSimpleList.remove(e)
                e.erase(canvas)
                el.remove(e)

    def testMyNeighbour(self, v, e):
        return (e.v2 == v and not self.directed) or e.v1 == v

    @property
    def allEdgesSimpleList(self):
        if not self._allEdges:
            self._allEdges = set(e for el in self.al.values() for e in el)
        return self._allEdges

    def connected(self, v1, v2):
        for e in self.allEdgesSimpleList:
            if self.testConnection(e, v1, v2):
                return e
        return None

    def testConnection(self, e, v1, v2):
        return e.v1 == v1 and e.v2 == v2 if self.directed else (e.v1 == v1 and e.v2 == v2) or (
                e.v1 == v2 and e.v2 == v1)

    def getClasicalAjacentLis(self):
        d = collections.defaultdict(list)
        for e in self.allEdgesSimpleList:
            d[e.v1].append(e.v2)
            if not self.directed:
                d[e.v2].append(e.v1)
        return d

    def selectStart(self, v, canvas):
        if v == self.finish:
            self.finish=None
        if self.start:
            self.start.changeColor(canvas)
        self.start = v
        self.start.changeColor(canvas, optResetColor.toStart)


    def selectFinish(self, v, canvas):
        if v == self.start:
            self.start = None
        if self.finish:
            self.finish.changeColor(canvas)
        self.finish = v
        self.finish.changeColor(canvas, optResetColor.toEnd)


    def resetColorsForAnimation(self, canvas, dontTouchStartFinish=False):
        for e in self.allEdgesSimpleList:
            e.changeColor(canvas)
        vs = filter(self.notStartFinish, self.al.keys()) if dontTouchStartFinish else self.al.keys()
        for v in vs:
            v.changeColor(canvas)


    def animatePath(self, canvas, path=None):
        if not path:
            return
        print(path)
        self.resetColorsForAnimation(canvas, dontTouchStartFinish=True)
        time.sleep(0.7)
        crs = canvas['cursor']
        canvas['cursor'] = 'watch'
        if not isinstance(path[0], tuple):
            path = [v for p in path for v in self.al.keys() if v.number == p]
            path = zip(path[:-1], path[1:])
        for e in filter(lambda x: x, (self.connected(*vt) for vt in path)):
            e.changeColor(canvas, optResetColor.toPassed)
            if self.notStartFinish(e.v1):
                e.v1.changeColor (canvas, optResetColor.toPassed)
            if self.notStartFinish (e.v2):
                e.v2.changeColor (canvas, optResetColor.toPassed)
            canvas.update()
            time.sleep (0.7)
        canvas['cursor'] = crs


    def notStartFinish(self, v):
        return not (v==self.start or v==self.finish)

    def __getstate__(self):
        self.__dict__['_allEdgesSimpleList'] = None
        return self.__dict__

    def __repr__(self):
        lb = os.linesep
        if not self.al:
            return 'None'
        s1 = '{}{}{}'.format('digraph mygraph ' if self.directed else 'graph mygraph ', '{', lb)
        s2 = (';' + lb).join([str(v) for v in self.al.keys()])
        s2 = '{}{}{}'.format(s2, ';' if s2 else '', lb)
        s3 = (';' + lb).join([str(e) for el in self.al.values() for e in el])
        s3 = '{}{}{}'.format(s3, ';' + lb if s3 else '', '}')
        return s1 + s2 + s3


class optResetColor(Enum):
    toEnd = 1
    toStart = 3
    toPassed = 4
    noOpt = 5


class Vertice:
    radius = 25
    width = 4
    color = 'blue'
    finishColor = 'green'
    startColor = 'yellow'
    passedColor = 'red'
    font = 'Arial 8'

    def __init__(self, x, y, number):
        self.x, self.y, self.number = x, y, number
        self.text, self.circle = None, None

    def draw(self, canvas):
        self.circle = canvas.create_oval(self.x - Vertice.radius, self.y - Vertice.radius, self.x + Vertice.radius,
                                         self.y + Vertice.radius, outline=Vertice.color, width=Vertice.width)
        self.text = canvas.create_text(self.x, self.y, font=Vertice.font, fill="black", text=str(self.number))

    def erase(self, canvas):
        if self.text:
            canvas.delete(self.text)
        if self.circle:
            canvas.delete(self.circle)

    def getTouchPoint(self, xt, yt):
        if xt == self.x:
            a = 1.5708 if yt > self.y else -1.5708
        else:
            t = (yt - self.y) / (xt - self.x)
            a = atan(t)
        k = 1
        if xt < self.x:
            k = -1
        x = k * cos(a) * Vertice.radius + self.x
        y = k * sin(a) * Vertice.radius + self.y
        return x, y

    def intersectMe(self, x, y):
        l = sqrt(pow(self.x - x, 2) + pow(self.y - y, 2))
        if l < 3 * Vertice.radius:
            return True
        else:
            return False

    def isMe(self, x, y):
        l = sqrt(pow(self.x - x, 2) + pow(self.y - y, 2))
        if l > Vertice.radius:
            return False
        return True

    def changeNumber(self, canvas, newNumber):
        self.number = newNumber
        canvas.itemconfig(self.text, text=newNumber)

    def changeColor(self, canvas, option=optResetColor.noOpt):
        if option==optResetColor.noOpt:
            self.color = Vertice.color
        elif option == optResetColor.toEnd:
            self.color = Vertice.finishColor
        elif option == optResetColor.toPassed:
            self.color = Vertice.passedColor
        elif option == optResetColor.toStart:
            self.color = Vertice.startColor
        canvas.itemconfig(self.circle, outline=self.color)


    def __getstate__(self):
        d = self.__dict__.copy()
        if 'text' in d:
            del d['text']
        if 'circle' in d:
            del d['circle']
        d['color'] = Vertice.color
        return d

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not other: return False          #if None!
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "{}".format(self.number)


class Edge:
    width = 4
    color = 'black'
    passedColor = 'red'

    def __init__(self, v1, v2):
        self.v1, self.v2 = v1, v2
        self.x2tp, self.y2tp = self.v2.getTouchPoint(self.v1.x, self.v1.y)
        self.x1tp, self.y1tp = self.v1.getTouchPoint(self.v2.x, self.v2.y)
        self.color = Edge.color
        self.line = None

    def draw(self, canvas):
        self.line = canvas.create_line(self.x1tp, self.y1tp, self.x2tp, self.y2tp, fill=self.color, width=Edge.width)

    def erase(self, canvas):
        if self.line:
            canvas.delete(self.line)

    def changeColor(self, canvas, option=optResetColor.noOpt):
        if option==optResetColor.noOpt:
            self.color = Edge.color
        elif option==optResetColor.toPassed:
            self.color = Edge.passedColor
        canvas.itemconfig(self.line, fill=self.color)

    def __getstate__(self):
        d = self.__dict__.copy()
        if 'line' in d:
            del d['line']
        d['color'] = Edge.color
        return d

    def __repr__(self):
        return '{}--{}'.format(self.v1, self.v2)


class DirectedEdge(Edge):
    def draw(self, canvas):
        self.line = canvas.create_line(self.x1tp, self.y1tp, self.x2tp, self.y2tp, fill=self.color, width=Edge.width,
                                       arrow=LAST)

    def __repr__(self):
        return '{}->{}'.format(self.v1, self.v2)


class MainFrame(Frame):
    menuNames = ['Граф', 'Алгоритми', 'Iнформацiя',
                 'Новий граф', 'Завантажити граф', 'Зберегти граф', 'Зберегти у форматi DOT',
                 'Вихід', 'Очистити кольори', 'В глибину', 'В ширину', 'Найкоротший шлях',
                 'Про програму','Перевірка зв`язності графа']

    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        self.createMainMenu(root)
        self.createPopUpMenu(root)
        self.frames = self.createFrames()
        self.fillToolbar()
        self.fillWorkTable()
        self.allRowColFlexible()
        # filds
        self.dragX = 0
        self.dragY = 0
        self.lineDraging = None
        self.graph = Graph()
        self.suspend = False

    def createFrames(self):
        tb = Frame(self, bd=1, relief=SUNKEN)
        tb.grid(row=0, column=0, sticky=(N, S, E, W))
        gr = Frame(self, bd=1, relief=SUNKEN)
        gr.grid(row=0, column=1, sticky=(N, S, E, W))
        return {'toolbar': tb, 'graph': gr}

    def fillToolbar(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.photo0 = PhotoImage(file=os.path.join(path, "img", "new.png"))
        self.photo1 = PhotoImage(file=os.path.join(path, "img", "circle.png"))
        self.photo2 = PhotoImage(file=os.path.join(path, "img", "edge.png"))
        self.photo3 = PhotoImage(file=os.path.join(path, "img", "line.png"))
        self.bt0 = Button(self.frames['toolbar'], image=self.photo0, height=60, width=60,
                          command=lambda: self.switchButtons(0))
        self.bt0.grid(column=0, row=0, sticky=(N, W, E))
        self.bt1 = Button(self.frames['toolbar'], image=self.photo1, height=60, width=60,
                          command=lambda: self.switchButtons(1))
        self.bt1.grid(column=0, row=1, sticky=(N, W, E))
        self.bt2 = Button(self.frames['toolbar'], image=self.photo2, height=60, width=60,
                          command=lambda: self.switchButtons(2))
        self.bt2.grid(column=0, row=2, sticky=(N, W, E))
        self.bt3 = Button(self.frames['toolbar'], image=self.photo3, height=60, width=60,
                          command=lambda: self.switchButtons(3))
        self.bt3.grid(column=0, row=3, sticky=(N, W, E))

    def fillWorkTable(self):
        self.c = Canvas(self.frames['graph'])
        self.c.grid(row=0, column=0, sticky=(N, S, W, E))
        self.c.bind('<Button-3>', self.popupMenu)
        self.c.bind('<Button-2>', self.popupMenu)

    def createPopUpMenu(self, root):
        self.popup = Menu(root, tearoff=0)
        self.popup.add_command(label="Видалити вершину", command=self.removeVrMenu)
        self.popup.add_command(label="Видалити ребра", command=self.removeEdMenu)
        self.popup.add_command(label="Перейменувати", command=self.renameVrMenu)
        self.popup.add_separator()
        self.popup.add_command(label="Початок пошуку", command=self.startVrMenu)
        self.popup.add_command(label="Кінець пошуку", command=self.finishVrMenu)

    def popupMenu(self, event):
        if self.suspend:
            return
        self.curv = self.graph.getVertice(event.x, event.y)
        if self.curv:
            self.popup.tk_popup(event.x_root, event.y_root)

    def renameVrMenu(self):
        nv = simpledialog.askinteger("Номер", "Введіть новий номер", parent=self.root, minvalue=0, maxvalue=1000)
        if nv:
            self.graph.renameVertice(self.c, self.curv, nv)

    def removeVrMenu(self):
        self.graph.deleteVertice(self.curv, self.c)

    def startVrMenu(self):
        self.graph.selectStart(self.curv, self.c)

    def finishVrMenu(self):
        self.graph.selectFinish(self.curv, self.c)

    def removeEdMenu(self):
        self.graph.deleteEdges(self.curv, self.c)

    def addVertice(self, event):
        self.graph.addVertice(self.c, event.x, event.y)

    def setDNDMode(self, switch=True):
        if switch:
            self.c.bind("<ButtonPress-1>", self.onDragstart)
            self.c.bind("<B1-Motion>", self.onDraging)
            self.c.bind("<ButtonRelease-1>", self.onDropAddEdge)
        else:
            self.c.unbind('<ButtonPress-1>')
            self.c.unbind('<B1-Motion>')
            self.c.unbind('<ButtonRelease-1>')

    def onDragstart(self, event):
        if self.suspend:
            return
        self.dragX = event.x
        self.dragY = event.y

    def onDraging(self, event):
        if self.suspend:
            return
        self.c.delete(self.lineDraging)
        self.lineDraging = self.c.create_line(self.dragX, self.dragY, event.x, event.y, fill='gray', width=3)

    def onDropAddEdge(self, event):
        if self.suspend:
            return
        self.c.delete(self.lineDraging)
        v1 = self.graph.getVertice(self.dragX, self.dragY)
        v2 = self.graph.getVertice(event.x, event.y)
        if v1 and v2: self.graph.addEdge(self.c, v1, v2)

    def switchButtons(self, n):
        if n == 1:
            self.setDNDMode(False)
            self.c.bind("<Button-1>", self.addVertice)
            self.bt1.config(relief=SUNKEN)
            self.bt2.config(relief=RAISED)
            self.bt3.config(relief=RAISED)
            self.c['cursor'] = 'cross'
        elif n == 2:
            self.c.unbind("<Button-1>")
            self.c['cursor'] = 'arrow'
            self.setDNDMode()
            self.bt1.config(relief=RAISED)
            self.bt2.config(relief=SUNKEN)
            self.bt3.config(relief=RAISED)
            self.bt3.config(state="disabled")
            self.graph.directed = True
        elif n == 3:
            self.c.unbind("<Button-1>")
            self.c['cursor'] = 'arrow'
            self.setDNDMode()
            self.bt1.config(relief=RAISED)
            self.bt2.config(relief=RAISED)
            self.bt3.config(relief=SUNKEN)
            self.bt2.config(state="disabled")
            self.graph.directed = False
        elif n == 0:
            self.c.unbind("<Button-1>")
            self.setDNDMode(False)
            self.bt1.config(relief=RAISED)
            self.bt2.config(relief=RAISED)
            self.bt3.config(relief=RAISED)
            self.bt2.config(state="normal")
            self.bt3.config(state="normal")
            self.c['cursor'] = 'cross'
            self.c.delete('all')
            self.graph.clean()

    def createMainMenu(self, root):
        # basement
        self.menu = Menu(root)
        # first level
        graphmenu = Menu(self.menu, tearoff=0)
        aboutmenu = Menu(self.menu, tearoff=0)
        algmenu = Menu(self.menu, tearoff=0)
        # second level
        self.menu.add_cascade(label=MainFrame.menuNames[0], menu=graphmenu)
        self.menu.add_cascade(label=MainFrame.menuNames[1], menu=algmenu)
        self.menu.add_cascade(label=MainFrame.menuNames[2], menu=aboutmenu)
        graphmenu.add_command(label=MainFrame.menuNames[3], command=self.clearGraphMenu)
        graphmenu.add_command(label=MainFrame.menuNames[4], command=self.openFileMenu)
        graphmenu.add_separator()
        graphmenu.add_command(label=MainFrame.menuNames[5], command=self.saveFileMenu)
        graphmenu.add_command(label=MainFrame.menuNames[6], command=self.saveDOTMenu)
        graphmenu.add_separator()
        graphmenu.add_command(label=MainFrame.menuNames[7], command=root.quit)
        algmenu.add_command(label=MainFrame.menuNames[8], command=self.onResetColors)
        algmenu.add_command(label=MainFrame.menuNames[9], command=self.onDFS)
        algmenu.add_command(label=MainFrame.menuNames[10], command=self.onBFS)
        algmenu.add_command(label=MainFrame.menuNames[11], command=self.onSPS)
        algmenu.add_command (label=MainFrame.menuNames[13], command=self.onCNT)
        aboutmenu.add_command(label=MainFrame.menuNames[12], command=self.onInfoDialog)
        root.config(menu=self.menu)

    def clearGraphMenu(self):
        self.switchButtons(0)

    def saveFileMenu(self, file=None):
        try:
            file = fdialog.asksaveasfile(mode='wb', defaultextension='.gra', filetypes=[('Graph files', '.gra')],
                                         title='Обрати файл')
            if file:
                self.graph.resetColorsForAnimation(self.c)
                pickle.dump(self.graph, file)
        except Exception as e:
            print(e)
            if file:
                file.close()
            mbx.showerror("Увага!", "Помилка збереження графу")

    def saveDOTMenu(self, file=None):
        try:
            file = fdialog.asksaveasfile(mode='wt', defaultextension='.txt', filetypes=[('Txt files', '.txt')],
                                         title='Обрати файл')
            if file:
                file.write('{}'.format(self.graph))
        except Exception as e:
            print(e)
            if file:
                file.close()
            mbx.showerror("Увага!", "Помилка збереження графу")

    def openFileMenu(self, file=None):
        try:
            file = fdialog.askopenfile(mode='rb', defaultextension='.gra',
                                       filetypes=[('Graph files', '.gra'), ('All files', '.*')], title='Обрати файл')
            if file:
                self.graph = pickle.load(file)
                self.c.delete('all')
                self.graph.drawAllGraph(self.c)
                self.switchButtons(2 if self.graph.directed else 3)
        except Exception as e:
            print(e)
            if file:
                file.close()
            mbx.showerror("Увага!", "Помилка завантаження графу")

    def onBFS(self):
        if hasattr(self, 'lst1'):
            if not self.graph.start:
                mbx.showerror('Де шукати?', 'Оберіть початок пошуку')
                return
            path = self.lst1(self.graph.getClasicalAjacentLis(), self.graph.start)
            if path:
                self.animateFoundPath(path)

    def onDFS(self):
        if hasattr(self, 'lst2'):
            if not self.graph.start:
                mbx.showerror('Де шукати?', 'Оберіть початок пошуку')
                return
            path = self.lst2(self.graph.getClasicalAjacentLis(), self.graph.start)
            if path:
                self.animateFoundPath(path)

    def onSPS(self):
        if hasattr(self, 'lst3'):
            if not self.graph.start:
                mbx.showerror('Де шукати?', 'Оберіть початок пошуку')
                return
            if not self.graph.finish:
                mbx.showerror('Де шукати?', 'Оберіть кiнець пошуку')
                return
            path = self.lst3(self.graph.getClasicalAjacentLis(), self.graph.start, self.graph.finish)
            if path:
                self.animateFoundPath(path)


    def onCNT(self):
        if hasattr(self, 'lst4'):
            if self.graph.directed:
                mbx.showinfo ('В роботi..', 'Алгоритм Косарайю не реализовано!')
                return
            vs = self.graph.al.keys()
            if not vs:
                return
            cal = self.graph.getClasicalAjacentLis()
            if len(vs) != len(cal.keys()):
                mbx.showinfo ('Результат', 'Цей граф є незв`язним')
                return
            res = self.lst4(cal, next(iter(vs)))
            mbx.showinfo('Результат', 'Цей граф є зв`язним' if res else 'Цей граф є незв`язним')


    def animateFoundPath(self, path):
        self.stopTheWorld()
        self.graph.animatePath(self.c, path)
        self.stopTheWorld(True)

    def stopTheWorld(self, enable=False):
        self.suspend = not enable
        for w in {self.bt0, self.bt1, self.bt2, self.bt3} - {self.bt3 if self.graph.directed else self.bt2}:
            w.configure(state="disabled" if not enable else 'normal')
        for m in MainFrame.menuNames[:3]:
            self.menu.entryconfig(m, state="disabled" if not enable else 'normal')

    def onResetColors(self):
        self.graph.start=None
        self.graph.finish=None
        self.graph.resetColorsForAnimation(self.c)

    def allRowColFlexible(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=(N, S, W, E))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.frames['toolbar'].grid_rowconfigure(0, weight=0)
        self.frames['toolbar'].grid_rowconfigure(1, weight=0)
        self.frames['toolbar'].grid_rowconfigure(2, weight=0)
        self.frames['graph'].grid_rowconfigure(0, weight=1)
        self.frames['graph'].grid_columnconfigure(0, weight=1)

    def onInfoDialog(self):
        text = '''
			Используйте для рисования направленного или 
			ненаправленного графа, а также для обхода его 
			вершин методом поиска "в глубину" или "ширину" 
			'''
        text = textwrap.dedent(text)  # get rid of left indent it the text
        top = Toplevel(self)  # show dialog - copied from stackoferflow
        x, y = self.root.winfo_x(), self.root.winfo_y()
        top.geometry("+{}+{}".format(x + 280, y + 120))  # put it slightly right and down from root
        top.title("Про програму...")
        Message(top, text=text, justify=LEFT, anchor=NW, width=600).grid(row=0, column=0, columnspan=2, padx=30)
        Button(top, text="Вихiд".center(14, ' '), command=top.destroy).grid(row=1, column=1, pady=10, padx=40)


def startGUI(lst1=None, lst2=None, lst3=None, lst4=None):
    window = Tk()
    window.title("Дослiдник Графiв")
    mf = MainFrame(window)
    mf.lst1, mf.lst2, mf.lst3, mf.lst4 = lst1, lst2, lst3, lst4
    window.geometry('1200x800')
    window.mainloop()


if __name__ == '__main__':
    window = Tk()
    window.title("Дослiдник Графiв")
    MainFrame(window)
    window.geometry('1200x800')
    window.mainloop()
