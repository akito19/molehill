import os
import sys
import argparse
os.system(f"{sys.executable} -m pip install mailchimp_marketing")
import mailchimp_marketing as Mailchimp
from mailchimp_marketing.api_client import ApiClientError

# FIXME: Change this email address
FROM_EMAIL = "mail@example.com"

def _isja(lang_ja):
    if lang_ja == 'true':
        return True
    else:
        return False

def _isen(lang_en):
    if lang_en == 'true':
        return True
    else:
        return False

def start(
        audience_name,
        reason,
        template_name_ja,
        template_name_en,
        template_file_ja,
        template_file_en,
        campaign_ja,
        campaign_en,
        from_name,
        job_id, db, table, email):
    mailchimp = Mailchimp.Client()
    mailchimp.set_config({
        "api_key": os.environ["MAILCHIMP_APIKEY"],
        "server": os.environ["MAILCHIMP_SERVER"]
    })

    accounts = extract_job_result(job_id, db, table, email)

    # Audience
    list_id = create_audience(mailchimp, reason, audience_name, from_name)
    add_merge_fields(mailchimp, list_id, accounts, email)
    add_subscriber(mailchimp, list_id, accounts, email)

    ja = _isja(lang_ja)
    en = _isen(lang_en)
    # Template
    templates = []
    if ja and en:
        template_list = [
            {"name": template_name_ja, "file": template_file_ja, "lang": JAPANESE},
            {"name": template_name_en, "file": template_file_en, "lang": ENGLISH}
        ]
        for template_info in template_list:
            tid = upload_template(mailchimp, template_info)
            template = {"id": tid, "lang": template_info["lang"]}
            templates.append(template)

        ## Campaign
        create_campaign(mailchimp, templates, from_name, campaign_ja, campaign_en)
    elif ja:
        template = {"name": template_name_ja, "file": template_file_ja, "lang": JAPANESE}
        tid = upload_template(mailchimp, template)
        tmpl = {"id": tid, "lang": template["lang"]}
        templates.append(tmpl)

        ## Campaign
        create_campaign(mailchimp, templates, from_name, title_ja=campaign_ja)
    elif en:
        template = {"name": template_name_en, "file": template_file_en, "lang": ENGLISH}
        tid = upload_template(mailchimp, template)
        tmpl = {"id": tid, "lang": template["lang"]}
        templates.append(tmpl)

        ## Campaign
        create_campaign(mailchimp, templates, from_name, title_en=campaign_en)
    else:
        print("Invalid Language settings")
        sys.exit(1)

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

        # Mailchimp restricts 500 items each upload.
        return list(_split_list(result, 500))

def _split_list(lst, num):
    for idx in range(0, len(lst), num):
        yield lst[idx:idx + num]

# https://mailchimp.com/developer/marketing/api/lists/add-list/
def create_audience(mailchimp, reason, audience_name, from_name):
    body = {
        "name": audience_name,
        "permission_reminder": reason,
        "email_type_option": False,
        "campaign_defaults": {
            "from_name": from_name,
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
    tags = json.loads(mmerges).values()
    idx = 0
    for key in list(accounts[0].keys()):
        # The parameter is used for EMAIL.
        if key == email:
            continue

        merge_fields.update({"name": key, "type": "text", "tag": list(tags)[idx]})
        idx += 1

        try:
            response = mailchimp.lists.add_list_merge_field(list_id, merge_fields)
            print("Response for merge field addition: {}".format(response))
        except ApiClientError as error:
            print("Error: {}".format(error.text))
            sys.exit(1)

def _val(val):
    if val is None:
        return ''
    else:
        return val

# https://mailchimp.com/developer/marketing/api/list-clients/
def add_subscriber(mailchimp, list_id, accounts, email):
    if not list_id:
        print('Error: Failed to get the audience list id')
        sys.exit(1)

    print('Adding notification target...')

    columns = list(account_set[0][0].keys())
    columns.remove(email)
    for accounts in account_set:
        members = []
        for account_data in accounts:
            mmerge = {}
            for idx, val in enumerate(json.loads(mmerges).values()):
                mmerge.update({val: _val(account_data[columns[idx]])})
            member = {
                "email_address": account_data[email],
                "email_type": "html",
                "status": "subscribed",
                "merge_fields": mmerge
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
def create_campaign(mailchimp, template_id, from_name, title_ja=None, title_en=None):
     for template in templates:
        if not template["id"]:
            print('Error: Failed to get the template id')
            sys.exit(1)

        if template["lang"] == JAPANESE:
            content = {
                "type": "regular",
                "settings": {
                    "subject_line": "subject line",
                    "preview_text": "preview text",
                    "title": title_ja,
                    "from_name": "Treasure Data Support",
                    "reply_to": SUPPORT_EMAIL,
                    "use_conversation": False,
                    "to_name": "email_address",
                    "template_id": template["id"],
                    "fb_comments": False
                }
            }

            print("Creating a campaign in Japanese version...")
            _create_campaign(mailchimp, content)
            print("Finished.")
        else:
            content = {
                "type": "regular",
                "settings": {
                    "subject_line": "subject line",
                    "preview_text": "preview text",
                    "title": title_en,
                    "from_name": "Treasure Data Support",
                    "reply_to": SUPPORT_EMAIL,
                    "use_conversation": False,
                    "to_name": "email_address",
                    "template_id": template["id"],
                    "fb_comments": False
                }
            }

            print("Creating a campaign in English version...")
            _create_campaign(mailchimp, content)
            print("Finished.")

def _create_campaign(mailchimp, content):
    try:
        mailchimp.campaigns.create(content)
    except ApiClientError as error:
        print("Error: {}".format(error.text))
        sys.exit(1)

if __name__ == '__main__':
    # TODO: Fix arguments for your requirements.
    parser = argparse.ArgumentParser()
    parser.add_argument("audience_name", help="Audience name", type=str)
    parser.add_argument("reason", help="Reason why customers get this notification", type=str)
    parser.add_argument("mmerges", help="merge_vars", type=str)
    parser.add_argument("template_name_ja", help="Template name (JA)", type=str)
    parser.add_argument("template_name_en", help="Template name (EN)", type=str)
    parser.add_argument("template_file_ja", help="Template HTML file name", type=str)
    parser.add_argument("template_file_en", help="Template HTML file name", type=str)
    parser.add_argument("campaign_ja", help="Campaign name (Japanese)", type=str)
    parser.add_argument("campaign_en", help="Campaign name (English)", type=str)
    parser.add_argument("lang_ja", help="Language (JA)", type=str)
    parser.add_argument("lang_en", help="Language (EN)", type=str)
    parser.add_argument("from_name", help="Set Email 'from'", type=str)
    parser.add_argument("job_id", help="Job ID", type=int)
    parser.add_argument("db", help="Database name for rejected users", type=int)
    parser.add_argument("table", help="Table name for rejected users", type=int)
    parser.add_argument("email", help="Email address", type=str)
    audience_name = args.audience_name
    reason = args.reason
    mmerges = args.mmerges
    template_name_ja = args.template_name_ja
    template_name_en = args.template_name_en
    template_file_ja = args.template_file_ja
    template_file_en = args.template_file_en
    campaign_ja = args.campaign_ja
    campaign_en = args.campaign_en
    lang_ja = args.lang_ja
    lang_en = args.lang_en
    from_name = args.from_name
    job_id = args.job_id
    db = args.db
    table = args.table
    email = args.email

    start(
        audience_name, reason, mmerges, template_name_ja, template_name_en,
        template_file_ja, template_file_en, campaign_ja, campaign_en,
        lang_ja, lang_en, from_name, job_id, db, table, email
    )
