# Druid with Kafka

## Kafka producer produce data to topic from TCP PORT

```bash
# install java
sudo yum update
sudo yum install java-1.8.0-openjdk-devel -y
# install kafka
wget https://dlcdn.apache.org/kafka/3.3.1/kafka_2.13-3.3.1.tgz
tar -xzf kafka_2.13-3.3.1.tgz
cd kafka_2.13-3.3.1
# setup zookeeper
tmux new-session -d -s zookeeper "bin/zookeeper-server-start.sh config/zookeeper.properties"
# setup kafka server
tmux new-session -d -s kafka-server "bin/kafka-server-start.sh config/server.properties"
# create topic
bin/kafka-topics.sh --create --topic test --bootstrap-server localhost:9092
# publish realtime data from tcp port to producer 
tmux new-session -d -s $TCP_PORT "nc -l $TCP_PORT | ./bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test"
```