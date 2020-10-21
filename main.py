import subprocess
import argparse
import requests

from time import sleep

def send(url, data):
    # wrap neatly in json
    json_payload ="{ \"text\": \"" + data + "\" }"

    # send to mattermost
    response = requests.post(url, json_payload)
    
    if not response.status_code == 200:
        print("could not post to", url)
        print("Error code", response.status_code)
    else:
        print("Successfully posted to ", url, response.status_code)

def get_docker_report(desired_containers):
    result = subprocess.run(['docker', 'ps', '-a','--format', '{{.Image}},{{.ID}},{{.Status}},{{.Names}}'], stdout=subprocess.PIPE)
    output = result.stdout.split(b"\n")

    containers = [ line.decode("utf-8").split(",") for line in output if len(line) > 0]
    msg = ""

    for container in containers:
        # print("image:",container[0])
        # print("id:",container[1])
        # print("name:",container[3])
        # print("status:",container[2])

        if container[3] in desired_containers and "Exited" in container[2]:
            msg += "Watchdog: Container %s (image: %s) has exited %s" % ( container[3], container[0], container[2].split(") ")[-1])

    return msg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send docker reports to given webhook (e.g. mattermost)')
    parser.add_argument('webhook', type=str, help="webhook url to send a perlisism to")
    parser.add_argument('-c','--containers', nargs='+', help='<Required> Set containers to be watched.', required=True)
    args = parser.parse_args()

    msg = get_docker_report(args.containers)
    print(msg)

    send(args.webhook, msg)
    # while(True):
    #     try:
    #         send(args.webhook, msg)
    #     except Exception as e:
    #         if type(e) == KeyboardInterrupt:
    #             raise e
    #         print(e)
    #         sleep(30)