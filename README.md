# Bot info:
## Telegram bot for checking lighting by ip check.
- Bot code deployed and running in [AWS EC2](https://console.aws.amazon.com/ec2/v2/home);
- Bot database running on MySql and deployed in [Planetscale](https://app.planetscale.com/);
### Functionality:
- Can make one-time check ip;
- Can add as many as you want ip addresses in ip list;
- Can watch and delete all ips which was added to ip list;
- Can make one-time ip check which was added to ip list;
- All ips which are in ip list checking every 5 minutes, and if some ip status changed, print message to ip owner about new status and time difference between old status.

#### Bot functional can try in telegram: [Lighting bot](https://t.me/check_lightning_bot)
### Bot settings:
In main.py you need to put your bot token, so open .env file and put there your token.
```sh
TOKEN='HERE_PUT_YOUR_TOKEN'
```
Same need to do for periodic_check.py, if already done it, skip it.
```sh
TOKEN='HERE_PUT_YOUR_TOKEN'
```
The last what need to do, make settings for MySql db in .env file:
```sh
HOST='WRITE_YOUR_HOST_SERVER'
USERNAME='WRITE_YOUR_CLOUD_DB_USERNAME'
PASSWORD='WRITE_YOUR_CLOUD_DB_PASSWORD'
BOT_DB='WRITE_YOUR_CLOUD_DB_NAME'
```