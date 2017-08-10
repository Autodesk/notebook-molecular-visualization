FROM continuumio/miniconda3:4.3.14

# Install requirements
RUN conda install -c openbabel openbabel
RUN conda install -c omnia biopython parmed
RUN conda install jupyter
RUN pip install "moldesign==0.8.0b3"

ADD requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# This disables notebook security until we can figure out a way to pass runtime tokens
# The supplied docker-compose files don't expose any public ports anyway
ADD deployment/jupyter_unsecure.json /root/.jupyter/jupyter_notebook_config.json
ADD deployment/run_notebook.sh /opt/run_notebook.sh

# Finally, install the actual package
ADD . /opt/notebook-molecular-visualization
WORKDIR /opt/notebook-molecular-visualization

RUN python setup.py sdist \
 && pip install --no-deps dist/*.tar.gz
RUN jupyter nbextension install --sys-prefix --py widgetsnbextension \
 && jupyter nbextension install --sys-prefix --py nbmolviz \
 && jupyter nbextension enable --sys-prefix --py widgetsnbextension \
 && jupyter nbextension enable --sys-prefix --py nbmolviz

EXPOSE 8888
