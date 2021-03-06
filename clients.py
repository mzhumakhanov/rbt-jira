from getpass import getpass
import os
import pickle

from jira.client import JIRA
from rbtools.api.client import RBClient


class RBTJIRAClient:
    def __init__(self):
        self.jira_to_rbt_map = self.load_jira_to_rbt_map()
        self.jira_client = self.get_jira_client()
        self.rb_client = self.get_rb_client().get_root()

    def get_post_review_dir(self):
        rbt_jira_dir = os.path.join(os.getenv('HOME'), ".rbt-jira")
        if not os.path.exists(rbt_jira_dir):
            os.mkdir(rbt_jira_dir)
        return rbt_jira_dir

    def valid_jira(self, jira):
        try:
            self.jira_client.issue(jira.upper())
        except:
            raise Exception("jira " + jira + " is not valid")

    def load_jira_to_rbt_map(self):
        map_path = os.path.join(self.get_post_review_dir(), 'jira-to-rbt.map')
        if os.path.exists(map_path):
            with open(map_path) as map_file:
                return pickle.load(map_file)
        return {}

    def save_jira_to_rbt_map(self):
        map_path = os.path.join(self.get_post_review_dir(), 'jira-to-rbt.map')
        with open(map_path, 'w') as map_file:
            pickle.dump(self.jira_to_rbt_map, map_file)

    def put_rb_for_jira(self, jira, rb):
        self.jira_to_rbt_map[jira] = rb
        self.save_jira_to_rbt_map()

    def get_rb_for_jira(self, jira):
        if self.jira_to_rbt_map.has_key(jira.upper()):
            return self.jira_to_rbt_map.get(jira.upper())
        issue = self.jira_client.issue(jira)
        rb_comments = (comment for comment in issue.fields.comment.comments if
                       comment.body.find('reviews.apache.org/r/') > 0)
        rb_ids = set()
        for comment in rb_comments:
            try:
                id = comment.body[comment.body.find("reviews.apache.org/r/") + len("reviews.apache.org/r/"):]
                id = id[:id.find('/')]
                rb_ids.add(int(id))
            except:
                pass
        if len(rb_ids) == 0:
            return None
        elif len(rb_ids) == 1:
            return list(rb_ids)[0]
        else:
            review_requests = []
            for id in rb_ids:
                try:
                    review_request = self.rb_client.get_review_request(review_request_id=id)
                    if review_request.status in ['pending'] and (
                                    jira in review_request.bugs_closed or review_request.summary.find(jira) >= 0):
                        review_requests.append(review_request)
                except:
                    pass
            if len(review_requests) == 0:
                return None
            elif len(review_requests) == 1:
                return review_requests[0].id
            else:
                msg = "Could not determine review request uniquely. Options were: \n"
                for review_request in review_requests:
                    msg += "\t" + str(review_request.id) + ":" + review_request.summary + "(solves " + ','.join(
                        bug for bug in review_request.bugs_closed) + ")\n"
                raise Exception(msg)

    def get_jira_client(self):
        options = {
            'server': 'https://issues.apache.org/jira'
        }
        # read the config file
        post_review_path = self.get_post_review_dir()
        jira_path = os.path.join(post_review_path, "jira")
        if os.path.exists(jira_path):
            with open(jira_path) as jira_file:
                try:
                    jira = pickle.load(jira_file)
                    # this is a hack
                    jira._session.max_retries = 3
                    if jira.session():
                        return jira
                except:
                    pass
        username = raw_input("Enter JIRA Username: ")
        password = getpass("Enter password: ")
        jira = JIRA(options, basic_auth=(username, password))
        with open(jira_path, 'wb') as jira_file:
            pickle.dump(jira, jira_file)
        return jira


    def get_rb_client(self):
        options = {}
        with open(".reviewboardrc") as reviewboardrc:
            for line in reviewboardrc:
                k, v = line.split("=")
                k = k.strip()
                v = eval(v.strip())
                options[k] = v
        rbclient = RBClient(options['REVIEWBOARD_URL'])
        self.repository = options['REPOSITORY']
        self.branch = options['BRANCH']
        self.target_groups = None
        if options.has_key('TARGET_GROUPS'):
            self.target_groups = options['TARGET_GROUPS']
        if rbclient.get_root().get_session()['authenticated']:
            return rbclient
        username = raw_input("Enter review board Username: ")
        password = getpass("Enter password: ")
        rbclient.login(username, password)
        return rbclient
