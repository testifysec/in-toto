#!/usr/bin/env python
"""
<Program Name>
  link.py

<Author>
  Lukas Puehringer <lukas.puehringer@nyu.edu>
  Santiago Torres <santiago@nyu.edu>

<Started>
  Sep 23, 2016

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Provides a class for link metadata which is information gathered when a
  step of the supply chain is performed.
"""

import attr
import json
from . import common as models__common
import securesystemslib.formats

FILENAME_FORMAT = "{step_name}.{short_keyid}.link"
UNFINISHED_FILENAME_FORMAT = ".{step_name}.{short_keyid}.link-unfinished"

@attr.s(repr=False)
class Link(models__common.Signable):
  """
  A link is the metadata representation of a supply chain step performed
  by a functionary.

  Links are recorded, signed and stored to a file when a functionary wraps
  a command with in_toto-run.

  Links also contain materials and products which are hashes of the file before
  the command was executed and after the command was executed.

  <Attributes>
    name:
        a unique name used to identify the related step in the layout
    materials and products:
        a dictionary in the format of
          { <relative file path> : {
            {<hash algorithm> : <hash of the file>}
          },... }

    byproducts:
        a dictionary in the format of
          {
            "stdout": <standard output of the executed command>
            "stderr": <standard error of the executed command>
          }

    command:
        the command that was wrapped by in_toto-run

    return_value:
        the return value of the executed command
   """

  _type = attr.ib("Link", init=False)
  name = attr.ib("")
  materials = attr.ib(default=attr.Factory(dict))
  products = attr.ib(default=attr.Factory(dict))
  byproducts = attr.ib(default=attr.Factory(dict))
  command = attr.ib("")
  return_value = attr.ib(None)

  def dump(self, filename=False, key=False):
    """
    Method to dump the link metdata files
    If filename is provided, link is stored with that name
    If key is provided, then the usual [step-name].[keyid].link
    format is used to store the link
    If nothing is provided (during inspection), link is stored
    as [step-name].link
    If both filename and key are provided, the key gets ignored
    as first preference is given to the filename.
    """
    if filename:
      fn = filename
    elif key:
      securesystemslib.formats.KEY_SCHEMA.check_match(key)
      fn = FILENAME_FORMAT.format(step_name=self.name, short_keyid="{:.8}".format(key["keyid"]))
    else:
      fn = "{}.link".format(self.name)
    super(Link, self).dump(fn)

  @staticmethod
  def read_from_file(filename):
    """Static method to instantiate a new Link object from a
    canonical JSON serialized file """
    with open(filename, 'r') as fp:
      return Link.read(json.load(fp))

  @staticmethod
  def read(data):
    """Static method to instantiate a new Link from a Python dictionary """
    # XXX LP: ugly workaround for attrs underscore strip
    # but _type is exempted from __init__ anyway
    if data.get("_type"):
      data.pop(u"_type")
    return Link(**data)
