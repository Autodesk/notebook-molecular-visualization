FROM node:boron

# Test runner image for nbmolviz - doesn't include nbmolviz itself
# Includes galileo + the test notebooks
# Needs to connect to a Jupyter server with nbmolviz and MDT installed. 

# install java for selenium
RUN apt-get update \
 && apt-get install -y default-jre \
                       software-properties-common \
                       curl git build-essential wget \
                       libgconf-2-4 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD galileo/package.json /opt/galileo/package.json
WORKDIR /opt/galileo
RUN npm install && npm run selenium
ADD galileo /opt/galileo

ADD nb /opt/test_notebooks
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh
