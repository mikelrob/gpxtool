#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
now = datetime.now()

import argparse
import sys
import xml.etree.ElementTree as ET
from iso8601 import iso8601

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('base',
                    type=argparse.FileType('r'),
                    help='base gpx file')
parser.add_argument('extra',
                    type=argparse.FileType('r'),
                    help='extra element gpx file')
parser.add_argument('--out',
                    required=False,
                    type=str)

args = vars(parser.parse_args())

NAME_SPACE = "http://www.topografix.com/GPX/1/1"

def gpxtool(args):
    ET.register_namespace("", NAME_SPACE)
    ET.register_namespace("gpxtpx", "http://www.garmin.com/xmlschemas/TrackPointExtension/v1")
    base = ET.parse(args['base'])
    extra = ET.parse(args['extra'])
    out = args['out'] if args['out'] is not None else sys.stdout.buffer

    base_track = get_track(base)
    base_segs = get_track_segs(base_track)

    extra_track = get_track(extra)
    extra_segs = get_track_segs(extra_track)

    for point in base_segs:
        time = get_track_point_time(point)
        for extra_point in extra_segs:
            extra_time = get_track_point_time(extra_point)
            if time == extra_time:
                extra_extensions = get_extensions(extra_point)
                point.append(extra_extensions)
                break

    # finally write it to buffer
    base.write(out)

def walk_tree(tree):
    for child in tree.getroot():
        print(child.tag, child.attrib)

def get_track(gpx):
    root = gpx.getroot()
    track_tag = '{{{}}}trk'.format(NAME_SPACE)
    for element in root:
        if element.tag == track_tag:
            return element

def get_track_segs(track):
    track_seg_tag = '{{{}}}trkseg'.format(NAME_SPACE)
    for element in track:
        if element.tag == track_seg_tag:
            return element

def get_track_point_time(track_point):
    time_tag = '{{{}}}time'.format(NAME_SPACE)
    for element in track_point:
        if element.tag == time_tag:
            return iso8601.parse_date(element.text)

def get_extensions(point):
    extensions_tag = '{{{}}}extensions'.format(NAME_SPACE)
    for element in point:
        if element.tag == extensions_tag:
            return element

if __name__ == '__main__':
    gpxtool(args)
    print("Started: {}".format(now))
    print("Finished: {}".format(datetime.now()))


