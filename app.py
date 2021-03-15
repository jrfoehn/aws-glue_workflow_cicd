#!/usr/bin/env python3

from aws_cdk import core
from infra.data_pipeline_stack import DataPipelineStack
from infra.etl_cicd_stack import EtlCicdStack
# from infra.glue_python_shell_stack import LabsGlueWorfklowCicdStack


app = core.App()
# LabsGlueWorfklowCicdStack(app, "labs-glue-worfklow-cicd")
dp_stack = DataPipelineStack(app, "data-pipeline-stack", env={'region': 'eu-west-1'})
etl_stack = EtlCicdStack(app, "etl-cicd-stack", dp_stack.bucket,env={"region": "eu-west-1"})
etl_stack.add_dependency(dp_stack)
app.synth()
