from dataiku.connector import Connector
from uipath_client import UIPathClient


class MyConnector(Connector):

    def __init__(self, config, plugin_config):
        Connector.__init__(self, config, plugin_config)  # pass the parameters to the base class

        self.access_type = config.get("access_type", "oauth-token")
        self.connection_details = config.get(self.access_type)
        self.account_logical_name = config.get("account_logical_name")
        self.filter = config.get("filter", None)
        folder_name = config.get("folder_name", None)
        self.client = UIPathClient(self.connection_details, folder_name)

    def get_read_schema(self):

        # In this example, we don't specify a schema here, so DSS will infer the schema
        # from the columns actually returned by the generate_rows method
        return None

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                      partition_id=None, records_limit=-1):

        logs = self.client.get_robot_logs(filter=self.filter, records_limit=records_limit)
        while True:
            for row in logs:
                row.pop("RawMessage", None)
                yield row
            if not self.client.is_finished():
                logs = self.client.get_robot_logs(filter=self.filter, records_limit=records_limit, skip=self.client.records_to_skip)
            else:
                break

    def get_writer(self, dataset_schema=None, dataset_partitioning=None,
                   partition_id=None):
        """
        Returns a writer object to write in the dataset (or in a partition).

        The dataset_schema given here will match the the rows given to the writer below.

        Note: the writer is responsible for clearing the partition, if relevant.
        """
        raise Exception("Unimplemented")

    def get_partitioning(self):
        """
        Return the partitioning schema that the connector defines.
        """
        raise Exception("Unimplemented")

    def list_partitions(self, partitioning):
        """Return the list of partitions for the partitioning scheme
        passed as parameter"""
        return []

    def partition_exists(self, partitioning, partition_id):
        """Return whether the partition passed as parameter exists

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("Unimplemented")

    def get_records_count(self, partitioning=None, partition_id=None):
        """
        Returns the count of records for the dataset (or a partition).

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("Unimplemented")
