FROM continuumio/anaconda3
RUN apt-get update
RUN apt -y install gcc
RUN apt-get -y install libatlas-base-dev
COPY h2som.py .
COPY clustering.py .
COPY /pyclusterbdmseed/ ./pyclusterbdmseed/
COPY environment.yml .
RUN conda env create -f environment.yml
ENV PATH /opt/conda/envs/whide/bin:$PATH
RUN /bin/bash -c "source activate whide"
RUN cd pyclusterbdmseed && python setup.py install
RUN mv /pyclusterbdmseed/build/temp.linux-x86_64-3.8/pyclusterbdmseed/core.o /opt/conda/envs/whide/lib/python3.8/site-packages/pyclusterbdmseed/
RUN mv /pyclusterbdmseed/build/temp.linux-x86_64-3.8/pyclusterbdmseed/c_core.o /opt/conda/envs/whide/lib/python3.8/site-packages/pyclusterbdmseed/
ENV PYTHONPATH "${PYTHONPATH}:/opt/conda/envs/whide/lib/python3.8/site-packages/pyclusterbdmseed/"