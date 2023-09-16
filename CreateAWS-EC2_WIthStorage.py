import pulumi
import pulumi_aws as aws

instance_name = 'instance-name-goes-here'
instance_type = 't2.micro'
ami_id = 'ami-id-goes-here'

# Create a security group that allows SSH and web traffic
secgrp = aws.ec2.SecurityGroup("secgrp",
    description='Allow SSH and web traffic',
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_blocks=['0.0.0.0/0'],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ])

# Create an Amazon Linux 2 LTS EC2 instance
my_instance = aws.ec2.Instance(f'{instance_name}',
   ami=f"{ami_id}", 
   instance_type=f"{instance_type}",
   vpc_security_group_ids=[secgrp.id], # security group
   user_data="#!/bin/bash\n echo 'Hello world' > /var/www/html/index.html", # Startup script
   tags={
       "Name": f"{instance_name}",
       "Instace_Type": f"{instance_type}"
   })

# Create an EBS volume
ebs_volume = aws.ebs.Volume('ExtraStorage',
    availability_zone=my_instance.availability_zone,
    size=10,  # GiB
    type='gp2',  # General Purpose SSD
)

# Attach the EBS volume to the instance
aws.ec2.VolumeAttachment('ExtraStorageAttachment',
    device_name="/dev/xvdb",
    volume_id=ebs_volume.id,
    instance_id=my_instance.id,
)

# Export the EC2 instance DNS name
pulumi.export("instancePublicDns", my_instance.public_dns)
