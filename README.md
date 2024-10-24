# Deployments, Tests, and Datasets of Free5GC and Open5GS

## 1. Using the Datasets from Our Experiments:

### 1. Choose the core network you would like to use the datasets with:
- **For Free5GC**:
```bash
cd Free5GC
```
- **For Open5GS**:
```bash
cd Open5GS
```

### 2. Select the experiment you would like to explore:

- **For Decrement_Test:**
- 10 rounds of a test with an initial time interval of 4600ms, where the time is decremented by 500ms between 10 connection tests for 100 UEs:
```bash
cd Decrement_Test
```
- **For Division_Test:**
- 10 rounds of a test with an initial time interval of 51200ms, where the time is divided by a factor of 2 between 20 connection tests for 100 UEs:
```bash
cd Division_Test
```
- **For Parallel_Test_100:**
- 10 rounds with a constant time interval of 100ms between connection tests for 100 UEs:
```bash
cd Parallel_Test_100
```
- **For Parallel_Test_10000:**
- 10 rounds with a constant time interval of 10000ms between connection tests for 100 UEs:
```bash
cd Parallel_Test_10000
```

### 3. Select the type of data for analysis:

- **For Tester:**
  - 10 CSV files containing tester logs from our experiments.

- **For timestamps.txt:**
  - 10 timestamps collected from our experiments to be used for metric collection.


## 2. Running the scripts for new tests
### 1. Choose the core network you would like to test:
- For Free5GC:
```bash
cd Free5GC
```
- For Open5GS
```bash
cd Open5GS
```

### 2. Update the namespace in the YAML deployment files to match your configuration:
#### 1. Go to Deployment directory
```bash
cd Deployment
```
#### 2. Update this field in all YAML files:
```YAML
namespace: your_namespace
```

### 3. Make the scripts executable using the ```chmod``` command:

```bash
cd ../Data/
chmod +x connection_test.sh
chmod +x capture_and_parse_logs.sh
```

### 4. Ensure that you have ```kubectl``` installed and are running in root mode:
```bash
sudo su
kubectl --version
```

### 5. Modify the initial variables in `connection_test.sh` to suit your requirements:

- `replicas`: Specifies the number of testers.
- `namespace`: Indicates where the pod commands will be executed.
- `sleep_time`: Defines the duration required to execute one round of the experiment.

### 6. Choose the workload test you would like to perform:

#### 1. For 10 rounds with a constant time interval of 1000ms between connection tests for 100 UEs:
```bash
./connection_test.sh parallel 100 1000 10
```
#### 2. For 10 rounds of a test with an initial time interval of 51200ms, where the time is divided by a factor of 2 between 20 connection tests for 100 UEs:
```bash
./connection_test.sh division 100 51200 20 2 10
```
#### 3. For 10 rounds of a test with an initial time interval of 4600ms, where the time is decremented by 500ms between 10 connection tests for 100 UEs:
```bash
./connection_test.sh decrement 100 4600 10 500 10
```