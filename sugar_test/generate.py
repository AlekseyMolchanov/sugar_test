#!/usr/bin/env python
# encoding: utf-8

from faker import Faker
fake = Faker()

from random import randint, choice

import check

#region generate_
def generate_first_name_male():
    return fake.first_name_male()

def generate_last_name_male():
    return fake.last_name_male()

def generate_first_name_female():
    return fake.first_name_female()

def generate_last_name_female():
    return fake.last_name_female()
    
def generate_CompanyName():
    while 1:
        company_name = fake.company()
        if check.check_account_CompanyName(company_name):
            yield company_name

def generate_Street():
    while 1:
        street = '%s %s' % (
            fake.street_name().split(' ')[0], 
            fake.random_int(min=1000, max=9999))
        if check.check_account_Street(street):
            yield street

def generate_City():
    while 1:
        city = fake.city()
        if check.check_account_City(city):
            yield city

def generate_Phone():
    while 1:
        phone = "+%s%s%s" % (
            fake.random_int(min=1, max=999),
            str(fake.random_int(min=1, max=999)).zfill(3), 
            str(fake.random_int(min=1234567, max=9876543)), 
        )
        if check.check_PhoneNumber(phone):
            yield phone

def generate_Email(first_name, last_name):
    email = '%s.%s@mailinator.com' % (first_name.lower(), last_name.lower())
    return email 

def generate_Position():
    return choice(['CEO', 'CFO', 'CIO'])

def generate_Industry():
    return choice(['Banking', 'Dairy', 'Services'])

def generate_ZIP():
    return fake.numerify(text="####")
 #endregion 
