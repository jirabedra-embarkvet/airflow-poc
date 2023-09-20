In order to run the PoC:
1. assume a valid role in infrastructure-engineering in a terminal 
aws sts assume-role --role-arn {role-arn} --role-session-name {role-session-name}
2. deploy the infra stack using the /templates/stack.yaml CloudFormation template
aws cloudformation deploy --stack-name airflow-poc --template-file templates/stack.yaml
3. Once the stack is deployed connect to the cluster
aws eks update-kubeconfig --region us-east-1 --name airflow-poc-cluster
4. Check that the cluster is in a healthy state. A healthy cluster may look like this
NAME                            STATUS   ROLES    AGE   VERSION
ip-172-31-3-35.ec2.internal     Ready    <none>   25m   v1.27.4-eks-8ccc7ba
ip-172-31-31-104.ec2.internal   Ready    <none>   25m   v1.27.4-eks-8ccc7ba
ip-172-31-64-131.ec2.internal   Ready    <none>   26m   v1.27.4-eks-8ccc7ba
ip-172-31-64-87.ec2.internal    Ready    <none>   25m   v1.27.4-eks-8ccc7ba
5. Manually add OIDC provider trusted entity to EBSCSI Driver policy
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
using the EKS cluster OIDC provider id.
6. Install EBS CSI EKS plugin
eksctl create addon --name aws-ebs-csi-driver --cluster airflow-poc-cluster --service-account-role-arn arn:aws:iam::763216446258:role/AirflowPocEBSCSIDriverRole --force
Check that the plugin is working by following https://docs.aws.amazon.com/eks/latest/userguide/ebs-sample-app.html guide
7. Install Airflow Helm chart
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace
8. Prepare EKS cluster for AWS Batch
Follow https://docs.aws.amazon.com/batch/latest/userguide/getting-started-eks.html#getting-started-eks-step-1
9. Configure Airflow by updating Airflow config. In this repo, in airflow-config folder there is a sample configuration.

Follow
https://blog.devgenius.io/setting-up-apache-airflow-on-kubernetes-with-gitsync-beaac2e397f3

To apply it run 
helm upgrade --install airflow apache-airflow/airflow -f ./airflow-config/values.yaml
In particular, enabling git-sync requires SSH auth to the repo to sync.

10. Update the user role trust policy so that Airflow can assume the appropriate role.
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
}

updating the OIDC Ids with the eks cluster's
11. Before craeating batch resources in EKS, follow https://docs.aws.amazon.com/batch/latest/userguide/getting-started-eks.html#getting-started-eks-step-1