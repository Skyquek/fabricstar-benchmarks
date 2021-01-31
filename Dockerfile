FROM hyperledger/caliper:0.4.0

RUN npm install -g fs-extra
RUN npm install -g --only=prod @hyperledger/caliper-cli@0.4.0
RUN npx caliper bind --caliper-bind-sut fabric:1.4 --caliper-bind-args=-g