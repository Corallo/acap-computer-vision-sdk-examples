import subprocess

example_name="hello-world"
keyword="Hello World!"

camera_public_ip="172.25.71.119"
repo_name=""
app_name=example_name+"-test"
archs= ["armv7hf", "aarch64"]

arch="aarch64"


command="docker build ./{} -t {}:{} --build-arg ARCH={}".format(repo_name+example_name, app_name, arch, arch)
try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError:
    print("Build failed")
    exit(1)

command="docker save {}:{} | docker -H tcp://{}:2375  load".format(app_name, arch, camera_public_ip)
try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError:
    print("upload failed")
    exit(1)


command="APP_NAME={}:{} docker-compose -f {}/docker-compose.yml -H tcp://{}:2375 up".format( app_name, arch,repo_name+example_name, camera_public_ip)
try:
    output=subprocess.check_output(command,shell=True)
except subprocess.CalledProcessError:
    print("run failed")
    exit(1)

if not (keyword in str(output)):
    print("Test failed")
    exit(1)

command="APP_NAME={}:{} docker-compose -f {}/docker-compose.yml -H tcp://{}:2375 down".format( app_name, arch,repo_name+example_name, camera_public_ip)
try:
    subprocess.run(command,shell=True)
except subprocess.CalledProcessError:
    print("Cleaning failed")
    exit(1)

print("Test passed")
