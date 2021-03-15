from aws_cdk import (
    core,
    aws_codepipeline as code_pipeline,
    aws_codepipeline_actions as code_pipeline_actions,
    aws_s3 as s3
)
import os

class EtlCicdStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_artifact = code_pipeline.Artifact(artifact_name="SourceArtifact")
        artifact_bucket = s3.Bucket(
            self,
            'artifact-bucket',
            removal_policy=core.RemovalPolicy.DESTROY
        )

        pipeline = code_pipeline.Pipeline(
            self,
            "etl_pipeline",
            pipeline_name="etl_pipeline",
            restart_execution_on_update=True,
            artifact_bucket=artifact_bucket,
            stages=[
                code_pipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        code_pipeline_actions.GitHubSourceAction(
                            action_name="GithubSource",
                            oauth_token=core.SecretValue.secrets_manager('github-token'),
                            owner=os.environ['GITHUB_OWNER'],
                            branch=os.environ['GITHUB_BRANCH'],
                            repo=os.environ['GITHUB_REPO'],
                            output=s3_artifact
                        )
                    ]
                ),
                code_pipeline.StageProps(
                    stage_name="Deploy",
                    actions=[
                        code_pipeline_actions.S3DeployAction(
                            action_name="S3Deploy",
                            input=s3_artifact,
                            bucket=bucket,
                            extract=True,
                            object_key="cicd"
                        )
                    ]
                )
            ]
        )