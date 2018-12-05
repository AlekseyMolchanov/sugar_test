#!/usr/bin/env python
# encoding: utf-8

import os
import re
from random import randint, choice

import pytest

from sugarcrm import Session, Account, Contact
from faker import Faker

fake = Faker()

COUNT = int(os.environ.get('COUNT'))
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

    # cleanup(session)

    def teardown_module():
        # cleanup(session)
        pass

    request.addfinalizer(teardown_module)
    return session

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
#endregion 
#region generate_

def generate_CompanyName():
    while 1:
        company_name = fake.company()
        if check_account_CompanyName(company_name):
            yield company_name

def generate_Street():
    while 1:
        street = '%s %s' % (
            fake.street_name().split(' ')[0], 
            fake.random_int(min=1000, max=9999))
        if check_account_Street(street):
            yield street

def generate_City():
    while 1:
        city = fake.city()
        if check_account_City(city):
            yield city

def generate_Phone():
    while 1:
        phone = "+%s%s%s" % (
            fake.random_int(min=1, max=999),
            str(fake.random_int(min=1, max=999)).zfill(3), 
            str(fake.random_int(min=1234567, max=9876543)), 
        )
        if check_PhoneNumber(phone):
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

ids = lambda collection: map(lambda each:each.id, collection)

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

def get_contacts(session, deleted=False):
    condition = dict(deleted=deleted)
    return session.get_entry_list(Contact(**condition))

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

def cleanup(session):
    accounts = get_accounts(session)
    if accounts:
        for account in accounts:
            linked = session.get_entry("Accounts", account.id, links={'Contacts': ['id']})            
            for link in linked.contacts:
                contact = session.get_entry_list(Contact(id=link.id)).pop()
                contact.deleted = True
                session.set_entry(contact)
                
            account.deleted = True
            session.set_entry(account)
    return True

@pytest.mark.skip(reason="not needed")
def test_get_modules(session):
    modules = session.get_available_modules()
    modules_keys = [m.module_key for m in modules]
    assert 'Accounts' in modules_keys and 'Contacts' in modules_keys

def test_generate(session):
    count = 0
    companys = generate_CompanyName()
    streets = generate_Street()
    citys = generate_City()
    phones = generate_Phone()

    while count <= COUNT: 
        
        account = create_account(
            session, 
            next(companys),
            next(streets), 
            generate_ZIP(), 
            next(citys), 
            next(phones), 
            generate_Industry()
        )

        for _ in range(randint(1, 10)):
            sex = randint(0, 1)
            if sex:
                first_name = fake.first_name_male()
                last_name = fake.last_name_male()
            else:
                first_name = fake.first_name_female()
                last_name = fake.last_name_female()

            contact = create_contact(
                session, 
                account.id, 
                first_name, 
                last_name, 
                generate_Position(), 
                generate_Email(first_name, last_name), 
                next(phones)
            )
        count+=1

@pytest.mark.skip(reason="not ready")
def test_sum_of_created_account_equals_100():
    '''
    01. Assert sum of created account equals 100
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_sum_of_each_child_contact_is_between_1_and_10():
    '''
    02. Assert sum of each child contact is between 1 and 10
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_contact_has_parent_account():
    '''
    03. Assert contact has parent account
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Account_Name_equals_two_words():
    '''
    04. Assert Account.Name equals two words
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Account_Street_equals_one_word_and_one_digit():
    '''
    05. Assert Account.Street equals one word and one digit
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Account_ZIP_equals_four_digits():
    '''
    06. Assert Account.ZIP equals four digits
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Account_City_equals_one_word():
    '''
    07. Assert Account.City equals one word
    '''
    pass

def test_Account_PhoneNumber_equals_iso164_string():
    '''
    08. Assert Account.PhoneNumber equals iso164 string
    '''
    assert all(map(lambda a: check_PhoneNumber(a.phone_work), get_accounts(session)))

@pytest.mark.skip(reason="not ready")
def test_Account_Industry_equels_Banking_or_Dairy_or_Services():
    '''
    09. Assert Account.Industry equels Banking or Dairy or Services
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Account_ChildContacts_Sum_is_between_0_and_10_child():
    '''
    10. Assert Account.ChildContacts.Sum is between 0 and 10 child
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Contact_FirstName_equals_one_random_first_name():
    '''
    11. Assert Contact.FirstName equals one random.first_name
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Contact_LastName_equals_one_random_last_name():
    '''
    12. Assert Contact.LastName equals one random.last_name
    '''
    pass

@pytest.mark.skip(reason="not ready")
def test_Contact_Position_equals_CEO_or_CFO_or_CIO():
    '''
    13. Assert Contact.Position equals CEO or CFO or CIO
    '''
    pass

def test_Contact_PhoneNumber_equals_iso164_string(session):
    '''
    14. Assert Contact.PhoneNumber equals iso164 string
    '''
    assert all(map(lambda c: check_PhoneNumber(c.phone_office), get_contacts(session)))

@pytest.mark.skip(reason="not ready")
def test_Contact_Email_equals_random_first_name_random_last_name_mailinator_com():
    '''
    15. Assert Contact.Email equals random.first_name.random.last_name@mailinator.com
    '''
    pass


def test_every_is_deleted(session):
    '''
    16. Assert every account is deleted
    '''
    assert cleanup(session)

def test_every_account_is_deleted(session):
    '''
    16. Assert every account is deleted
    '''
    assert not get_accounts(session)

def test_every_contact_is_deleted(session):
    '''
    17. Assert every contact is deleted
    '''
    assert not get_contacts(session)
