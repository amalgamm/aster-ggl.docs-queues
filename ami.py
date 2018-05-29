from asterisk.ami import AMIClient
from asterisk.ami import SimpleAction
from config import ami_ip, ami_port, ami_secret, ami_user
import sys, json



def reload_queues():
    try:
        client = AMIClient(address=ami_ip, port=ami_port)
        client.login(username=ami_user, secret=ami_secret)
        command = SimpleAction(
            'QueueReload',
            Members='yes',
            Rules='no',
            Parametes='yes'
        )
        result = str(client.send_action(command).response).replace("\r", "").split("\n")
        if isinstance(result,list):
            if 'Response: Success' in result:
                return True
            else:
                return False

    except Exception as e:
        return str(e)
