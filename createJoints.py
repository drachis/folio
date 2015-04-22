# -*- coding: utf-8 -*-
"""
Created on Thu Oct 09 11:46:26 2014

@author: toli

create joints at selected objects and name them after the object.
"""
import maya.cmds as cmds
sel = cmds.ls(selection=True)
cmds.select(clear= True)
for obj in sel:
    cmds.joint(
        name = obj,
        radius=0.3,
        p = cmds.xform(obj, query=True, translation=True, worldSpace=True)
        )
    cmds.select(clear= True)
import maya.cmds as cmds
sel = cmds.ls(selection=True)
cmds.select(clear= True)
for obj in sel:
    cmds.joint(
        name = obj,
        radius=0.3,
        p = cmds.xform(obj, query=True, translation=True, worldSpace=True)
        )
    cmds.select(clear= True)