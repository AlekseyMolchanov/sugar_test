#!/usr/bin/env python
# encoding: utf-8

import os
import re

PHONE164 = re.compile(r'^\+?[1-9]\d{1,14}$')

#region check_

def check_account_CompanyName(value):
    '''
    A *random* CompanyName e.g. John Doe (two words)
    '''
    return value and len(value.split(' ')) == 2

def check_account_Street(value):
    '''
    A *random* Street e.g. Anystreet 1 (one word and one digit)
    '''
    _parts = value and value.split(' ')
    return value and \
            len(_parts) == 2 and \
            any(map(lambda part: str(part).isdigit(), _parts)) and \
            any(map(lambda part: not str(part).isdigit(), _parts))

def check_account_ZIP(value):
    '''
    A *random* ZIP e.g. 1234 (four digits)
    '''
    return value and \
            len(str(value).strip()) == 4 and \
            str(value).isdigit()

def check_account_City(value):
    '''
    A *random* City e.g. Smith (one word)
    '''
    return value and len(str(value).split(' ')) == 1

def check_PhoneNumber(value):
    '''
    A *random*  e.g. +41441234567 (iso164 string)
    '''
    return PHONE164.match(value)

def check_account_Industry(value):
    '''
    A *random* Industry e.g. Banking (one word)
    '''
    return value in ['Banking', 'Dairy', 'Services']


def check_account_child(account):
    '''
    Between 0 and 10 child contacts (foreign key)
    '''
    pass

def check_contact_Parent(value):
    '''
    Parent account ID *not random*
    '''
    pass

def check_contact_Firstname(value):
    '''
    A *random* Firstname e.g. Randy
    '''
    return value and value.strip() and \
            len(str(value).split(' ')) == 1 and \
            not str(value).isdigit()

def check_contact_Lastname(value):
    '''
    A *random* Lastname e.g. Jones
    '''
    return value and value.strip() and \
            len(str(value).split(' ')) == 1 and \
            not str(value).isdigit()

def check_contact_Position(value):
    '''
    A *random* Position e.g. CEO (one word)
    '''
    return  value in ['CEO', 'CFO', 'CIO']
            
def check_contact_Email(value, first_name, last_name):
    '''
    A *random* Email e.g. randy.jones@mailinator.com
    '''
    email = '%s.%s@mailinator.com' % (first_name.lower(), last_name.lower())
    return value == email

#endregion 
