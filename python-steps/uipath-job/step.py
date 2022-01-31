import time
import logging
from dataiku.customstep import get_step_config, get_plugin_config, get_step_resource
from uipath_client import UIPathClient, UIPathClientError


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='uipath-orchestrator plugin %(levelname)s - %(message)s')


logger.info("Starting step")
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

# settings at the step instance level (set by the user creating a scenario step)
step_config = get_step_config()
folder_name = step_config.get("folder_name")
robot_name = step_config.get("robot_name")
process_name = step_config.get("process_name")
folder_type = step_config.get("folder_type", "classical")
logger.info(
    "folder_name={}, robot_name={}, process_name={}, folder_type={}".format(
        folder_name,
        robot_name,
        process_name,
        folder_type
    )
)

client = UIPathClient(oauth_token, folder_name=folder_name)

process_id = client.get_process_key_by_name(process_name)
if process_id is None:
    raise ValueError("Process '{}' does not exist".format(process_name))
if folder_type == "classical" and robot_name:
    robot_ids = client.get_robot_by_name(robot_name, folder_type=folder_type)
    logger.info("Robot name '{}' returned id(s) {}".format(robot_name, robot_ids))
else:
    robot_ids = []

job = client.start_job(process_id, robot_ids=robot_ids)
finished = False
while not finished:
    time.sleep(30)
    job_status = client.get_jobs_by_key(job.get("Key"))
    finished = (job_status.get("EndTime") is not None)
    logger.info("Job status: finished={}".format(finished))
    if job_status.get('State') == 'Stopped':
        raise UIPathClientError("Job was stopped from UiPath Orchestrator")
    if job_status.get('State') == 'Faulted':
        raise UIPathClientError("Job was stopped with an error during execution")
