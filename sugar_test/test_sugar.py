#!/usr/bin/env python
# encoding: utf-8

import os
import re
from random import randint
import generate
import check

import pytest

from sugarcrm import Session, Account, Contact


assert os.environ['SUGAR_CRM_COUNT']
assert os.environ['SUGAR_CRM_URL']
assert os.environ['SUGAR_CRM_USERNAME']
assert os.environ['SUGAR_CRM_PASSWORD']

COUNT = int(os.environ.get('SUGAR_CRM_COUNT'))

@pytest.fixture(scope="module")
def session(request):
    url = os.environ['SUGAR_CRM_URL']
    username = os.environ['SUGAR_CRM_USERNAME']
    password = os.environ['SUGAR_CRM_PASSWORD']
    session = Session(url, username, password)

    # cleanup(session)

    def teardown_module():
        # cleanup(session)
        pass

    request.addfinalizer(teardown_module)
    return session

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
    companys = generate.generate_CompanyName()
    streets = generate.generate_Street()
    citys = generate.generate_City()
    phones = generate.generate_Phone()

    while count <= (COUNT - 1): 
        
        account = create_account(
            session, 
            next(companys),
            next(streets), 
            generate.generate_ZIP(), 
            next(citys), 
            next(phones), 
            generate.generate_Industry()
        )

        for _ in range(randint(1, 10)):
            sex = randint(0, 1)
            if sex:
                first_name = generate.generate_first_name_male()
                last_name = generate.generate_last_name_male()
            else:
                first_name = generate.generate_first_name_female()
                last_name = generate.generate_last_name_female()

            contact = create_contact(
                session, 
                account.id, 
                first_name, 
                last_name, 
                generate.generate_Position(), 
                generate.generate_Email(first_name, last_name), 
                next(phones)
            )
        count+=1

def test_sum_of_created_account_equals_100(session):
    '''
    01. Assert sum of created account equals 100
    '''
    assert len(get_accounts(session)) == COUNT

@pytest.mark.skip(reason="duplicate test")
def test_sum_of_each_child_contact_is_between_1_and_10():
    '''
    02. Assert sum of each child contact is between 1 and 10
    '''
    pass

def test_contact_has_parent_account(session):
    '''
    03. Assert contact has parent account
    '''
    assert all(map(lambda c: c.account_id, get_contacts(session)))

def test_Account_Name_equals_two_words(session):
    '''
    04. Assert Account.Name equals two words
    '''
    assert all(map(lambda a: check.check_account_CompanyName(a.name), get_accounts(session)))

def test_Account_Street_equals_one_word_and_one_digit(session):
    '''
    05. Assert Account.Street equals one word and one digit
    '''
    assert all(map(lambda a: check.check_account_Street(a.billing_address_street), get_accounts(session)))

def test_Account_ZIP_equals_four_digits(session):
    '''
    06. Assert Account.ZIP equals four digits
    '''
    assert all(map(lambda a: check.check_account_ZIP(a.billing_address_postalcode), get_accounts(session)))

def test_Account_City_equals_one_word(session):
    '''
    07. Assert Account.City equals one word
    '''
    assert all(map(lambda a: check.check_account_City(a.billing_address_city), get_accounts(session)))

def test_Account_PhoneNumber_equals_iso164_string(session):
    '''
    08. Assert Account.PhoneNumber equals iso164 string
    '''
    assert all(map(lambda a: check.check_PhoneNumber(a.phone_office), get_accounts(session)))

def test_Account_Industry_equels_Banking_or_Dairy_or_Services(session):
    '''
    09. Assert Account.Industry equels Banking or Dairy or Services
    '''
    assert all(map(lambda a: check.check_account_Industry(a.industry), get_accounts(session)))

def test_Account_ChildContacts_Sum_is_between_0_and_10_child(session):
    '''
    10. Assert Account.ChildContacts.Sum is between 0 and 10 child
    '''
    accounts = get_accounts(session)
    if accounts:
        for account in accounts:
            linked = session.get_entry("Accounts", account.id, links={'Contacts': ['id']})            
            assert (len(linked.contacts) >= 0) and (len(linked.contacts) <= 10)

def test_Contact_FirstName_equals_one_random_first_name(session):
    '''
    11. Assert Contact.FirstName equals one random.first_name
    '''
    names = list(map(lambda c: c.first_name, get_contacts(session)))
    checks = list(map(lambda name: check.check_contact_Firstname(name), names))
    assert all(checks)

def test_Contact_LastName_equals_one_random_last_name(session):
    '''
    12. Assert Contact.LastName equals one random.last_name
    '''
    names = list(map(lambda c: c.last_name, get_contacts(session)))
    checks = list(map(lambda name: check.check_contact_Lastname(name), names))
    assert all(checks)

def test_Contact_Position_equals_CEO_or_CFO_or_CIO(session):
    '''
    13. Assert Contact.Position equals CEO or CFO or CIO
    '''
    assert all(map(lambda c: check.check_contact_Position(c.title), get_contacts(session)))

def test_Contact_PhoneNumber_equals_iso164_string(session):
    '''
    14. Assert Contact.PhoneNumber equals iso164 string
    '''
    assert all(map(lambda c: check.check_PhoneNumber(c.phone_work), get_contacts(session)))

def test_Contact_Email_equals_random_first_name_random_last_name_mailinator_com(session):
    '''
    15. Assert Contact.Email equals random.first_name.random.last_name@mailinator.com
    '''
    checks = list(map(lambda c: check.check_contact_Email(c.email1, c.first_name, c.last_name), get_contacts(session)))
    assert all(checks)


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
