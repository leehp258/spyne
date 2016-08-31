# encoding: utf8
#
# spyne - Copyright (C) Spyne contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

import logging
logger = logging.getLogger(__name__)

from collections import defaultdict

from lxml import etree, html

from spyne.protocol.cloth import XmlCloth
from spyne.protocol.cloth._base import XmlClothProtocolContext
from spyne.util.oset import oset


def parse_html_fragment_file(T_FILES):
    elt = html.fromstring(open(T_FILES).read())
    elt.getparent().remove(elt)
    return elt


class HtmlClothProtocolContext(XmlClothProtocolContext):
    def __init__(self, parent, transport, type=None):
        super(HtmlClothProtocolContext, self).__init__(parent, transport, type)

        self.assets = []
        self.eltstack = defaultdict(list)
        self.ctxstack = defaultdict(list)
        self.rootstack = oset()
        self.tags = set()
        self.screen = None


class HtmlCloth(XmlCloth):
    mime_type = 'text/html; charset=UTF-8'

    def __init__(self, app=None, mime_type=None, ignore_uncap=False,
                           ignore_wrappers=False, cloth=None, cloth_parser=None,
                                polymorphic=True, hier_delim='.', doctype=None):

        super(HtmlCloth, self).__init__(app=app, mime_type=mime_type,
                ignore_uncap=ignore_uncap, ignore_wrappers=ignore_wrappers,
                cloth=cloth, cloth_parser=cloth_parser, polymorphic=polymorphic)

        self.hier_delim = hier_delim
        self.doctype = doctype

    def _parse_file(self, file_name, cloth_parser):
        if cloth_parser is None:
            cloth_parser = html.HTMLParser(remove_comments=True)

        cloth = html.parse(file_name, parser=cloth_parser)
        return cloth.getroot()

    def docfile(self, *args, **kwargs):
        return etree.htmlfile(*args, **kwargs)

    def write_doctype(self, ctx, parent, cloth=None):
        if cloth is not None:
            dt = cloth.getroottree().docinfo.doctype
        elif self.doctype is not None:
            dt = self.doctype
        elif self._root_cloth is not None:
            dt = self._root_cloth.getroottree().docinfo.doctype
        elif self._cloth is not None:
            dt = self._cloth.getroottree().docinfo.doctype
        else:
            return

        parent.write_doctype(dt)
        ctx.protocol.doctype_written = True
        logger.debug("Doctype written as: '%s'", dt)

    def get_context(self, parent, transport):
        return HtmlClothProtocolContext(parent, transport)

    @staticmethod
    def get_class_cloth(cls):
        return cls.Attributes._html_cloth

    @staticmethod
    def get_class_root_cloth(cls):
        return cls.Attributes._html_root_cloth

    def dict_to_parent(self, ctx, cls, inst, parent, name, **kwargs):
        parent.write(str(inst))

    def subserialize(self, ctx, cls, inst, parent, name='', **kwargs):
        # FIXME: This ugly HACK needs to GO!!!
        try:
            from neurons.base.screen import ScreenBase

        except ImportError:
            pass

        else:
            if issubclass(cls, ScreenBase) and isinstance(inst, ScreenBase):
                assert ctx.protocol.screen is None
                ctx.protocol.screen = inst
                logger.debug("Found screen instance %r", cls)

        return super(HtmlCloth, self).subserialize(ctx, cls, inst, parent, name,
                                                                       **kwargs)

# FIXME: Deprecated
HtmlBase = HtmlCloth
