import boto3
import datetime
import time

today = datetime.date.today()
today_string = today.strftime('%Y/%m/%d')

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Get list of regions
    regions = ec2.describe_regions().get('Regions',[] )

    # Iterate over regions
    for region in regions:
        print ("Checking region %s " % region['RegionName'])
        reg=region['RegionName']

        # Connect to region
        ec2 = boto3.client('ec2', region_name=reg)
    
        # Get all in-use volumes in all regions  
        result = ec2.describe_volumes(Filters=[{'Name': 'tag:ebs_snapshot_auto', 'Values': ['true']}])
        
        for volume in result['Volumes']:
            print ("Backing up %s in %s" % (volume['VolumeId'], volume['AvailabilityZone']))
            
            for d in volume['Attachments']:
                device=d['Device']
                      
            if 'Tags' in volume:
              for tags in volume['Tags']:
                  if tags["Key"] == 'Name':
                      volumename = tags["Value"]
            
            # Create snapshot
            result = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description='Lambda_AutoSnapshot on {0} of volume {1} - Created {2}'.format(volumename, volume['VolumeId'], today_string),)
         
            # Get snapshot resource 
            ec2resource = boto3.resource('ec2', region_name=reg)
            snapshot = ec2resource.Snapshot(result['SnapshotId'])
        
            volumename = 'N/A'
        
            # Find name tag for volume if it exists
            if 'Tags' in volume:
                for tags in volume['Tags']:
                    if tags["Key"] == 'Name':
                        volumename = tags["Value"]
        
            # Add volume name to snapshot for easier identification            
            snapshot.create_tags(
             Tags = [
                      {
                          'Key': 'ebs_auto_snapshot',
                          'Value': 'true'
                      },
                      {
                          'Key': 'volume',
                          'Value': volume['VolumeId']
                      },
                      {
                          'Key': 'CreatedOn',
                          'Value': today_string
                      },
                      {
                          'Key': 'Name',
                          'Value': (volumename)
                      },
                      {
                          'Key': 'Device',
                          'Value': (device)
                      }
                  ]
              )          
    
            print('Snapshot completed')
