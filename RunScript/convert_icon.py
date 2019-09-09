# /usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import glob
import shutil
import pprint
import biplist
from PIL import Image


src_root = os.path.dirname(os.path.realpath(__file__))
input_dir = os.path.join(src_root, "logos")
output_dir = os.path.join(src_root, "icons")
primary_icon_name = "Lark"

iPhone_size_scall = [
    (20, 2),
    (20, 3),
    (29, 2),
    (29, 3),
    (40, 2),
    (40, 3),
    (60, 2),
    (60, 3),
]

iPad_size_scall = [
    (20, 1),
    (20, 2),
    (29, 1),
    (29, 2),
    (40, 1),
    (40, 2),
    (76, 1),
    (76, 2),
    (83.5, 2),
]


def convertImage(imageFile, outdir, size, scale, is_iPhone=True):
    image = Image.open(imageFile)
    try:
        basename = os.path.basename(imageFile)
        name = os.path.splitext(basename)[0]
        scale_string = "" if scale == 1 else "@%dx" % scale
        suffix = "" if is_iPhone else "~ipad"
        new_name = "{name}{size}x{size}{scale_string}{suffix}.png".format(
            name=name,
            size=size,
            scale_string=scale_string,
            suffix=suffix,
        )
        size_of_scale = int(size*scale)
        resize = (size_of_scale, size_of_scale)
        new_image = image.resize(resize, Image.BILINEAR)
        new_image.save(os.path.join(output_dir, new_name))
    except Exception as e:
        print(e)


def getCFBundleIconFiles(name, is_iPhone=True):
    CFBundleIconFiles = set()
    size_scale_array = iPhone_size_scall if is_iPhone else iPad_size_scall
    for (size, scale) in size_scale_array:
        file_name = "{name}{size}x{size}".format(
            name=name,
            size=size,
        )
        CFBundleIconFiles.add(file_name)
    CFBundleIconFilesArray = list(CFBundleIconFiles)
    CFBundleIconFilesArray.sort()
    return CFBundleIconFilesArray


def getCFBundleAlternateIconSingle(name, is_iPhone=True):
    CFBundleIconFiles = getCFBundleIconFiles(name, is_iPhone=is_iPhone)
    info_dict = {"UIPrerenderedIcon": False}
    info_dict["CFBundleIconFiles"] = CFBundleIconFiles
    return info_dict


def getPrimaryIcon(primary_icon_name, is_iPhone=True):
    CFBundlePrimaryIcon = {}
    CFBundlePrimaryIcon["CFBundleIconName"] = primary_icon_name
    CFBundleIconFiles = getCFBundleIconFiles(
        primary_icon_name,
        is_iPhone=is_iPhone
    )
    CFBundlePrimaryIcon["CFBundleIconFiles"] = CFBundleIconFiles
    return CFBundlePrimaryIcon


def getCFBundleAlternateIcons(names, is_iPhone=True):
    CFBundleAlternateIcons = {
        "UINewsstandBindingType": "UINewsstandBindingTypeMagazine",
        "UINewsstandBindingEdge": "UINewsstandBindingEdgeLeft",
    }
    for name in names:
        CFBundleAlternateIcons[name] = getCFBundleAlternateIconSingle(
            name,
            is_iPhone=is_iPhone
        )
    return CFBundleAlternateIcons


def getCFBundleIcons(names, primaryIcon, is_iPhone=True):
    key = "CFBundleIcons" if is_iPhone else "CFBundleIcons~ipad"
    CFBundleIcons = {}
    CFBundleIcons["CFBundleAlternateIcons"] = getCFBundleAlternateIcons(
        names,
        is_iPhone=is_iPhone
    )
    CFBundleIcons["CFBundlePrimaryIcon"] = getPrimaryIcon(
        primaryIcon,
        is_iPhone=is_iPhone
    )
    return (key, CFBundleIcons)


def move_icons_to_directory(origin_dir_path, dest_dir_path):
    imageRe = os.path.join(origin_dir_path, "*.png")
    for imageFile in glob.glob(imageRe):
        basename = os.path.basename(imageFile)
        dest_file_path = os.path.join(dest_dir_path, basename)
        shutil.move(imageFile, dest_file_path)


if __name__ == '__main__':
    """Create Dir"""
    if os.path.exists(output_dir):
        if os.path.isfile(output_dir):
            os.remove(output_dir)
        elif os.path.isdir(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=False)

    """Convert icons"""
    imageRe = os.path.join(input_dir, "*.png")
    names = []
    for imageFile in glob.glob(imageRe):
        basename = os.path.basename(imageFile)
        name = os.path.splitext(basename)[0]
        names.append(name)
        for (size, scale) in iPhone_size_scall:
            convertImage(imageFile, output_dir, size, scale, is_iPhone=True)
        for (size, scale) in iPad_size_scall:
            convertImage(imageFile, output_dir, size, scale, is_iPhone=False)

    """Edit Info.plist"""
    (iPhone_key, iPhone_value) = getCFBundleIcons(
        names,
        primary_icon_name,
        is_iPhone=True
    )
    (iPad_key, iPad_value) = getCFBundleIcons(
        names,
        primary_icon_name,
        is_iPhone=False
    )
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(iPhone_key)
    pp.pprint(iPhone_value)
    pp.pprint(iPad_key)
    pp.pprint(iPad_value)
    plist_file_path = os.path.join(src_root, "Info.plist")
    plist_info = {}
    plist_info[iPhone_key] = iPhone_value
    plist_info[iPad_key] = iPad_value
    biplist.writePlist(plist_info, plist_file_path, binary=False)
    print("Write Info.plist Success")