FROM ubuntu:latest
LABEL authors="greg"
COPY install-miniconda.sh main.py requirements.txt /root/
# change the shell to bash instead of /bin/sh in order to have access to the source command
SHELL ["/bin/bash", "-c"]
# add timezone info to container so we dont get prompted for geographical info when installing python3
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
RUN chmod +x /root/install-miniconda.sh && chmod +x /root/main.py && \
    apt-get update -y &&  \
    apt-get install wget git -y && \
    apt-get install python3 python3-pip -y && \
    apt-get install build-essential libpoppler-cpp-dev pkg-config poppler-utils -y && \
    /root/install-miniconda.sh
RUN source /root/miniconda3/bin/activate && \
    conda create -n test python=3.9 && \
    conda activate test && \
    python -m pip install -r /root/requirements.txt
ENTRYPOINT ["/root/miniconda3/bin/conda","run", "-n", "test", "python" , "/root/main.py"]