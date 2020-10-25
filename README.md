# MDIT_regQuest-GRA-Enrich


## Getting Started

In order to deploy your CloudFormation template you will need to create an AWS deployment pipeline.
Navigate to [Lilly Cloud](https://lillycloud.global.lilly.com/) and choose *Code Deployment Pipeline* under *AWS Services*.
Once your pipeline has been created you will be able to deploy your template just by pushing code to GitHub.

## Special Notes

- The `params.dev.json`, `params.qa.json`, and `params.prod.json` files are required. They allow you to pass parameters and tags to your CloudFormation template.
- The `deployment-tests/` directory is required and must have at least one shell script in it. These scripts can be used to test your CloudFormation stack deployment.
- Your CloudFormation template must be placed in the `template.yml` file. It is the only file executed by CloudFormation.
- You must apply a permissions boundary to any IAM role created in order for your template to successfully deploy. Details are in the example template file.
