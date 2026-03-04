# -*- coding: utf-8 -*-
# @author: leesoar

"""something."""
import argparse
import json
import sys

from . import util, __version__


def show_devices(args):
    devices = util.get_device(args.timeout)

    if not devices:
        return print("No online devices.")

    for i, d in enumerate(devices, start=1):
        print(f"=> Device {i}:\n{json.dumps(d, ensure_ascii=False, indent=4)}\n")


def play(args):
    src = {"file_video": args.src}

    try:
        if args.device_location:
            device = util.parse_xml(args.device_location)
        elif args.query_device:
            device = list(filter(lambda x: args.query_device.lower() in x["friendly_name"].lower(), util.get_device(args.timeout)))[0]
        else:
            device = util.get_device(args.timeout)[0]
    except Exception:
        device = None

    if not device:
        print("No online devices.")
        sys.exit()

    print(f"Current play device: {device['friendly_name']}")

    if args.src.startswith("http"):
        util.play(args.src.replace("&", "&amp;").replace("\\", ""), device, True)
    else:
        serve_ip = util.get_serve_ip(util.get_serve_ip(device["host"]))
        files_urls = util.start_server(src, serve_ip)
        util.play(files_urls, device)


def run():
    parser = argparse.ArgumentParser(
        description=f"A UPnP/DLNA client, support local file and online resource cast to screen.",
        prog="dlna", add_help=False)

    subparsers = parser.add_subparsers(dest='cmd', title='Available commands')
    parser.add_argument('-v', '--version', action='version', version=__version__, help='Get version of dlna')
    parser.add_argument('-h', '--help', action='help', help='Show help message')

    p_device = subparsers.add_parser('device')
    p_device.set_defaults(func=show_devices)
    p_device.add_argument("-t", "--timeout", type=float, default=5)

    p_play = subparsers.add_parser('play')
    p_play.set_defaults(func=play)
    p_play.add_argument("-d", "--device", dest="device_location")
    p_play.add_argument("-q", "--query", dest="query_device")
    p_play.add_argument("-t", "--timeout", type=float, default=5)
    p_play.add_argument('src', type=str, help="media src")

    try:
        args = parser.parse_args()
        args.func(args)
    except Exception:
        print("Caught an exception, please try again.")
