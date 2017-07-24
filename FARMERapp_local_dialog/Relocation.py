import numpy, os, datetime
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory

#=================helper functions==============
#Conventions:
#Rotation matrices: counter clockwise rotation, looking away from the origin
#Angles: radial: Theta, azimuthal: Phi (the convention used in  mathematics textbooks, not that in quantum mechanics textbooks

def GetRotation(Angle, Axis):
    #to find the rotation matrix that can operate on column vectors
    Axis=Axis.lower()
    if Axis=='x':
        a00 = 1
        a01 = 0
        a02 = 0
        a10 = 0
        a11 = numpy.cos(Angle)
        a12 =-numpy.sin(Angle)
        a20 = 0
        a21 = numpy.sin(Angle)
        a22 = numpy.cos(Angle)
    elif Axis=='y':
        a00 = numpy.cos(Angle)
        a01 = 0
        a02 = numpy.sin(Angle)
        a10 = 0
        a11 = 1
        a12 = 0
        a20 =-numpy.sin(Angle)
        a21 = 0
        a22 = numpy.cos(Angle)
    elif Axis=='z':
        a00 = numpy.cos(Angle)
        a01 =-numpy.sin(Angle)
        a02 = 0
        a10 = numpy.sin(Angle)
        a11 = numpy.cos(Angle)
        a12 = 0
        a20 = 0
        a21 = 0
        a22 = 1
    else:
        print ('Error in running Rotation function')
        return
    return numpy.array([[a00, a01, a02], [a10, a11, a12], [a20, a21, a22]]).astype(numpy.float)

def FindRadAzi(XYZ):
    #to find the radial and azimuthal angles of a vector
    X, Y, Z = XYZ
    #Theta: radial
    Theta = numpy.arctan2(Y,X)
    #Phi: azimuthal
    Length = ((XYZ**2).sum())**0.5   
    Phi = numpy.arccos(Z/Length)
    return Theta, Phi

def MatrixOp(Operater, RowVectors):
    #to find the result of operating on row vectors
    return numpy.dot(Operater, RowVectors.transpose()).transpose()

def ToXZ(RowVec3):
    #translate and rotate 3 row vectors so that the first vector is the origin, the second is on 0z, and the third is on xz plane
    Translation = - RowVec3[0]
    New = RowVec3 + Translation

    Theta, Phi = FindRadAzi(New[1])
    Rotation0 = GetRotation(-Theta, 'z')
    Rotation1 = GetRotation(-Phi, 'y')
    New = MatrixOp(Rotation1, MatrixOp(Rotation0, New))

    Theta, Phi = FindRadAzi(New[2])
    Rotation2 = GetRotation(-Theta, 'z')
    New = MatrixOp(Rotation2, New)

    return Translation, Rotation2.dot(Rotation1).dot(Rotation0), New

def GetOutput(OriginalFile, REFIndexFile, InputFile, OutputFile, NumForm = 'standard'):
    Original = numpy.loadtxt(OriginalFile).astype(numpy.float)
    REFIndex = numpy.loadtxt(REFIndexFile).astype(numpy.int)
    Input = numpy.loadtxt(InputFile).astype(numpy.float)
    
    REF0 = Original[REFIndex]
    REF1 = Input[:]
    
    Translation0, Rotation0, New0 = ToXZ(REF0)
    Translation1, Rotation1, New1 = ToXZ(REF1)
    
    a0 = New0[1, 2]
    b0 = New0[2, 2]
    c0 = New0[2, 0]
    a1 = New1[1, 2]
    b1 = New1[2, 2]
    c1 = New1[2, 0]
    SX = c1/c0
    KZ = (a0*b1 - a1*b0)/(a1*c0)
    SZ = a1/a0
    
    ScaleShear = numpy.array([
        [SX, 0, 0],
        [0, 1, 0],
        [SZ*KZ, 0, SZ]])
    
    New = Original + Translation0
    New = MatrixOp(Rotation0, New)
    New = MatrixOp(ScaleShear, New)
    New = MatrixOp(numpy.linalg.inv(Rotation1), New)
    New = New - Translation1
    
    if NumForm == 'standard': Format = '%.5f'
    else: Format = '%.18e'
    numpy.savetxt(OutputFile, New, newline='\r\n', fmt=Format)
    
    return New

#==============================================
#use dialogs to choose
rootWin = Tk()
rootWin.title('FARMER')

StringList = ['working directory',
              'original coordinates',
              'REF indices',
              'input REF coordinates',
              'output file']

iString = 0
String0 = StringVar()
String0.set(os.getcwd())
def GetString0():
    global String0
    String0.set(askdirectory(title = StringList[0]))
Button0 = Button(rootWin, text = StringList[iString], command = GetString0)
Button0.grid(row=iString, column=0, sticky = E) 
Label0 = Label(rootWin, textvariable = String0)
Label0.grid(row=iString, column=1, sticky = W)

iString = 1
String1 = StringVar()
def GetString1():
    global String1
    String1.set(askopenfilename(initialdir=String0.get(), title = StringList[1]))
Button1 = Button(rootWin, text = StringList[iString], command = GetString1)
Button1.grid(row=iString, column=0, sticky = E) 
Label1 = Label(rootWin, textvariable = String1)
Label1.grid(row=iString, column=1, sticky = W)

iString = 2
String2 = StringVar()
def GetString2():
    global String2
    String2.set(askopenfilename(initialdir=String0.get(), title = StringList[2]))
Button2 = Button(rootWin, text = StringList[iString], command = GetString2)
Button2.grid(row=iString, column=0, sticky = E) 
Label2 = Label(rootWin, textvariable = String2)
Label2.grid(row=iString, column=1, sticky = W)

iString = 3
String3 = StringVar()
def GetString3():
    global String3
    String3.set(askopenfilename(initialdir=String0.get(), title = StringList[3]))
Button3 = Button(rootWin, text = StringList[iString], command = GetString3)
Button3.grid(row=iString, column=0, sticky = E) 
Label3 = Label(rootWin, textvariable = String3)
Label3.grid(row=iString, column=1, sticky = W)

iString = 4
String4 = StringVar()
String4.set('Output')
Entry4 = Entry(rootWin, textvariable = String4, justify = 'right')
Entry4.grid(row = iString, column=0, sticky = E)
Label4 = Label(rootWin, text = '.txt (enter output filename)')
Label4.grid(row=iString, column=1, sticky = W)

NumForm = ['standard', 'scientific']
iString = 5
String5 = StringVar()
String5.set(NumForm[0])
Option = OptionMenu(rootWin, String5, *NumForm)
Option.grid(row = iString, column = 0, sticky = E)
LabelOption = Label(rootWin, text = 'number format')
LabelOption.grid(row = iString, column = 1, sticky = W)

def DisplayArray(Array, Row0 = 0, Col0 = 2):
    Array = Array.astype(str)
    for i in range(Array.shape[0]):
        for j in range(Array.shape[1]):
            Label5 = Label(text = Array[i, j], relief = RIDGE)
            Label5.grid(row = i + Row0, column = j + Col0, sticky = NSEW)

def Calculate():
    try:
        Output = GetOutput(OriginalFile = String1.get(), 
                           REFIndexFile = String2.get(), 
                           InputFile = String3.get(), 
                           OutputFile = String0.get() + '/' + String4.get() + '.txt',
                           NumForm = String5.get())
        #DisplayArray(Output)
        TextOut = 'OK\t' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except:
        TextOut = 'error\t' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Label5 = Label(rootWin, text = TextOut)
    Label5.grid(row=6, column=1, sticky = W)
        
iString = iString + 1
ButtonCalc = Button(rootWin, text = 'calculate', command = Calculate)
ButtonCalc.grid(row=iString, column=0, sticky = E)

def Open():
    os.system('"' + String0.get() + '/' + String4.get() + '.txt' + '"')
iString = iString + 1
ButtonCalc = Button(rootWin, text = 'open output', command = Open)
ButtonCalc.grid(row=iString, column=0, sticky = E)
#Label6 = Label(rootWin, textvariable = String4)
#Label6.grid(row=iString, column=1, sticky = W)

iString = iString + 1
ButtonStop = Button(rootWin, text = 'stop', command = rootWin.quit)
ButtonStop.grid(row=iString, column=0, sticky = E)

#UpdateLabel()
rootWin.update()#_idletasks()
rootWin.mainloop()
rootWin.destroy()
