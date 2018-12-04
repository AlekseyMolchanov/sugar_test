#!/usr/bin/env python
# encoding: utf-8

import os
import re
from random import randint, choice

import pytest

from sugarcrm import Session, Account, Contact
from faker import Faker

fake = Faker()

COUNT = os.environ.get('COUNT')
PHONE164 = re.compile('^\+?[1-9]\d{1,14}$')

assert os.environ['COUNT']
assert os.environ['URL']
assert os.environ['USERNAME']
assert os.environ['PASSWORD']

@pytest.fixture(scope="module")
def session(request):
    url = os.environ['URL']
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    session = Session(url, username, password)

    cleanup(session)

    def teardown_module():
        cleanup(session)
        pass

    request.addfinalizer(teardown_module)
    return session

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

def check_account_PhoneNumber(value):
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
    return value and \
            len(str(value).strip()) == 1 and \
            not str(value).isdigit()

def check_contact_Lastname(value):
    '''
    A *random* Lastname e.g. Jones
    '''
    return value and \
            len(str(value).strip()) == 1 and \
            not str(value).isdigit()

def check_contact_Position(value):
    '''
    A *random* Position e.g. CEO (one word)
    '''
    return  value in ['CEO', 'CFO', 'CIO']
            
def check_contact_Email(value):
    '''
    A *random* Email e.g. randy.jones@mailinator.com
    '''
    pass


ids = lambda collection: map(lambda each:each.id, collection)
'''
01. Assert sum of created account equals 100
02. Assert sum of each child contact is between 1 and 10
03. Assert contact has parent account
04. Assert Account.Name equals two words
05. Assert Account.Street equals one word and one digit
06. Assert Account.ZIP equals four digits
07. Assert Account.City equals one word
08. Assert Account.PhoneNumber equals iso164 string
09. Assert Account.Industry equels Banking or Dairy or Services
10. Assert Account.ChildContacts.Sum is between 0 and 10 child

11. Assert Contact.FirstName equals one random.first_name
12. Assert Contact.LastName equals one random.last_name
13. Assert Contact.Position equals CEO or CFO or CIO
14. Assert Contact.PhoneNumber equals iso164 string
15. Assert Contact.Email equals random.first_name.random.last_name@mailinator.com
16. Assert every account is deleted
17. Assert every contact is deleted
'''

def get_accounts(session, deleted=False, account_type='test'):
    condition = dict(deleted=deleted)
    account_type and condition.update(dict(account_type=account_type))
    return session.get_entry_list(Account(**condition))

def create_account(session, name, street, ZIP, city, phoneNumber, industry, account_type='test'):
    account = Account(
        account_type=account_type,
        name=name,
        billing_address_street=street,
        billing_address_postalcode=ZIP,
        billing_address_city=city,
        phone_office=phoneNumber,
        industry=industry
    )
    return session.set_entry(account)

def create_contact(session, account_id, first_name, last_name, position, email, phone):
    contact = Contact(
        account_id=account_id,
        first_name=first_name,
        last_name=last_name,
        title=position,
        email1=email,
        phone_work=phone
    )
    return session.set_entry(contact)

def get_contacts(session, deleted=False):
    condition = dict(deleted=deleted)
    return session.get_entry_list(Contact(**condition))

def test_get_modules(session):
    modules = session.get_available_modules()
    modules_keys = [m.module_key for m in modules]
    assert 'Accounts' in modules_keys and 'Contacts' in modules_keys

def generate_CompanyName(count):
    stack = []
    while len(stack) <= count:
        company_name = fake.company()
        check_account_CompanyName(company_name) and stack.append(company_name)
    return stack

def generate_Street(count):
    stack = []
    while len(stack) <= count:
        street = '%s %s' % (
            fake.street_name().split(' ')[0], 
            fake.random_int(min=1000, max=9999))
        check_account_Street(street) and stack.append(street)
    return stack

def generate_City(count):
    stack = []
    while len(stack) <= count:
        city = fake.city()
        check_account_City(city) and stack.append(city)
    return stack

def generate_Phone(count):
    stack = []
    while len(stack) <= count:
        phone = "+%s%s%s" % (
            fake.random_int(min=1, max=999),
            str(fake.random_int(min=1, max=999)).zfill(3), 
            str(fake.random_int(min=1234567, max=9876543)), 
        )
        check_account_PhoneNumber(phone) and stack.append(phone)
    return stack

def test_generate(session):
    count = 0
    companys = generate_CompanyName(COUNT)
    streets = generate_Street(COUNT)
    citys = generate_City(COUNT)
    phones = generate_Phone(COUNT)

    while count <= COUNT:
        company_name = companys.pop()
        street = streets.pop()
        city = citys.pop()
        phone = phones.pop()
        ZIP = fake.numerify(text="####")
        industry = choice(['Banking', 'Dairy', 'Services'])
        contacts_count = randint(1, 10)

        count+=1
        
        account = create_account(
            session, 
            company_name,
            street, 
            ZIP, 
            city, 
            phone, 
            industry
        )

        for _ in range(contacts_count):
            sex = randint(0, 1)
            if sex:
                first_name = fake.first_name_male()
                last_name = fake.last_name_male()
            else:
                first_name = fake.first_name_female()
                last_name = fake.last_name_female()

            email = '%s.%s@mailinator.com' % (first_name.lower(), last_name.lower())
            position = choice(['CEO', 'CFO', 'CIO'])

            contact = create_contact(session, 
                account.id, first_name, last_name, position, 
                email, generate_Phone(1).pop())
    
def cleanup(session):
    
    contacts_index = {}
    contacts_acc_index = {}
    
    contacts = get_contacts(session)
    for contact in contacts:
        if hasattr(contact, 'account_id'):
            contacts_index[contact.id] = contact

            if contact.account_id not in contacts_acc_index:
                contacts_acc_index[contact.account_id] = []
            contacts_acc_index[contact.account_id].append(contact.id)

    accounts = get_accounts(session)
    if accounts:
        for account in accounts:
            for contact_id in contacts_index.get(account.id) or []:
                contact = contacts_index.get(contact_id)
                contact.deleted = True
                session.set_entry(account)

            account.deleted = True
            session.set_entry(account)
