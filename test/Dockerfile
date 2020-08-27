FROM centos:8

RUN yum -y update
#RUN yum update groupinstall -y 'Development Tools'
RUN yum -y --enablerepo=extras install epel-release
RUN yum -y install squashfs-tools libseccomp-devel libuuid-devel openssl-devel
RUN yum -y install python3-pip
RUN yum -y install git wget gcc R-core
#RUN pip install coverage nose nose-watch

RUN export VERSION=1.14.6 OS=linux ARCH=amd64 && \
    wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
    tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
    rm go$VERSION.$OS-$ARCH.tar.gz

ENV GOPATH="${HOME}/go"
ENV PATH="/usr/local/go/bin:${PATH}:${GOPATH}/bin"

#RUN echo 'export GOPATH=${HOME}/go' >> ~/.bashrc && \
#    echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc && \
#    source ~/.bashrc

RUN export VERSION=3.2.0 &&  \
    wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz && \
    tar -xzf singularity-${VERSION}.tar.gz

RUN cd singularity && ./mconfig && \
    make -C ./builddir && \
    make -C ./builddir install


RUN cd / && wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh -b

ENV PATH="/root/miniconda3/bin:${PATH}"

RUN conda create -y --name metag
RUN source activate metag
RUN conda config --add channels bioconda && conda config --add channels r && conda config --add channels conda-forge 
RUN conda install datrie -y
RUN conda install psutil -y
RUN conda install snakemake=5.5.3  -y
RUN conda install -c r r-essentials r-base r-ggplot2 -y

RUN pip install osfclient
RUN git clone https://github.com/signaturescience/metagenomics

RUN cd /metagenomics/workflows && python download_offline_files.py --workflow all

WORKDIR /metagenomics/test
CMD [ "sh", "-c", "source activate metag && export SINGULARITY_BINDPATH="data:/tmp" && python test_all_workflows.py"]
