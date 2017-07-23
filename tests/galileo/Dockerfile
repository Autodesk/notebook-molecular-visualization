FROM node:boron

# Test runner image for nbmolviz - doesn't include nbmolviz itself
# Needs to connect to a Jupyter server with nbmolviz and MDT installed. 

ADD package.json /opt/tests/package.json
WORKDIR /opt/tests
RUN npm install && npm run selenium
ADD . /opt/tests/
