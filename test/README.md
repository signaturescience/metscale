###Running unit tests
Currently we have individual tests for each rule in a workflow per file.
There is also test_all_workflows that will runs all the files in the workflow.
We can run all these files from the command line:
python test_all_workflows.py

There is also a docker file with a Centos OS to duplicate our clients environment 
docker build -t "centos" .


docker run -t --privileged "centos"
or maybe 
docker run --entrypoint "python" centos test_all_workflow.py
or
sudo docker run -it --privileged "centos" /bin/bash