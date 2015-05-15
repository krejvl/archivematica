#!/usr/bin/env python2

# This file is part of Archivematica.
#
# Copyright 2010-2013 Artefactual Systems Inc. <http://artefactual.com>
#
# Archivematica is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Archivematica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Archivematica.  If not, see <http://www.gnu.org/licenses/>.

# @package Archivematica
# @subpackage MCPServer
# @author Joseph Perry <joseph@artefactual.com>

import logging
import lxml.etree as etree
import sys
import uuid

import archivematicaMCP
from unit import unit

sys.path.append("/usr/share/archivematica/dashboard")
from main.models import Transfer

sys.path.append("/usr/lib/archivematica/archivematicaCommon")
from dicts import ReplacementDict

LOGGER = logging.getLogger('archivematica.mcp.server')

class unitTransfer(unit):
    def __init__(self, currentPath, UUID=""):
        self.owningUnit = None
        self.unitType = "Transfer"
        # Just use the end of the directory name
        self.pathString = "%transferDirectory%"
        currentPath2 = currentPath.replace(archivematicaMCP.config.get('MCPServer', "sharedDirectory"), "%sharedPath%", 1)

        if not UUID:
            try:
                UUID = Transfer.objects.filter(currentlocation=currentPath2).values_list('uuid')[0][0]
                LOGGER.info('Using existing Transfer %s at %s', UUID, currentPath2)
            except IndexError:
                pass

        if not UUID:
            uuidLen = -36
            if archivematicaMCP.isUUID(currentPath[uuidLen - 1:-1]):
                UUID = currentPath[uuidLen - 1:-1]
            else:
                UUID = str(uuid.uuid4())
                self.UUID = UUID
                Transfer.objects.create(uuid=UUID, currentlocation=currentPath2)

        self.currentPath = currentPath2
        self.UUID = UUID
        self.fileList = {}
        self.query = Transfer.objects.filter(uuid=self.UUID)

    def getModel(self):
        return self.query[0]

    def __str__(self):
        return 'unitTransfer: <UUID: {u.UUID}, path: {u.currentPath}>'.format(u=self)

    def setMagicLink(self, link, exitStatus=""):
        """Assign a link to the unit to process when loaded.
        Deprecated! Replaced with Set/Load Unit Variable"""
        updates = {
            "magiclink": link
        }
        if exitStatus:
            updates["magiclinkexitmessage"] = exitStatus
        self.query.update(**updates)

    def getMagicLink(self):
        """Load a link from the unit to process.
        Deprecated! Replaced with Set/Load Unit Variable"""
        try:
            return self.query.values_list("magiclink", "magiclinkexitmessage")[0]
        except IndexError:
            return

    def reload(self):
        self.currentPath = self.query.values_list("currentlocation")[0][0]

    def getReplacementDic(self, target):
        ret = ReplacementDict.frommodel(
            type_='transfer',
            sip=self.getModel(),
        )
        ret["%unitType%"] = self.unitType
        return ret

    def xmlify(self):
        ret = etree.Element("unit")
        etree.SubElement(ret, "type").text = "Transfer"
        unitXML = etree.SubElement(ret, "unitXML")
        etree.SubElement(unitXML, "UUID").text = self.UUID
        tempPath = self.currentPath.replace(archivematicaMCP.config.get('MCPServer', "sharedDirectory"), "%sharedPath%").decode("utf-8")
        etree.SubElement(unitXML, "currentPath").text = tempPath

        return ret
