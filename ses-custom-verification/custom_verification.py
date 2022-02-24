
import boto3

client = boto3.client('ses', 'us-east-1')

def main():
    print("Custom-Verification")
    create_template()
    list_templates()
    send_verification()

def create_template():
    response = client.create_custom_verification_email_template(
        TemplateName='CustomVerificationTemplate02',
        FromEmailAddress='elux@datum.com.gt',
        TemplateSubject='Bienvenido! Por favor confirma tu correo electrónico',
        TemplateContent="<html><head></head><body style='font-family:sans-serif;'><h1 style='text-align:center'>Ready to start sending email with ProductName?</h1><p>We here at Example Corp are happy to have you on board! There's just one last step to complete before you can start sending email. Just click the following link to verify your email address. Once we confirm that you're really you, we'll give you some additional information to help you get started with ProductName.</p></body></html>",
        SuccessRedirectionURL='https://www.example.com/verifysuccess',
        FailureRedirectionURL='https://www.example.com/verifyfailure'
    )

    print("Create Template")
    print(response)

def list_templates():
    response = client.list_custom_verification_email_templates(
        NextToken='',
        MaxResults=100
    )

    print("List Template")
    print(response)

def send_verification():
    response = client.send_custom_verification_email(
        EmailAddress='ever.lux@itzdata.tech',
        TemplateName='CustomVerificationTemplate02',
        ConfigurationSetName=''
    )

    print("Send Verification")
    print(response)


main()