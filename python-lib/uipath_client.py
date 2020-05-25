import requests

JOB_URL = "https://platform.uipath.com/{account_logical_name}/{tenant_logical_name}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
REFRESH_TOKEN_URL = "https://account.uipath.com/oauth/token"
URL = "https://platform.uipath.com/{account_logical_name}/{tenant_logical_name}"
GET_PROCESSKEY_BY_NAME = "{url}/odata/Releases?$filter=ProcessKey eq '{process_name}'"
GET_ROBOT_BY_NAME = "{url}/odata/Robots?$filter=Name eq '{robot_name}'"
START_JOB = "{url}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
GET_JOBS = "{url}/odata/Jobs"
GET_ROBOT_LOGS = "{url}/odata/RobotLogs"


class UIPathClient(object):

    def __init__(self, config):
        self.config = config
        self.tenant_logical_name = self.config.get("tenant_logical_name")
        self.account_logical_name = self.config.get("account_logical_name")
        self.process_name = self.config.get("process_name")
        self.client_id = self.config.get("client_id")
        refresh_token = self.config.get("refresh_token")
        self.access_token = self.get_access_token(refresh_token)
        self.remaining_records = 0
        self.records_to_skip = 0

    def get_access_token(self, refresh_token):
        headers = self.get_headers(no_auth=True)
        json_data = {
            "grant_type": "refresh_token",
            "client_id": "{}".format(self.client_id),
            "refresh_token": "{}".format(refresh_token)
        }
        json_response = self.post(REFRESH_TOKEN_URL, headers=headers, json=json_data)
        return json_response.get("access_token", None)

    def post(self, url, headers=None, json={}):
        args = {}
        if headers is not None:
            args["headers"] = headers
        if json is not None:
            args["json"] = json
        response = requests.post(url, **args)
        json_response = response.json()
        return json_response

    def get_headers(self, no_auth=False):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UIPATH-TenantName": self.tenant_logical_name
        }
        if not no_auth:
            headers["Authorization"] = "Bearer {access_token}".format(access_token=self.access_token)
        return headers

    def get_process_key_by_name(self, process_name):
        url = URL.format(account_logical_name=self.account_logical_name, tenant_logical_name=self.tenant_logical_name)
        url = GET_PROCESSKEY_BY_NAME.format(url=url, process_name=process_name)
        headers = self.get_headers()
        json_response = self.get(url, headers=headers)
        return json_response["value"][0]["Key"]

    def get(self, url, headers=None, json=None, params=None):
        args = {}
        args["url"] = url
        if headers is not None:
            args["headers"] = headers
        if json is not None:
            args["json"] = json
        if params is not None and params != {}:
            args["params"] = params
        response = requests.get(**args)
        if response.status_code >= 400:
            raise Exception("Error {}: {}".format(response.status_code, response.text))
        json_response = response.json()
        return json_response

    def get_robot_by_name(self, robot_name):
        url = URL.format(account_logical_name=self.account_logical_name, tenant_logical_name=self.tenant_logical_name)
        url = GET_ROBOT_BY_NAME.format(url=url, robot_name=robot_name)
        headers = self.get_headers()
        json_response = self.get(url, headers=headers)
        return json_response["value"][0]["Id"]

    def get_jobs(self, filter=None):
        url = URL.format(account_logical_name=self.account_logical_name, tenant_logical_name=self.tenant_logical_name)
        url = GET_JOBS.format(url=url)
        headers = self.get_headers()
        if filter is None:
            params = None
        else:
            params = {
                "$filter": filter
            }
        json_response = self.get(url, headers=headers, params=params)
        return json_response["value"]

    def get_jobs_by_key(self, job_key):
        jobs = self.get_jobs()
        for job in jobs:
            if job["Key"] == job_key:
                return job
        return None

    def get_robot_logs(self, filter=None, records_limit=-1, skip=0):
        if filter is None or filter == "":
            params = {}
        else:
            params = {
                "$filter": filter
            }
        if records_limit > 0 and records_limit < 1000:  # Cannot request a large amount with $top
            params.update({
                "$top": records_limit
            })
        if skip > 0:
            params.update({
                "$skip": skip
            })
        headers = self.get_headers()
        url = URL.format(
            account_logical_name=self.account_logical_name,
            tenant_logical_name=self.tenant_logical_name
        )
        url = GET_ROBOT_LOGS.format(url=url)
        json_response = self.get(url, headers=headers, params=params)
        self.update_remaining_records(json_response)
        return json_response["value"]

    def update_remaining_records(self, json_response):
        self.records_to_skip = self.records_to_skip + len(json_response["value"])
        self.remaining_records = json_response["@odata.count"] - self.records_to_skip

    def start_job(self, process_id):
        json_data = {
            "startInfo": {
                "ReleaseKey": process_id,
                "RobotIds": [],
                "JobsCount": 1,
                "JobPriority": "Normal",
                "Strategy": "JobsCount",
                "InputArguments": "{}"
            }
        }
        headers = self.get_headers()
        base_url = URL.format(account_logical_name=self.account_logical_name, tenant_logical_name=self.tenant_logical_name)
        url = START_JOB.format(url=base_url)
        json_response = self.post(url, headers=headers, json=json_data)
        return json_response["value"][0]

    def is_finnished(self):
        return self.remaining_records == 0
