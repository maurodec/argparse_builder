# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import html
from browser import document as doc

from collections import OrderedDict

# import animator
import argtools


# Variables ===================================================================
ARG_PARSER_TEMPLATE = """import argparse

# ...
parser = argparse.ArgumentParser(
    $parameters
)
$arguments
args = parser.parse_args()

"""

ARG_TEMPLATE = """parser.add_argument(
    $parameters
)"""


# Functions & objects =========================================================
class ArgInput(object):
    def __init__(self, element):
        self.ID = element.id.split("_")[0]
        self.name = element.id.split("_")[-1]
        self.element = element

        if self.element.value == "":
            self.element.value = self.element.title

        self.is_text_type = (element.type == "text" or element.nodeName == "TEXTAREA")

        if self.is_text_type:
            element.bind("focus", self.input_remove_help)
            element.bind("blur", self.input_add_help)
        elif element.nodeName == "SELECT":
            element.bind("change", self.on_change)

    def on_change(self, ev):
        if self.name == "type" and ev.target.value == "custom":
            new_html = '<input id="%s" type="text" _non_str="true" ' % self.ID
            new_html += '_non_key="" _default="" />'
            ev.target.outerHTML = new_html

            self.is_text_type = True
            self.element = doc[self.ID]

    def input_remove_help(self, ev):
        if ev.target.value == ev.target.title:
            ev.target.value = ""

    def input_add_help(self, ev):
        if ev.target.value == "":
            ev.target.value = ev.target.title

    @property
    def value(self):
        # selects
        if not self.is_text_type and \
           self.element.value == self.element._default:
            return None

        if self.element.type == "checkbox":
            value = self.element.checked

            if self.element._default == str(value):
                return None

            return value

        if self.element.value != self.element.title:
            if self.element._non_str:
                return self.element.value

            return '"' + self.element.value + '"'  # TODO: long lines / mutiple lines

        return None

    @value.setter
    def value(self, new_val):
        self.element.value = new_val

    def __str__(self):
        if self.element._non_key:
            return str(self.value)

        return self.name + "=" + str(self.value)


class Argument(object):
    def __init__(self):
        self.ID = str(argtools.get_id_from_pool())
        element = self._add_html_repr()

        arguments = element.get(selector="input")
        arguments = list(filter(lambda x: x.type != "button", arguments))
        arguments += element.get(selector="select")
        arguments += element.get(selector="textarea")
        self.inputs = OrderedDict(
            map(
                lambda x: (x.id.split("_")[-1], ArgInput(x)),
                sum(arguments, [])
            )
        )

    def _add_html_repr(self):
        """
        Add new argument table.
        """
        template = doc["argument_template"].innerHTML

        table = html.TABLE(id=self.ID + "_argument", Class="argument_table")
        table.html = template.replace("$ID", self.ID)
        doc["arguments"] <= table

        return table

    def remove(self):
        doc[self.ID + "_argument"].outerHTML = ""

    def __str__(self):
        vals = map(
            lambda x: str(x),
            filter(
                lambda x: x.value is not None,
                self.inputs.values()
            )
        )

        if len(list(vals)) == 0:
            return ""

        return ARG_TEMPLATE.replace(
            "$parameters",
            "\t" + "\n\t".join(vals)
        )


class ArgParser(object):
    def __init__(self):
        self.arguments = OrderedDict()
        self.add_argument()

    def bind_argument(self, argument):
        doc[argument.ID + "_argument_button_add"].bind(
            "click",
            self.add_argument
        )
        doc[argument.ID + "_argument_button_rm"].bind(
            "click",
            self.remove_argument
        )
        # doc[ID + "_argument_button_up"].bind("click", move_argument_up)
        # doc[ID + "_argument_button_down"].bind("click", move_argument_down)

    def new_argument(self):
        arg = Argument()
        self.bind_argument(arg)
        return arg

    def add_argument(self, ev=None):
        arg = self.new_argument()
        self.arguments[arg.ID] = arg

    def remove_argument(self, ev=None):
        if len(self.arguments) > 1:
            ID = ev.target.id.split("_")[0]
            self.arguments[ID].remove()
            del self.arguments[ID]

    def __str__(self):
        out = ""
        for item in self.arguments.values():
            out += item.__str__()

        out = ARG_PARSER_TEMPLATE.replace("$arguments", out)

        return out


# Main program ================================================================
a = ArgParser()

def set_txt(ev=None):
    doc["output"].value = a.__str__()

doc["output"].bind("click", set_txt)

# debug
# from browser import alert

# a = Argument()
# alert(a.inputs)
# alert(str(a))
# a.remove()
# a = Argument()