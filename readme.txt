In order to run the PoC:
1. assume a valid role in infrastructure-engineering in a terminal 
aws sts assume-role --role-arn {role-arn} --role-session-name {role-session-name}
2. deploy the infra stack using the stack.yaml CloudFormation template
aws cloudformation deploy --stack-name airflow-poc --template-file templates/stack.yaml
3. Once the stack is deployed connect to the cluster
aws eks update-kubeconfig --region us-east-1 --name airflow-poc-cluster
4. Check that the cluster is in a healthy state. A healthy cluster may look like this
NAME                            STATUS   ROLES    AGE   VERSION
ip-172-31-3-35.ec2.internal     Ready    <none>   25m   v1.27.4-eks-8ccc7ba
ip-172-31-31-104.ec2.internal   Ready    <none>   25m   v1.27.4-eks-8ccc7ba
ip-172-31-64-131.ec2.internal   Ready    <none>   26m   v1.27.4-eks-8ccc7ba
ip-172-31-64-87.ec2.internal    Ready    <none>   25m   v1.27.4-eks-8ccc7ba


