import boto3
import click
rgapi = boto3.client('resourcegroupstaggingapi')
dbs = boto3.client('rds')


def mod_pg(gname,pname,pvalue,am):
    pg = []
    if gname:
        pgroups = dbs.modify_db_parameter_group(DBParameterGroupName=gname,Parameters=[{
            'ApplyMethod': am,
            'ParameterName':pname,
            'ParameterValue':pvalue,
        }])
    else:
        print("Enter the parameter group name")
    
    return pgroups




@click.group()
def cli():
    """botocli manages services in aws"""

@cli.group('rdb')
def rdb():
    """ Commands for db's"""

@rdb.command('modpg')
@click.option('--gname',default=None, help="only the db's for the project (tag Project:<name>)")
@click.option('--pname',default=None,
              help="Only dbinstances for environment (tag Environment:<name>)")
@click.option('--pvalue',default=None,
              help="Only dbinstances for environment (tag Environment:<name>)")
@click.option('--am',default=None,
              help="Only dbinstances for environment (tag Environment:<name>)")

def modify_pgs(gname,pname,pvalue,am):
    pg = mod_pg(gname,pname,pvalue,am)
    print(pg)
    mod_pg(gname,pname,pvalue,am)

if __name__ == '__main__':
    cli()
