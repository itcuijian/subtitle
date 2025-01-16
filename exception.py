#!/usr/bin/python3
# -*- coding: UTF-8 -*-

class CustomException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"
