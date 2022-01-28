import aws_cdk as core
import aws_cdk.assertions as assertions
from cdk.cdk_stack import CdkStack

def test_lambda_created():
    app = core.App()
    stack = CdkStack(app, "aws-lambda-cdk")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "main.handler"
    })
