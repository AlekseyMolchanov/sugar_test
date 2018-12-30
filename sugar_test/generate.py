#!/usr/bin/env python
# encoding: utf-8

from faker import Faker
fake = Faker()

from random import randint, choice
from datetime import datetime, timedelta
import check

#region generate_

def generate_person(sex=None):
    if sex is None:
        sex = choice([0,1])

    salutation = [None, 'Dr.', 'Prof.']
    
    if sex:
        salutation += ['Mr.']
    else:
        salutation += ['Ms.']

    if sex:
        return generate_first_name_male(), generate_last_name_male(), 1, choice(salutation)
    return generate_first_name_female(), generate_last_name_female(), 0, choice(salutation)

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
 
def generate_Country():
    return fake.country()

def generate_AccountType():
    return choice(['Analyst', 'Competitor', 'Customer', 'Integrator',
                        'Investor', 'Other', 'Partner', 'Press', 'Prospect', 'Reseller'])

def generate_dates_range(hours=1, fmt="%Y-%m-%dT%H:%M:%S-00:00"):
    # yyyy-mm-ddThh:mm:ss-00:00
    s = datetime.now() + timedelta(minutes=randint(240, 1200)) 
    e = s + timedelta(hours=hours)
    return s.strftime(fmt), e.strftime(fmt)

def generate_now(hours=0, fmt="%Y-%m-%dT%H:%M:%S-00:00"):
    # yyyy-mm-ddThh:mm:ss-00:00
    s = datetime.now()  + timedelta(hours=hours)
    return s.strftime(fmt)
 #endregion 
