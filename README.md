# Deployments, Tests and DataSets of Free5GC and Open5GS

## 1. Running the scripts for new tests
### 1. Choose the core network you would like to test:
- For Free5GC:
```bash
cd Free5GC/Data
```
- For Open5GS
```bash
cd Open5GS/Data
```
### 2. Make the scripts executable using the ```chmod``` command:

  ```bash
  chmod +x connection_test.sh
  chmod +x capture_and_parse_logs.sh
  ```

### 3. Ensure that you have ```kubectl``` installed and are running in root mode:
```bash
    sudo su
    kubectl --version
```

### 4. Choose the workload test you would like to perform:

#### 1. For 10 rounds with a constant time interval of 1000ms between connection tests for 100 UEs:
```bash
    ./connection_test.sh parallel 100 1000 10
```
#### 2. For 10 rounds of a test with an initial time interval of 51200ms, where the time is divided/decremented by a factor of 2 between 20 connection tests for 100 UEs:
```bash
    ./connection_test.sh [division|decrement] 100 51200 20 2 10
```