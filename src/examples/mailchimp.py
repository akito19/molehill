import os
import sys
import argparse
os.system(f"{sys.executable} -m pip install mailchimp_marketing")
import mailchimp_marketing as Mailchimp
from mailchimp_marketing.api_client import ApiClientError

# FIXME: Change this email address
FROM_EMAIL = "mail@example.com"

def start(audience_name, reason, template_name, campaign_ja, campaign_en, job_id, db, table, email):
    mailchimp = Mailchimp.Client()
    mailchimp.set_config({
        "api_key": os.environ["MAILCHIMP_APIKEY"],
        "server": os.environ["MAILCHIMP_SERVER"]
    })

    accounts = extract_job_result(job_id, db, table, email)

    # Audience
    list_id = create_audience(mailchimp, reason, audience_name)
    add_merge_fields(mailchimp, list_id, accounts, email)
    add_subscriber(mailchimp, list_id, accounts, email)

    # Template
    template_id = upload_template(mailchimp, template_name)

    # Campaign
    create_campaign(mailchimp, template_id, campaign_ja, campaign_en)

def extract_job_result(job_id, db, table, target_email):
    import tdclient
    import json
    import time

    apikey = os.environ["TD_API_KEY"]
    endpoint = os.environ["TD_API_SERVER"]
    with tdclient.Client(apikey=apikey, endpoint=endpoint) as td:
        # job_result_format() doesn't have column_header
        job = td.job(job_id)
        # result_schema returns `[['col1', 'varchar(32)'], ['col2', 'varchar(16)'], ...]` for example.
        headers = list(map(lambda x: x[0], job.result_schema))

        results = []
        target_emails = []
        removed_target = []
        for row in job.result_format('json'):
            dic = dict(zip(headers, row))
            email = dic[target_email]

            # Email duplication leads error below:
            # `Duplicate items found for email foo@email.com, please provide unique email address per member item`
            if email in target_emails:
                removed_target.append(dic)
                continue

            target_emails.append(email)
            results.append(dic)

        print('===== Removed accounts due to duplication =====')
        print(removed_target)
        print('===== Preparing to send removed accoutns to Treasure Data... ======')

        with open('/home/td-user/reject.json', mode='w', encoding='utf-8') as f:
            for target in removed_target:
                target['time'] = int(time.time())
                json.dump(target, f, ensure_ascii=False)
                f.write('\n')
        td.import_file(db, table, "json", "/home/td-user/reject.json")
        print(f'===== Import issued ({db}.{table}) ======')

        return results

# https://mailchimp.com/developer/marketing/api/lists/add-list/
def create_audience(mailchimp, reason, audience_name):
    body = {
        "name": audience_name,
        "permission_reminder": reason,
        "email_type_option": False,
        "campaign_defaults": {
            "from_name": "FROM name", # FIXME: Change from name
            "from_email": FROM_EMAIL,
            "subject": audience_name,
            "language": "EN_US"
        },
        "contact": {
            "company": "Company name, Inc.",
            "address1": "Foo Street.",
            "address2": "",
            "city": "Some City",
            "state": "CA",
            "zip": "123456",
            "country": "US"
        }
    }

    try:
        print("Creating Audience list...")
        response = mailchimp.lists.create_list(body)
        print("Response for Audience creation: {}".format(response))
        return response['id']
    except ApiClientError as error:
        print("An exception occurred: {}".format(error.text))

# https://mailchimp.com/developer/marketing/api/list-merges/add-merge-field/
def add_merge_fields(mailchimp, list_id, accounts, email):
    merge_fields = {}
    for key in list(accounts[0].keys()):
        # The parameter is used for EMAIL.
        if key == email:
            continue

        # Tag lengths have only 10 letters.
        # If you'd like to specify TAG such as MMERGE1, MMERGE2, and etc., add `"key": "MERGE_VAR"` property.
        merge_fields.update({"name": key, "type": "text"})
        try:
            response = mailchimp.lists.add_list_merge_field(list_id, merge_fields)
            print("Response for merge field addition: {}".format(response))
        except ApiClientError as error:
            print("Error: {}".format(error.text))
            sys.exit(1)

# https://mailchimp.com/developer/marketing/api/list-clients/
def add_subscriber(mailchimp, list_id, accounts, email):
    if not list_id:
        print('Error: Failed to get the audience list id')
        sys.exit(1)

    print('Adding notification target...')

    members = []
    columns = list(accounts[0].keys())
    columns.remove(email)
    for accounts_data in accounts:
        member = {
            "email_address": accounts_data[email],
            "email_type": "html",
            "status": "subscribed",
            "merge_fields": {
                # Following items are sample.
                # Start `MMERGE5` because other fields (Fistname, Lastname, Address and Phone Number) are assigned initially.
                # NOTE: Please fix columns by correspoiding your notification target.
                "MMERGE5": accounts_data[columns[0]],
                "MMERGE6": accounts_data[columns[1]],
                "MMERGE7": accounts_data[columns[2]],
                "MMERGE8": accounts_data[columns[3]],
                "MMERGE9": accounts_data[columns[4]]
            }
        }

        print('subscribing...', member)
        members.append(member)

    data = {
        "members": members,
        "update_existing": True
    }

    try:
        response = mailchimp.lists.batch_list_members(list_id, data)
        print("Added subscribers")
    except ApiClientError as error:
        print("Error: {}".format(error.text))
        sys.exit(1)

# https://mailchimp.com/developer/marketing/api/templates/add-template/
def upload_template(mailchimp, template_name):
    try:
        template_file = open('template.html', "r")
        html = template_file.read()
        template = {"name": template_name, "html": html}
        template_file.close()
        response = mailchimp.templates.create(template)
        print("Added the templates")

        return response['id'] # template id
    except ApiClientError as error:
        print("Error: {}".format(error.text))
        sys.exit(1)

# https://mailchimp.com/developer/marketing/api/campaigns/add-campaign/
def create_campaign(mailchimp, template_id, campaign_ja, campaign_en):
    if not template_id:
        print('Error: Failed to get the template id')
        sys.exit(1)

    content_ja = {
        "type": "regular",
        "settings": {
            "subject_line": "subject line",
            "preview_text": "preview text",
            "title": campaign_ja,
            "from_name": "{your_name}",
            "reply_to": FROM_EMAIL,
            "use_conversation": False,
            "to_name": "email_address",
            "template_id": template_id,
            "fb_comments": False
        }
    }

    content_en = {
        "type": "regular",
        "settings": {
            "subject_line": "subject line",
            "preview_text": "preview text",
            "title": campaign_en,
            "from_name": "{your_name}",
            "reply_to": FROM_EMAIL,
            "use_conversation": False,
            "to_name": "email_address",
            "template_id": template_id,
            "fb_comments": False
        }
    }

    try:
        print("Creating a campaing in Japanese version...")
        mailchimp.campaigns.create(content_ja)
        print("Creating a campaing in English version...")
        mailchimp.campaigns.create(content_en)
        print("Campaign created")
    except ApiClientError as error:
        print("Error: {}".format(error.text))
        sys.exit(1)

if __name__ == '__main__':
    # TODO: Fix arguments for your requirements.
    parser = argparse.ArgumentParser()
    parser.add_argument("audience_name", help="Audience name", type=str)
    parser.add_argument("reason", help="Reason why customers get this notification", type=str)
    parser.add_argument("template_name", help="Template name", type=str)
    parser.add_argument("campaign_ja", help="Campaign name (Japanese)", type=str)
    parser.add_argument("campaign_en", help="Campaign name (English)", type=str)
    parser.add_argument("job_id", help="Job ID", type=int)
    parser.add_argument("db", help="Database name for rejected users", type=int)
    parser.add_argument("table", help="Table name for rejected users", type=int)
    parser.add_argument("email", help="Email address", type=str)
    audience_name = args.audience_name
    reason = args.reason
    template_name = args.template_name
    campaign_ja = args.campaign_ja
    campaign_en = args.campaign_en
    job_id = args.job_id
    db = args.db
    table = args.table
    email = args.email

    start(audience_name, reason, template_name, campaign_ja, campaign_en, job_id, email)
