# -*- coding: utf-8 -*-
import json
import traceback
import pickle
import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def jprint(obj):
    """make beautiful json"""
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)


def get_secrets(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        traceback.print_exc()


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_authenticated_service(flg):
    SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
    CLIENT_SECRETS_FILE = resource_path('secret.json')
    creds = None

    """well ok let's go with official quickstart"""

    if (os.path.exists("token.pickle")):
        with open("token.pickle", "rb") as tokenFile:
            creds = pickle.load(tokenFile)
    if not creds or not creds.valid:
        if (creds and creds.expired and creds.refresh_token):
            creds.refresh(Request())
        else:
            if flg:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                with open("token.pickle", "wb") as tokenFile:
                    pickle.dump(creds, tokenFile)
    if creds:
        return build('photoslibrary', 'v1', credentials=creds)


