from aws_cdk import (
    aws_iam as iam,
    aws_glue as glue,
    aws_s3 as s3,
    core
)

data_pipeline = {
    "nodes": [
        {
            "id": "nyc_csv_crawler",
            "type": "crawler"
        },
        {
            "id": "csv_to_parquet",
            "type": "job",
            "in": [{
                "name": "nyc_csv_crawler",
                "type": "crawler"
            }]
        },
        {
            "id": "nyc_parquet_crawler",
            "type": "crawler",
            "in": [{
                "name": "csv_to_parquet",
                "type": "job"
            }]
        },
        {
            "id": "parquet_processing",
            'type': "job",
            "in": [
                {
                    "name": "nyc_parquet_crawler",
                    "type": "crawler"
                }
            ]
        }
    ]
}

class DataPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            'nyc-bucket',
            removal_policy=core.RemovalPolicy.DESTROY
        )

        glue_role = iam.Role(
            self,
            'glue-role',
            assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSGlueServiceRole'),
                              iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess')]
        )

        csv_crawler = glue.CfnCrawler(
            self,
            'nyc_csv_crawler',
            name='nyc_csv_crawler',
            role=glue_role.role_arn,
            database_name='nyc_db',
            table_prefix='csv_',
            targets={
                's3Targets': [{
                    "path": "s3://nyc-tlc/trip data/",
                    "exclusions": ["fhv*", "green_*"]
                }],
            },
            configuration='{"Version":1.0,"CrawlerOutput": {"Partitions": { "AddOrUpdateBehavior": "InheritFromTable" }}}'
        )

        csv_to_parquet_command = glue.CfnJob.JobCommandProperty(
            name="glueetl",
            script_location=f"s3://{self.bucket.bucket_name}/cicd/src/csv_to_parquet.py"
        )

        csv_to_parquet_job = glue.CfnJob(
            self,
            "csv_to_parquet",
            name="csv_to_parquet",
            command=csv_to_parquet_command,
            default_arguments={
                "--bucket": self.bucket.bucket_name,
            },
            role=glue_role.role_name,
            glue_version="2.0",
            worker_type="Standard",
            number_of_workers=20,
        )

        parquet_crawler = glue.CfnCrawler(
            self,
            "nyc_parquet_crawler",
            name="nyc_parquet_crawler",
            role=glue_role.role_arn,
            database_name="nyc_db",
            table_prefix="parquet_",
            targets={
                's3Targets':[{"path": f"s3://{self.bucket.bucket_name}"}]
            }
        )

        parquet_processing_command = glue.CfnJob.JobCommandProperty(
            name="glueetl",
            script_location=f"s3://{self.bucket.bucket_name}/cicd/src/parquet_processing.py"
        )
        parquet_processing_job = glue.CfnJob(
            self,
            "parquet_processing",
            name="parquet_processing",
            command=parquet_processing_command,
            default_arguments={
                "--bucket": self.bucket.bucket_name,
                "--prefix": "parquet",
                "--additional-python-modules": "pyarrow,pandas==1.2.3,fsspec==0.7.4"
            },
            role=glue_role.role_name,
            glue_version="2.0",
            worker_type="G.1X",
            number_of_workers=20,
        )

        glue_workflow = glue.CfnWorkflow(
            self,
            "nyc_workflow",
            name="nyc_workflow"
        )

        last_trigger = None
        for node in data_pipeline['nodes']:
            if node['type'] == "crawler":
                action_property = glue.CfnTrigger.ActionProperty(crawler_name=node['id'])
            elif node['type'] == "job":
                action_property = glue.CfnTrigger.ActionProperty(job_name=node['id'])
            else:
                print("Not supported yet")

            if "in" not in node:
                trigger = glue.CfnTrigger(
                    self,
                    "on_demand_trigger",
                    workflow_name=glue_workflow.name,
                    actions=[action_property],
                    type="ON_DEMAND"
                )
            else:
                condition_list = []
                for event in node['in']:
                    if event['type'] == "crawler":
                        condition_list = condition_list + [glue.CfnTrigger.ConditionProperty(crawler_name=event['name'],
                                                                             crawl_state="SUCCEEDED",
                                                                             logical_operator="EQUALS")]
                    elif event['type'] == "job":
                        condition_list = condition_list + [glue.CfnTrigger.ConditionProperty(job_name=event['name'],
                                                                             state="SUCCEEDED",
                                                                             logical_operator="EQUALS")]

                predicate = glue.CfnTrigger.PredicateProperty(conditions=condition_list, logical="AND")

                trigger = glue.CfnTrigger(
                    self,
                    f"trigger-{node['id']}",
                    name=f"trigger-{node['id']}",
                    workflow_name=glue_workflow.name,
                    actions=[action_property],
                    type="CONDITIONAL",
                    predicate=predicate,
                    start_on_creation=True
                )
            if last_trigger:
                last_trigger.add_depends_on(trigger)
            last_trigger=trigger