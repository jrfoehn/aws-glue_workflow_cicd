#!/usr/bin/env python3

from aws_cdk import core

from labs_glue_worfklow_cicd.labs_glue_worfklow_cicd_stack import LabsGlueWorfklowCicdStack


app = core.App()
LabsGlueWorfklowCicdStack(app, "labs-glue-worfklow-cicd")

app.synth()
