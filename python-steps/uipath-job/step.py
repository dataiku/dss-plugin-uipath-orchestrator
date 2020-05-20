import time
from dataiku.customstep import get_step_config, get_plugin_config, get_step_resource
from uipath_client import UIPathClient

# the plugin's resource folder path (string)
resource_folder = get_step_resource()

# settings at the plugin level (set by plugin administrators in the Plugins section)
plugin_config = get_plugin_config()

config = plugin_config.get("config")
oauth_token = config.get("oauth-token")
account_logical_name = oauth_token.get("account_logical_name")
tenant_logical_name = oauth_token.get("tenant_logical_name")
client_id = oauth_token.get("client_id")
refresh_token = oauth_token.get("refresh_token")
client = UIPathClient(oauth_token)

# settings at the step instance level (set by the user creating a scenario step)
step_config = get_step_config()
robot_name = step_config.get("robot_name")
process_name = step_config.get("process_name")

process_id = client.get_process_key_by_name(process_name)
robot_id = client.get_robot_by_name(robot_name)

job = client.start_job(process_id)
finished = False
while not finished:
    time.sleep(30)
    job_status = client.get_jobs_by_key(job.get("Key"))
    finished = (job_status["EndTime"] is not None)
    if job_status['State'] == 'Stopped':
        raise Exception("Job was stoped from UiPath Orchestrator")

# ALX:job_id=6334559, job_key=6e2bc7e0-2a87-41b0-b864-606df5fc1a98  ->
# https://cloud.uipath.com/dataiku/DataikuDefault/jobs?fid=194740&tid=193970&index=0&size=10&state=GYSwNgLgpgTgzgHwMYygQwiA9gOwCogC2UCAbmmAK4lhoBGUYCAMmnBANQAmaAngnCwwICUIy4IuIVEky5JUOEgB6ARmXKAJAAYEm1XoBMCAJwIAzAgAsAXRsIArHoBsCAwHYEADjtA%3D
