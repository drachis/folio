"""
From three selected object A, B, C
the distance between A and B drives the scale of C
Automates the expression setup
"""
import pymel as pm
import maya.cmds as cmds
import math
# distance between selected
for node in pm.core.ls(selection = True):
    print node.translate.get()
    print node.outputs(connections=1)

def distance(x1,x2,y1,y2,z1,z2):
    sq1 = (x1-x2)*(x1-x2)
    sq2 = (y1-y2)*(y1-y2)
    sq3 = (z1-z2)*(z1-z2)
    return math.sqrt(sq1 + sq2 + sq3)
    
def nodeDist(node1, node2):
    t1 = node1.translate.get()
    t2 = node2.translate.get()
    return distance(t1[0],t2[0],\
                t1[1],t2[1],\
                t1[2],t2[2])

def expDist(node1,node2):
    # create a distance equation from the two nodes given and return it as a string.
    nodes = [node1.name(),node2.name()]
    axes = ["X","Y","Z"]
    equation = "sqrt("
    for axi in axes:
        axi = "translate" + axi
        eq = "(" + nodes[0] + "." + axi + "-" + nodes[1]  + "."+ axi + ")"
        equation += eq + "*" + eq + "+"
    equation = equation[:-1]+ ")"
    print equation
    return equation
                
if __name__ == "__main__":
    sel = pm.core.ls(selection = True)
    for each in sel:
        print "[Name]" + str(each.name())
    size = nodeDist(sel[0],sel[1])
    cmds.scale(size,size,size, 'nurbsSphere1',absolute=True)
    exp = expDist(pm.core.general.PyNode(sel[0]),pm.core.general.PyNode(sel[1]))
    target = sel[2].name()
    cmds.expression(o = '%s'%(target) , s ="%s.scaleX = %s"%(target,exp))
    cmds.expression(o = '%s'%(target) , s ="%s.scaleY = %s"%(target,exp))
    cmds.expression(o = '%s'%(target) , s ="%s.scaleZ = %s"%(target,exp))