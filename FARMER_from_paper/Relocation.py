import numpy

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
        print 'Error in running Rotation function'
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
#==============================================

#list of coordinates of REFs and ROIs, row vectors, space delimited
OriginalFile = 'Original.txt'

#list of indices of REFs, in the combined list above, space delimited
#note that counting starts from 0
REFIndexFile = 'REFIndex.txt'

#coordinates of REFs in the new session
InputFile = 'Input.txt'

#output coordinates in the new session
OutputFile = 'Output.txt'

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

numpy.savetxt(OutputFile, New)
