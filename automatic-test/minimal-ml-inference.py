import subprocess
import psutil

example_name="minimal-ml-inference"
keyword="Hello World!"

camera_public_ip="172.25.71.119"
repo_name=""
app_name=example_name+"-test"
model_name="acap-dl-models"

archs= ["armv7hf", "aarch64"]
chips=[["cpu","tpu"],["cpu", "artpec8"]]

arch="aarch64"
chip="artpec8"

command="docker run -it --rm --privileged multiarch/qemu-user-static --credential yes --persistent yes"
try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError:
    print("Qemu install failed")
    exit(1)


#Build
command="docker build ./{} -t {}:{} --build-arg ARCH={}".format(repo_name+example_name, app_name, arch, arch)
try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError:
    print("Build App failed")
    exit(1)

command="docker build ./{} -f {}/Dockerfile.model -t {}:{}  --build-arg ARCH={}".format(repo_name+example_name,repo_name+example_name, model_name, arch, arch)
try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError:
    print("Build model failed")
    exit(1)

#Upload
command="docker save {}:{} | docker -H tcp://{}:2375  load".format(app_name, arch, camera_public_ip)
try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError:
    print("upload failed")
    exit(1)

command="docker save {}:{} | docker -H tcp://{}:2375  load".format(model_name, arch, camera_public_ip)
try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError:
    print("upload failed")
    exit(1)

#Run
command="APP_NAME={}:{} MODEL_NAME={}:{} timeout 10 docker-compose -f {}/docker-compose.yml -H tcp://{}:2375 --env-file {}/config/env.{}.{} up".format(app_name, arch, model_name, arch, repo_name+example_name, camera_public_ip, repo_name+example_name ,arch, chip)
try:
    output=subprocess.check_output(command, shell=True)

except subprocess.TimeoutExpired:
    print("Timeout reached")
except subprocess.CalledProcessError:
    print("run failed")
    exit(1)

if not (keyword in str(output)):
    print("Test failed")
    exit(1)

command="APP_NAME={}:{} MODEL_NAME={}:{} docker-compose -f {}/docker-compose.yml -H tcp://{}:2375 --env-file {}/config/env.{}.{} down -v".format(app_name, arch, model_name, arch, repo_name+example_name, camera_public_ip, repo_name+example_name ,arch, chip)

try:
    subprocess.run(command,shell=True)
except subprocess.CalledProcessError:
    print("Cleaning failed")
    exit(1)

print("Test passed")
