FROM continuumio/anaconda3
RUN apt-get update
RUN apt -y install gcc
RUN apt-get -y install libatlas-base-dev
COPY h2som.py .
COPY clustering.py .
COPY /pyclusterbdm ./pyclusterbdm
COPY environment.yml .
RUN conda env create -f environment.yml
ENV PATH /opt/conda/envs/whide/bin:$PATH
RUN /bin/bash -c "source activate whide"
RUN cd pyclusterbdm && python setup.py install
RUN mv /pyclusterbdm/build/temp.linux-x86_64-3.8/pyclusterbdm/core.o /opt/conda/lib/python3.7/site-packages/pyclusterbdm
RUN mv /pyclusterbdm/build/temp.linux-x86_64-3.8/pyclusterbdm/c_core.o /opt/conda/lib/python3.7/site-packages/pyclusterbdm
ENV PYTHONPATH "${PYTHONPATH}:/opt/conda/lib/python3.7/site-packages/pyclusterbdm"