# -*- coding: utf-8 -*-
import KBEngine
import math
import Math
import time
import random
from KBEDebug import *

class Motion:
    """
    docstring for ClassName
    """


    def __init__(self):

        self.nextMoveTime = int(time.time() + random.randint(5, 15))

    def stopMotion(self):
        """
        停止移动
        """
        if self.isMoving:
        #INFO_MSG("%i stop motion." % self.id)
            self.cancelController("Movement")
            self.isMoving = False

    def randomWalk(self,basePos):
        """
        随机移动entity
        """

        if self.isMoving:
            return False

        if time.time() < self.nextMoveTime:
            return False

        while True:
            # 移动半径距离在30米内
            if self.canNavigate():
                destPos = self.getRandomPoints(basePos, 30.0, 1, 0)

                if len(destPos) == 0:
                    self.nextMoveTime = int(time.time() + random.randint(5, 15))
                    return False

                destPos = destPos[0]
            else:
                rnd = random.random()
                a = 30.0 * rnd              # 移动半径距离在30米内
                b = 360.0 * rnd             # 随机一个角度
                x = a * math.cos( b )       # 半径 * 正余玄
                z = a * math.sin( b )

                destPos = (basePos.x + x, basePos.y, basePos.z + z)

            if self.position.distTo(destPos) < 2.0:
                continue

            self.gotoPosition(destPos)
            self.isMoving = True
            self.nextMoveTime = int(time.time() + random.randint(5, 15))
            break

        return True

    def resetSpeed(self):

        walkSpeed = self.getDatas()["moveSpeed"]
        if walkSpeed != self.moveSpeed:
            self.moveSpeed = walkSpeed

    def backSpawnPos(self):
        """
        virtual method.
        """
        INFO_MSG("%s::backSpawnPos: %i, pos=%s, speed=%f." % (self.getScriptName(), self.id, self.spawnPos, self.moveSpeed * 0.1))

        self.resetSpeed()
        self.gotoPosition(self.spawnPos)


    def gotoEntity(self, targetID, dist = 0.0):
        """
        virtual method.
        移动到entity位置
        """
        if self.isMoving:
            self.stopMotion()

        entity = KBEngine.entities.get(targetID)
        if entity is None:
            DEBUG_MSG("%s::gotoEntity: not found targetID=%i" % (targetID))
            return

        if entity.position.distTo(self.position) <= dist:
            return

        self.isMoving = True
        self.moveToEntity(targetID, self.moveSpeed * 0.1, dist, None, True, False)


    def gotoPosition(self, position,speed=0.0, dist = 0.0):
        """
        virtual method.
        移动到位置
        """
        DEBUG_MSG("Motion::gotoPosition.%i:isMoving = %i,position(%f,%f,%f),dist=%f,speed=%f" %
            (self.id,self.isMoving,position.x,position.y,position.z,dist,speed))

        if self.isMoving:
            self.stopMotion()

        self.isMoving = True

        if speed == 0.0:
            speed = self.moveSpeed * 0.1

        self.moveToPoint(position, speed, dist, None, False, False)


    def getStopPoint(self, yaw = None, rayLength = 100.0):
        """
        """
        if yaw is None:
            yaw = self.yaw
        yaw = (yaw / 2);
        vv = Math.Vector3(math.sin(yaw), 0, math.cos(yaw))
        vv.normalise()
        vv *= rayLength

        lastPos = self.position + vv;

        pos = KBEngine.raycast(self.spaceID, self.layer, self.position, vv)
        if pos == None:
            pos = lastPos

        return pos


    def setCruiseSpeed(self,exposed,speed):
        """
        """
        if exposed != self.id:
            return

#        DEBUG_MSG("Motion::setCruiseSpeed.%i:speed = %f,CruiseSpeed = %f" % (self.id,speed,self.cruiseSpeed))

        if speed != self.cruiseSpeed and speed >= 0:
            self.cruiseSpeed = speed
    #--------------------------------------------------------------------------------------------
    #                              Callbacks
    #--------------------------------------------------------------------------------------------
    def onMove(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        #DEBUG_MSG("%s::onMove: %i controllerId =%i, userarg=%s" % \
        #               (self.getScriptName(), self.id, controllerId, userarg))
        self.isMoving = True

    def onMoveFailure(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        DEBUG_MSG("%s::onMoveFailure: %i controllerId =%i, userarg=%s" % \
                        (self.getScriptName(), self.id, controllerId, userarg))

        self.isMoving = False

    def onMoveOver(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity移动结束时均会调用此接口
        """
        self.isMoving = False