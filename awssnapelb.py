import boto3
import botocore
import click
import datetime
ec2 = boto3.resource('ec2')
elbList = boto3.client('elbv2')
costexplorer = boto3.client('ce')
classicelblist = boto3.client('elb')
dbs = boto3.client('rds')
rgapi = boto3.client('resourcegroupstaggingapi')


def filter_dbs(project,env):
    db = []
    if project:
        filter = [{'Key':'Cost Center','Values':[project]},{'Key':'Environment','Values':[env]}]
        dbinstance = rgapi.get_resources(TagFilters=filter,ResourceTypeFilters=['rds:db'])
    else:
        dbinstance = dbs.describe_db_instances()
    return dbinstance


def sh_cost(project,day,dimension):
    ct = []
    now = datetime.datetime.utcnow()
    start = (now - datetime.timedelta(days=int(day))).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')
    costs = costexplorer.get_cost_and_usage(TimePeriod={'Start':start,'End':end},Granularity='DAILY',Filter={"And":[{"Dimensions":{'Key':'USAGE_TYPE_GROUP','Values':[dimension]}},{"Tags":{'Key':'Cost Center','Values':[project]}}]},Metrics=['UnblendedCost'])
    for cost in costs['ResultsByTime']:
        print(cost)
    return ct



def total_cost(project,day):
    ct = []
    now = datetime.datetime.utcnow()
    start = (now - datetime.timedelta(days=int(day))).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')
    costs = costexplorer.get_cost_and_usage(TimePeriod={'Start':start,'End':end},Granularity='MONTHLY',Filter={'Tags':{'Key':'Cost Center','Values':[project]}},Metrics=['UnblendedCost'])
    for cost in costs['ResultsByTime']:
        print(cost)
    return ct


def filter_instances(project,env):
    instances = []

    if project:
        filters = [{'Name':'tag:Cost Center', 'Values':[project]},{'Name':'tag:Environment', 'Values':[env]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def list_tg(lb):
    tgt  = []
    loadbalancers = elbList.describe_load_balancers(Names=[lb])
    for lb in loadbalancers['LoadBalancers']:
        lbalancer = lb['LoadBalancerName']
        lbalancerarn = lb['LoadBalancerArn']
        tgs = elbList.describe_target_groups(LoadBalancerArn=lbalancerarn)
        for tg in tgs['TargetGroups']:
            targetgps = tg['TargetGroupArn']
            print(targetgps)                
    return tgt

def rmv_tg(lb):
    tgt  = []
    loadbalancers = elbList.describe_load_balancers(Names=[lb])
    for lb in loadbalancers['LoadBalancers']:
        lbalancer = lb['LoadBalancerName']
        lbalancerarn = lb['LoadBalancerArn']
        tgs = elbList.describe_target_groups(LoadBalancerArn=lbalancerarn)
        for tg in tgs['TargetGroups']:
            targetgps = tg['TargetGroupArn']
            print(targetgps)
    return targetgps

def rmv_tgts(lb):
    test = []
    loadbalancers = elbList.describe_load_balancers(Names=[lb])
    for lb in loadbalancers['LoadBalancers']:
        lbalancer = lb['LoadBalancerName']
        lbalancerarn = lb['LoadBalancerArn']
        tgs = elbList.describe_target_groups(LoadBalancerArn=lbalancerarn)
        for tg in tgs['TargetGroups']:
            targetgps = tg['TargetGroupArn']
            tgts = elbList.describe_target_health(TargetGroupArn=targetgps)
            for tgt in tgts['TargetHealthDescriptions']:
                target_id = tgt['Target']['Id']
                print(target_id)
        return target_id



def list_targets(lb):
    test = []
    loadbalancers = elbList.describe_load_balancers(Names=[lb])
    for lb in loadbalancers['LoadBalancers']:
        lbalancer = lb['LoadBalancerName']
        lbalancerarn = lb['LoadBalancerArn']
        tgs = elbList.describe_target_groups(LoadBalancerArn=lbalancerarn)
        for tg in tgs['TargetGroups']:
            targetgps = tg['TargetGroupArn']
            print(targetgps)
            tgts = elbList.describe_target_health(TargetGroupArn=targetgps)
            for tgt in tgts['TargetHealthDescriptions']:
                target_id = tgt['Target']['Id']
                print(target_id)
    return test
    


def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'


def tar_instances(project):
    instances = []
    if project:
        filters = [{'Name':'tag:Cost Center', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

"""
def lst_targets(project):
     loadbalancers = elbList.describe_target_health(TargetGroupArn='arn:aws:elasticloadbalancing:eu-west-1:672985825598:targetgroup/test/4ae1eee6118aae2e')
     "list the targets"
     for target in loadbalancers['TargetHealthDescriptions']:
         target_id = target['Target']['Id']

     return target_id

"""

@click.group()
def cli():
    """botocli manages services in aws"""

@cli.group('rdb')
def rdb():
    """ Commands for db's"""

@rdb.command('listall')
@click.option('--project', default=None,help="only the db's for the project (tag Project:<name>)")

def list_allrdsinstances(project):
    """ commands to list rds instances """
    db_list = dbs.describe_db_instances()
    for db in db_list['DBInstances']:
        print("RDS Instance {0} belongs to {1} engine and is {2}".format(db['DBInstanceIdentifier'],db['Engine'],db['DBInstanceStatus']))


@rdb.command('listdbs')
@click.option('--project', default=None,help="only the db's for the project (tag Project:<name>)")
@click.option('--env', prompt='Environment Name',
              help="Only dbinstances for environment (tag Environment:<name>)")

def list_rdsinstances(project,env):
    """ commands to list project rds instances """
    db_instances = filter_dbs(project,env)
    for db in db_instances['ResourceTagMappingList']:
        db = str(db['ResourceARN'])
        dbsmod = db[38:]
        db_list = dbs.describe_db_instances(DBInstanceIdentifier=dbsmod)
        for db in db_list['DBInstances']:
            print("RDS Instance {0} belongs to {1} engine and is {2}".format(db['DBInstanceIdentifier'],db['Engine'],db['DBInstanceStatus']))	


@rdb.command('start')
@click.option('--project', default=None,help="only the db's for the project (tag Project:<name>)")
@click.option('--env', prompt='Environment Name',
              help="Only dbinstances for environment (tag Environment:<name>)")

def start_rdsinstances(project,env):
    """ Command to start rds instances """
    db_instances = filter_dbs(project,env)
    for db in db_instances['ResourceTagMappingList']:
        try:
            db = str(db['ResourceARN'])
            dbsmod = db[38:]
            db_list = dbs.start_db_instance(DBInstanceIdentifier=dbsmod)
            print("starting the instance {0}".format(db_list['DBInstance']['DBInstanceIdentifier']))

        except dbs.exceptions.InvalidDBInstanceStateFault:
            pass
            print("{0} Instance is already started".format(dbsmod))


@rdb.command('stop')
@click.option('--project', default=None,help="only the db's for the project (tag Project:<name>)")
@click.option('--env', prompt='Environment Name',
              help="Only dbinstances for environment (tag Environment:<name>)")
def stop_rdsinstances(project,env):
    """ Command for stopping rds instances """
    db_instances = filter_dbs(project,env)
    for db in db_instances['ResourceTagMappingList']:
        try:
            db = str(db['ResourceARN'])
            dbsmod = db[38:]
            db_list = dbs.stop_db_instance(DBInstanceIdentifier=dbsmod)
            print("stopping the instance {0}".format(db_list['DBInstance']['DBInstanceIdentifier']))

        except dbs.exceptions.InvalidDBInstanceStateFault:
            pass
            print("{0} Instance has already stopped or it is stopping".format(dbsmod))


@cli.group('lb')
def lb():
    """Commands for load balancers"""
@lb.command('listalbs')
@click.option('--project', default=None,help="only the elb's for the project (tag Project:<name>)")
def list_loadbalancers(project):
    "Lists the ELBv2's"
    loadbalancers = elbList.describe_load_balancers()
    "List the lb's"
    for elb in loadbalancers['LoadBalancers']:
        print('ELBv2 Name : ' + elb['LoadBalancerName'])
    
"""
@lb.command('listtargetgroups')
@click.option('--project', default=None,help="only the targets for the project (tag Project:<name>)")
def list_targetgroups(project):
    loadbalancers = elbList.describe_target_groups()
    "List Targetgroups in the ELB"
    for elb in loadbalancers['TargetGroups']:
        print('ELB Target group Name : ' + elb['TargetGroupName'])
    return
"""
@lb.command('listtargetgroups')
@click.option('--lb', default=None,help="only the elb's for the project (tag Project:<name>)")

def lst_tg(lb):
    "List Targetgroups in the ELB"
    target_groups = list_tg(lb)
    for tg in target_groups:
        print(tg)

@lb.command('listtargets')
@click.option('--lb', default=None,help="only the elb's for the project (tag Project:<name>)")

def lst_tg(lb):
    "List Targets in the ELB"
    targets = list_targets(lb)
    for tg in targets:
	print(tg)


@lb.command('removetargets')
@click.option('--lb', default=None,help="only the targets for the project (tag Project:<name>)")

def rm_targets(lb):
     "removes the targets from a targetgroup"
     target_id = rmv_tgts(lb)
     Targets = []
     Target = {}
     Target['Id'] = target_id
     Targets.append(Target)
     Tgroup =  rmv_tg(lb)
     lbs = elbList.deregister_targets(TargetGroupArn=Tgroup,Targets=Targets)
     print(lbs)


@lb.command('addtargets')
@click.option('--project', default=None,help="only the targets for the project (tag Project:<name>)")
@click.option('--lb', prompt='Loadbalancer Name',
              help="Only instances for environment (tag Environment:<name>)")
def add_targets(project,lb):
     "adds the targets to the targetgroup"
     target_id = tar_instances(project)
     for i in target_id:
        Targets = []
        Target = {}
        Target['Id'] = i.id
        Target['Port'] = 80
        Targets.append(Target)
     print(Targets)
     Tgroup =  rmv_tg(lb)
     lbs = elbList.register_targets(TargetGroupArn=Tgroup,Targets=Targets)
     print(lbs)



@cli.group('costs')
def costs():
    """Commands for showing costs"""

@costs.command('show')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--day', prompt='Enter the days',
              help="Only instances for environment (tag Environment:<name>)")
@click.option('--dimension', prompt='Enter the dimension',
              help="Only instances for environment (tag Environment:<name>)")
def list_costs(project,day,dimension):
     cost_explorer = sh_cost(project,day,dimension)
     for cost in cost_explorer:
         print(cost)

@costs.command('showtotal')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--day', prompt='Enter the days',
              help="Number of days for which cost is calculated")
def list_totalcosts(project,day):
     cost_explorer = total_cost(project,day)
     for cost in cost_explorer:
         print(cost)


@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--env', prompt='Environment Name',
              help="Only instances for environment (tag Environment:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project, list_all,env):
    "List EC2 snapshots"

    instances = filter_instances(project,env)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
@click.option('--env', prompt='Environment Name',
              help="Only instances for environment (tag Environment:<name>)")
def list_volumes(project,env):
    "List EC2 volumes"

    instances = filter_instances(project,env)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--env', prompt='Environment Name',
              help="Only instances for environment (tag Environment:<name>)")
def create_snapshots(project,env):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project,env)

    for i in instances:
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("  Skipping {0}, snapshot already in progress".format(v.id))
                continue

            print("  Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by SnapshotAlyzer 30000")

        print("Starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job's done!")

    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--env', prompt='Environment Name',
              help="Only instances for environment (tag Environment:<name>)")
def list_instances(project,env):
    "List EC2 instances"
    instances = filter_instances(project,env)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Environment', '<no environment>'),
	    tags.get("Cost Center", '<no project>')
            )))

    return


@instances.command('stop')
@click.option('--project', default=None,
  help='Only instances for project')
@click.option('--env', prompt='Environment Name',
              help="Only instances for environment (tag Environment:<name>)")
def stop_instances(project,env):
    "Stop EC2 instances"

    instances = filter_instances(project,env)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None,
  help='Only instances for project')
@click.option('--env', prompt='Environment Name',
              help="Only instances for environment (tag Environment:<name>)")
def start_instances(project,env):
    "Start EC2 instances"

    instances = filter_instances(project,env)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start {0}. ".format(i.id) + str(e))
            continue

    return

if __name__ == '__main__':
    cli()

