# PoC Setup Instructions

This README provides step-by-step instructions to set up a Proof of Concept (PoC) environment for an Airflow-based workflow on AWS infrastructure. Follow these instructions to successfully configure and deploy the required components.

## Prerequisites

Before starting the PoC setup, ensure you have the following prerequisites in place:

- AWS CLI installed and configured with necessary permissions.
- `eksctl` installed to interact with Amazon EKS.
- `helm` installed to manage Kubernetes applications.
- AWS Batch and EBS CSI EKS plugin knowledge and setup familiarity.

## Step 1: Assume a Valid Role

Assume a valid role in infrastructure-engineering using the AWS CLI:

`aws sts assume-role --role-arn {role-arn} --role-session-name {role-session-name}`


## Step 2: Deploy Infrastructure Stack

Deploy the infrastructure stack using the CloudFormation template located at `/templates/stack.yaml`:

`aws cloudformation deploy --stack-name airflow-poc --template-file templates/stack.yaml`


## Step 3: Connect to the EKS Cluster

Once the stack is deployed, connect to the EKS cluster:

`aws eks update-kubeconfig --region us-east-1 --name airflow-poc-cluster`



## Step 4: Check Cluster Health

Check that the cluster is in a healthy state by running:

```shell
$ kubectl get nodes
NAME                            STATUS   ROLES    AGE   VERSION
ip-172-31-3-35.ec2.internal     Ready    <none>   25m   v1.27.4-eks-8ccc7ba
ip-172-31-31-104.ec2.internal   Ready    <none>   25m   v1.27.4-eks-8ccc7ba
ip-172-31-64-131.ec2.internal   Ready    <none>   26m   v1.27.4-eks-8ccc7ba
ip-172-31-64-87.ec2.internal    Ready    <none>   25m   v1.27.4-eks-8ccc7ba
```

## Step 5: Add OIDC Provider Trusted Entity

Manually add an OIDC provider trusted entity to the EBSCSI Driver policy using the EKS cluster OIDC provider ID. Use the following JSON policy as a reference:

```json
{
    "Effect": "Allow",
    "Principal": {
        "Federated": "arn:aws:iam::763216446258:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/27E460D354237B681F8F60D14F0CE780"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
        "StringEquals": {
            "oidc.eks.us-east-1.amazonaws.com/id/27E460D354237B681F8F60D14F0CE780:sub": "system:serviceaccount:kube-system:ebs-csi-controller-sa"
        }
    }
}
```

## Step 6: Install EBS CSI EKS Plugin

Install the EBS CSI EKS plugin using `eksctl`:

```shell
eksctl create addon --name aws-ebs-csi-driver \ 
  --cluster airflow-poc-cluster \
  --service-account-role-arn arn:aws:iam::763216446258:role/AirflowPocEBSCSIDriverRole \
  --force
```

Check that the plugin is working by following the [official AWS documentation guide](https://docs.aws.amazon.com/eks/latest/userguide/ebs-sample-app.html).

## Step 7: Install Airflow Helm Chart

Install the Airflow Helm chart:

`helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace`

**Note**: If the apache-airflow repository is not installed, run the appropriate command to install it:

`helm repo add apache-airflow https://airflow.apache.org`

## Step 8: Prepare EKS Cluster for AWS Batch

Follow the [AWS Batch documentation](https://docs.aws.amazon.com/batch/latest/userguide/getting-started-eks.html#getting-started-eks-step-1) to prepare your EKS cluster for AWS Batch.

## Step 9: Configure Airflow

Configure Airflow by updating the Airflow configuration. In this repository, you can find a sample configuration in the `airflow-config` folder. To apply it, run:

`helm upgrade --install airflow apache-airflow/airflow -f ./airflow-config/values.yaml`

Ensure that you have SSH authentication set up for Git synchronization if you enable git-sync in your configuration.

That's it! Your PoC environment for Airflow on AWS infrastructure should now be set up and ready for use.

## Step 10: Update User Role Trust Policy

Update the user role trust policy so that Airflow can assume the appropriate role.

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "eks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "batch.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::763216446258:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/47101D85FBCB245BADEED8CA4736785A"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "oidc.eks.us-east-1.amazonaws.com/id/47101D85FBCB245BADEED8CA4736785A:aud": "sts.amazonaws.com",
                    "oidc.eks.us-east-1.amazonaws.com/id/47101D85FBCB245BADEED8CA4736785A:sub": "system:serviceaccount:flyte:flyte-backend-flyte-binary"
                }
            }
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::763216446258:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/47101D85FBCB245BADEED8CA4736785A"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "oidc.eks.us-east-1.amazonaws.com/id/47101D85FBCB245BADEED8CA4736785A:aud": "sts.amazonaws.com"
                }
            }
        }
	]
}```