#!/usr/bin/env python
# coding: utf8
# Part of the bioread package for reading BIOPAC data.
#
# Copyright (c) 2016 Board of Regents of the University of Wisconsin System
#
# Written by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
# Imaging and Behavior, University of Wisconsin-Madison
# Project home: http://github.com/njvack/bioread
#
# This script pulls all the markers from an AcqKnowledge file and writes it
# to a delimited format.

"""Print the markers from an AcqKnowledge file.

Usage:
  acq_markers [options] <file>...
  acq_markers -h | --help
  acq_markers --version

Options:
  -o <file>     Write to a file instead of standard output.
"""

from __future__ import (
    unicode_literals, absolute_import, division, with_statement)

import sys
import csv

from bioread.vendor.docopt import docopt
from bioread import readers
from bioread.version import version_str


FIELDS = [
    'filename',
    'time (s)',
    'label',
    'channel',
    'style',
]


def marker_formatter(acq_filename, graph_sample_msec):
    """ Return a function that turns a marker into a dict. """
    def f(marker):
        return {
            'filename': acq_filename,
            'time (s)': (marker.sample_index * graph_sample_msec) / 1000,
            'label': marker.text,
            'channel': marker.channel or 'Global',
            'style': marker.style or 'None'
        }
    return f


def acq_markers_output_file(input_filenames, output_filename):
    with open(output_filename, 'w') as f:
        return acq_markers(input_filenames, f)


def acq_markers(input_filenames, output_stream):
    csv_out = csv.DictWriter(output_stream, FIELDS, delimiter=str("\t"))
    csv_out.writeheader()
    for fname in input_filenames:
        with open(fname, 'rb') as infile:
            r = readers.AcqReader(infile)
            r._read_markers()
            mf = marker_formatter(fname, r.graph_header.sample_time)
            for m in r.markers:
                csv_out.writerow(mf(m))


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    pargs = docopt(
        __doc__,
        args,
        version="bioread {0}".format(version_str()))

    if pargs['-o']:
        return acq_markers_output_file(pargs['<file>'], pargs['-o'])
    else:
        return acq_markers(pargs['<file>'], sys.stdout)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))