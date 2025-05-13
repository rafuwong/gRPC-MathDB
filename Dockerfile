FROM python:3.11
WORKDIR /server_app
COPY server.py mathdb.proto client.py /server_app/
RUN apt-get update && apt-get install -y python3 python3-pip net-tools
RUN python3 -m pip install --upgrade pip && pip3 install grpcio==1.60.1 grpcio-tools==1.60.1 --break-system-packages
RUN python3 -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. mathdb.proto 
EXPOSE 5440
CMD ["python3", "server.py"]
