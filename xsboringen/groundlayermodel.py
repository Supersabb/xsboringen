#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.solid import Solid

from collections import namedtuple
from pathlib import Path
import logging
import csv
import os


class GroundLayerModel(object):
    IndexFieldNames = namedtuple('IndexFields',
        ['number', 'name', 'topfile', 'basefile', 'color'],
        )
    def __init__(self,
            solids=None,
            res=10.,
            styles=None,
            default=None,
            name=None,
            ):
        self.solids = solids or []
        self.styles = styles or {}
        self.res = res
        self.default = default
        self.name = name

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:}, '
            'solids={s.size:d})').format(s=self)

    @property
    def size(self):
        return len(self.solids)

    @classmethod
    def from_folder(cls, folder, indexfile, fieldnames,
        delimiter=',',
        res=10.,
        default=None,
        name=None,
        ):
        folder = Path(folder)
        fieldnames = cls.IndexFieldNames(**fieldnames)
        solids = []
        styles = {}
        with open(indexfile) as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                # if solid number is less or equal to zero, skip
                solid_number = int(row[fieldnames.number])
                if not solid_number > 0:
                    continue

                # add solid to model as tuple (number, solid)
                solid_name = row[fieldnames.name]
                solids.append((solid_number, Solid(
                    name=solid_name,
                    topfile=folder / row[fieldnames.topfile],
                    basefile=folder / row[fieldnames.basefile],
                    res=res,
                    stylekey=solid_name,
                    )))

                # add style to styles dict
                solid_style = default.copy()
                solid_style.update({
                    'label': solid_name,
                    'facecolor': row[fieldnames.color],
                    })
                styles[solid_name] = solid_style

        return cls(
            solids=solids,
            res=res,
            styles=styles,
            default=default,
            name=name,
            )

    def sort(self):
        self.solids = [s for s in sorted(self.solids)]
