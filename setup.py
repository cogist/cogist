"""
Setup script for building Cogist macOS app bundle
"""

from setuptools import setup

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "iconfile": None,
    "plist": {
        "CFBundleName": "Cogist",
        "CFBundleDisplayName": "Cogist",
        "CFBundleIdentifier": "com.cogist.app",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "????",
        # Critical: Language settings
        "CFBundleDevelopmentRegion": "zh_CN",
        "CFBundleAllowMixedLocalizations": True,
        "CFBundleLocalizations": ["zh_CN", "zh-Hans", "en"],
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "10.15",
    },
    "includes": [
        "PySide6",
    ],
    "resources": [
        "Resources/zh-Hans.lproj",
        "Resources/en.lproj",
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
