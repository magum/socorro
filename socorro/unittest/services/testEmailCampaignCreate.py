import socorro.unittest.testlib.expectations as expect
import socorro.services.emailCampaignCreate as ecc
import socorro.lib.util as util

from socorro.database.schema import EmailCampaignsTable

from datetime import datetime, timedelta

#-----------------------------------------------------------------------------------------------------------------
def getDummyContext():
  context = util.DotDict()
  context.databaseHost = 'fred'
  context.databaseName = 'wilma'
  context.databaseUserName = 'ricky'
  context.databasePassword = 'lucy'
  context.databasePort = 127
  context.smtpHostname = 'localhost'
  context.smtpPort = 25
  context.smtpUsername = None
  context.smtpPassword = None
  context.unsubscribeBaseUrl = 'http://example.com/unsubscribe/%s'
  context.fromEmailAddress = 'from@example.com'
  return context

#-----------------------------------------------------------------------------------------------------------------
def testCreateEmailCampaign():
  context = getDummyContext()

  product = 'Foobar'
  versions = '5'
  signature = 'JohnHancock'
  start_date = datetime.now()
  end_date = datetime.now() + timedelta(hours=1)
  # FIXME where should this go?
  end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
  subject = 'test subject'
  body = 'test body'
  author = 'John Doe'
  email_count = 0

  parameters = {
    'product': product,
    'versions': versions,
    'signature': signature,
  }

  version_clause = ''
  if len(versions) > 0:
    version_clause = " version IN %(versions)s AND "

  sql = """
        SELECT DISTINCT contacts.id, reports.email, contacts.subscribe_token
        FROM reports
        LEFT JOIN email_contacts AS contacts ON reports.email = contacts.email
        WHERE TIMESTAMP WITHOUT TIME ZONE '%s' <= reports.date_processed AND
              TIMESTAMP WITHOUT TIME ZONE '%s' > reports.date_processed AND
              reports.product = %%(product)s AND
              %s
              reports.signature = %%(signature)s AND
              LENGTH(reports.email) > 4 AND
              contacts.subscribe_status IS NOT FALSE
              AND contacts.email NOT IN (
                  SELECT contacted.email
                  FROM email_campaigns AS prev_campaigns
                  JOIN email_campaigns_contacts ON email_campaigns_contacts.email_campaigns_id = prev_campaigns.id
                  JOIN email_contacts AS contacted ON email_campaigns_contacts.email_contacts_id = contacted.id
                  WHERE prev_campaigns.product = %%(product)s
                  AND prev_campaigns.signature = %%(signature)s
             ) """ % (start_date, end_date, version_clause)

  dummyCursor = expect.DummyObjectWithExpectations()
  dummyCursor.expect('execute', (sql, parameters), {}, None)
  dummyCursor.expect('fetchall', (), {}, [['0','one@example.com','']])

  parameters = [product, versions, signature, subject, body, start_date, end_date, email_count, author]
  logger = util.FakeLogger()
  table = EmailCampaignsTable(logger)
  sql = table.insertSql
  dummyCursor.expect('execute', (sql, parameters), {}, None)
  dummyCursor.expect('fetchone', (), {}, ['1234'])

  campaign = ecc.EmailCampaignCreate(context)
  campaignId = campaign.create_email_campaign(dummyCursor, product, versions, signature, subject, body, start_date, end_date, author)
  assert campaignId == ('1234', [{'token': '', 'id': '0', 'email': 'one@example.com'}])

#-----------------------------------------------------------------------------------------------------------------
def testDetermineEmails():
  context = getDummyContext()

  product = 'Foobar'
  versions = '5'
  signature = 'JohnHancock'
  start_date = datetime.now()
  end_date = datetime.now() + timedelta(hours=1)

  parameters = {
    'product': product,
    'versions': versions,
    'signature': signature,
  }

  version_clause = ''
  if len(versions) > 0:
    version_clause = " version IN %(versions)s AND "

  sql = """
        SELECT DISTINCT contacts.id, reports.email, contacts.subscribe_token
        FROM reports
        LEFT JOIN email_contacts AS contacts ON reports.email = contacts.email
        WHERE TIMESTAMP WITHOUT TIME ZONE '%s' <= reports.date_processed AND
              TIMESTAMP WITHOUT TIME ZONE '%s' > reports.date_processed AND
              reports.product = %%(product)s AND
              %s
              reports.signature = %%(signature)s AND
              LENGTH(reports.email) > 4 AND
              contacts.subscribe_status IS NOT FALSE
              AND contacts.email NOT IN (
                  SELECT contacted.email
                  FROM email_campaigns AS prev_campaigns
                  JOIN email_campaigns_contacts ON email_campaigns_contacts.email_campaigns_id = prev_campaigns.id
                  JOIN email_contacts AS contacted ON email_campaigns_contacts.email_contacts_id = contacted.id
                  WHERE prev_campaigns.product = %%(product)s
                  AND prev_campaigns.signature = %%(signature)s
             ) """ % (start_date, end_date, version_clause)


  dummyCursor = expect.DummyObjectWithExpectations()
  dummyCursor.expect('execute', (sql, parameters), {}, None)
  dummyCursor.expect('fetchall', (), {}, [])

  campaign = ecc.EmailCampaignCreate(context)
  email_rows = campaign.determine_emails(dummyCursor, product, versions, signature, start_date, end_date)

def testEnsureContacts():
  context = getDummyContext()

  parameters = [('me@example.com', 'abcdefg')]
  sql = """INSERT INTO email_contacts (email, subscribe_token) VALUES (%s, %s) RETURNING id"""
  dummyCursor = expect.DummyObjectWithExpectations()
  dummyCursor.expect('executemany', (sql, parameters), {}, None)

  # with dbID already set
  campaign = ecc.EmailCampaignCreate(context)
  email_rows = [['1234', 'me@example.com', 'abcdefg']]
  full_email_rows = campaign.ensure_contacts(dummyCursor, email_rows)
  assert full_email_rows == [{'token': 'abcdefg', 'id': '1234', 'email': 'me@example.com'}]

  # without dbID set
  email_rows = [[None, 'me@example.com', None]]
  full_email_rows = campaign.ensure_contacts(dummyCursor, email_rows, 'abcdefg')
  assert full_email_rows == [{'token': 'abcdefg', 'id': None, 'email': 'me@example.com'}]

def testSaveCampaign():
  context = getDummyContext()

  product = 'Foobar'
  versions = '5'
  signature = 'JohnHancock'
  subject = 'email subject'
  body = 'email body'
  start_date = datetime.now()
  end_date = datetime.now() + timedelta(hours=1)
  author = 'me@example.com'
  email_count = 0

  parameters = (product, versions, signature, subject, body, start_date, end_date, email_count, author)

  sql =  """INSERT INTO email_campaigns (product, versions, signature, subject, body, start_date, end_date, email_count, author)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"""

  dummyCursor = expect.DummyObjectWithExpectations()
  dummyCursor.expect('execute', (sql, list(parameters)), {}, None)
  dummyCursor.expect('fetchone', (), {}, ['123'])

  campaign = ecc.EmailCampaignCreate(context)
  campaignId = campaign.save_campaign(dummyCursor, product, versions, signature, subject, body, start_date, end_date, author)

  assert campaignId == '123'

