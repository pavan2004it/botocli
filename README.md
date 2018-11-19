# botocli

This is a command line utility to manage aws resources it has been designed by using the boto3 sdk and click.

To use the utility configure the awscli with your credentials.

For details as to how to configure awscli please refer to the below amazon documentation.

https://docs.aws.amazon.com/cli/latest/userguide/installing.html

Once you have configured that you need to install Python and pip



Post that install the package by issuing the command pip install directory of the package/*.whl



Once the package is installed then you can start using the application.




Issue the command botocli --help you will see the below response.




Usage: botocli [OPTIONS] COMMAND [ARGS]...

  botocli manages services in aws



Options:
  --help  Show this message and exit.



Commands:
  costs      Commands for showing costs
  instances  Commands for instances
  lb         Commands for load balancers
  rdb        Commands for db's
  snapshots  Commands for snapshots
  volumes    Commands for volumes



From here you can select any of the subcommands with help option and you will get the complete command .



botocli costs --help

Usage: botocli costs [OPTIONS] COMMAND [ARGS]...

  Commands for showing costs

Options:
  --help  Show this message and exit.

Commands:
  show
  showtotal



botocli costs showtotal --help



Usage: botocli costs showtotal [OPTIONS]

Options:
  --project TEXT  Only snapshots for project (tag Project:<name>)
  --day TEXT      Number of days for which cost is calculated
  --help          Show this message and exit.




Finally the complete command looks like botocli costs showtotal --project Devops



botocli costs showtotal --project Devops



Enter the days: 30

{'TimePeriod': {'Start': '2018-10-14', 'End': '2018-11-01'}, 'Total': {'UnblendedCost': {'Amount': '8.7531046793', 'Unit
': 'USD'}}, 'Groups': [], 'Estimated': False}
{'TimePeriod': {'Start': '2018-11-01', 'End': '2018-11-13'}, 'Total': {'UnblendedCost': {'Amount': '10.7107138938', 'Uni
t': 'USD'}}, 'Groups': [], 'Estimated': True}  

In this example we are shown the costs for the project Devops for a duration of 30 days.


Similarly you can explore other commands.



Note: I have tagged my resources in AWS by project, you may want to do the same.
