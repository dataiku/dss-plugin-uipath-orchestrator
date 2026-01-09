# UiPath Orchestrator Plugin

This Dataiku DSS plugin lets you import robot logs from your [UiPath Orchestrator](https://www.uipath.com/) account.


## How to set up

1.  From the Automation Cloud interface, click on **Admin \> Tenants \> Use the caret to unfold your tenant \> API Access (cloud icon)**, and copy the user key, account logical name, tenant logical name and client ID.  

2.  From DSS, click on **Plugin \> UiPath Orchestrator \> Settings \> UiPath oauth token \> Add preset**. Name the preset and add all the details copied from step 1.

## How to use

### Robot logs connector

In a DSS flow, click **Dataset \> UiPath Orchestrator \> UiPath Robot logs**. In the **Token API access** selector, pick the preset created in step 2. If folders are being used in your service, you may have to had the robot’s folder name. Finally, press **Test & get schema** and **Create**.

### Scenario step

To create a scenario step, you will need the name of the process you want to run as well as the name of the robot you want to use to execute the process.

- To find the process name, go to **Automation Cloud \> Your service \> Your process \> … \> View Process**.
- There, copy the name of the package.
- To find the robot name, go to **Automation Cloud \> Your service \> Management \> Robots**. In order to be used by DSS, the robot type must be set to **Unattended**.
- In your project’s flow, select Scenario \> New scenario. Once the scenario named and created, go to its **Steps** tab, add a step of the **UiPath Job** type. Pick the Token API access preset created in step 2, and complete the Process and Robot name with the information found earlier.
- You can now start the process on the robot from your DSS step. However, it is not possible to abort the job from DSS. To do so, you have to go to the process page on your UiPath Orchestrator interface.

### Licence

Copyright 2021-2022 Dataiku SAS

This plugin is distributed under the Apache License version 2.0
