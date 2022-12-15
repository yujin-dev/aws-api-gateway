**Lets take a look at Kafka logs**

```console
.
├── __consumer_offsets-0
│   ├── 00000000000000000000.index
│   ├── 00000000000000000000.log
│   ├── 00000000000000000000.timeindex
│   ├── leader-epoch-checkpoint
│   └── partition.metadata
├── __consumer_offsets-1
│   ├── 00000000000000000000.index
│   ├── 00000000000000000000.log
│   ├── 00000000000000000000.timeindex
│   ├── leader-epoch-checkpoint
│   └── partition.metadata
...

├── quickstart-events-49
│   ├── 00000000000000000000.index
│   ├── 00000000000000000000.log
│   ├── 00000000000000000000.timeindex
│   ├── 00000000000000000014.snapshot
│   ├── leader-epoch-checkpoint
│   └── partition.metadata
├── cleaner-offset-checkpoint
├── log-start-offset-checkpoint
├── meta.properties
├── recovery-point-offset-checkpoint
└── replication-offset-checkpoint
```

consumer에서 각 offset마다 데이터가 저장되어 있고, 스트리밍된 데이터는 토픽 로그에 그대로 기록되어 있다.
```bash
hello
world
...
```
