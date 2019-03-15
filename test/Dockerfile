FROM centos:6.10

RUN yum -y install epel-release libarchive-devel squashfs-tools
RUN yum -y install git python-pip wget gcc R-core
#RUN pip install coverage nose nose-watch
RUN wget https://github.com/singularityware/singularity/releases/download/2.6.1/singularity-2.6.1.tar.gz &&\
		tar xvf singularity-2.6.1.tar.gz &&\
		cd singularity-2.6.1 &&\
		./configure --prefix=/usr/local --sysconfdir=/etc &&\
		make &&\
		make install

RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh 
RUN bash Miniconda3-latest-Linux-x86_64.sh -b

ENV PATH="~/miniconda3/bin:$PATH"
RUN conda create -y --name metag
RUN source activate metag
RUN conda config --add channels bioconda
RUN conda install datrie -y
RUN conda install snakemake -y
RUN conda install -c r r-essentials r-base r-ggplot2 -y

RUN pip install osfclient
RUN git clone https://github.com/signaturescience/metagenomics.git

WORKDIR /metagenomics/test
CMD [ "sh", "-c", "source activate metag && python test_all_workflows.py"]
