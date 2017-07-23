FROM continuumio/miniconda3:4.3.14


# Install node/npm
RUN conda install -c conda-forge nodejs
RUN conda install -c vdbwrair imagemagick

# Install requirements
RUN conda install -c openbabel openbabel
RUN conda install -c omnia biopython parmed
RUN conda install jupyter
RUN pip install "moldesign==0.8.0b3"

# install prerequisites now to cache them
ADD ./tests/package.json /opt/tests/package.json
RUN cd /opt/tests && npm install && npm run selenium

ADD requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# Finally, install the actual package
ADD . /opt/notebook-molecular-visualization
WORKDIR /opt/notebook-molecular-visualization
RUN mv /opt/tests/node_modules tests/node_modules

RUN python setup.py sdist \
 && pip install --no-deps dist/*.tar.gz
RUN jupyter nbextension install --sys-prefix --py widgetsnbextension \
 && jupyter nbextension install --sys-prefix --py nbmolviz \
 && jupyter nbextension enable --sys-prefix --py widgetsnbextension \
 && jupyter nbextension enable --sys-prefix --py nbmolviz

