#!/bin/bash

# Check if at least 3 arguments are provided
if [ $# -lt 3 ]; then
    echo -e "\nUsage: $0 [division|decrement|parallel] num_ue delay interval divdec repetitions\n"
    exit 0
fi

# Check if the first argument is "division", "decrement" or "parallel"
if [[ "$1" != "division" && "$1" != "decrement" && "$1" != "parallel" ]]; then
    echo -e "\nError: The first argument must be 'division', 'decrement', or 'parallel'\n"
    exit 1
fi

# Assign the first argument to the test variable
test=$1
namespace=free5gc
replicas=50
sleep_time=1600
components=("amf" "ausf" "nrf" "nssf" "pcf" "smf" "udm" "udr" "upf")

# Check the number of arguments based on the test
if [[ "$test" == "parallel" ]]; then
    if [ $# -ne 4 ]; then
        echo -e "\nUsage for 'parallel': $0 parallel num_ue delay repetitions\n"
        exit 1
    fi
    num_ue=$2
    delay=$3
    repetitions=$4
    dir_name=Parallel_${delay}
else
    if [ $# -ne 6 ]; then
        echo -e "\nUsage for 'division' or 'decrement': $0 [division|decrement] num_ue delay interval factor repetitions\n"
        exit 1
    fi
    num_ue=$2
    delay=$3
    interval=$4
    divdec=$5
    repetitions=$6
    if [[ "$test" == "division" ]]; then
        dir_name=Division_${delay}
    else
        dir_name=Decrement_${delay}
    fi
fi

mkdir $dir_name

# Loop through the number of repetitions
for i in $(seq 1 $repetitions); do
    
    cd $dir_name
    mkdir test_${i}
    cd ..

    start_time=$(date +%s)
    if [[ "$test" == "parallel" ]]; then
        test_name=my5grantester_free5gc_${test}_${num_ue}_0_${i}.csv
    else
        test_name=my5grantester_free5gc_${test}_${num_ue}_${delay}_${divdec}_${interval}_0_${i}.csv
    fi
    # Path to the YAML file
    yaml_file="../Deployment/tester/my5grantester.yaml"
    copy_file="../Deployment/tester/my5grantester2.yaml" 

    cp $yaml_file $copy_file

    # Update the YAML file with the provided values
    sed -i 's/\$TEST\b/'"$test"'/g' $copy_file
    sed -i 's/\$NUM_UE\b/'"$num_ue"'/g' $copy_file
    sed -i 's/\$DELAY\b/'"$delay"'/g' $copy_file

    # Only update INTERVAL and FACTOR if operation is not parallel
    if [[ "$test" != "parallel" ]]; then
        sed -i 's/\$INTERVAL\b/'"$divdec"'/g' $copy_file
        sed -i 's/\$CONSTANT\b/'"$interval"'/g' $copy_file
    fi

    kubectl apply -f $copy_file

    rm $copy_file

    cd ..
    python3 Deployment/start.py

    kubectl port-forward deployment/free5gc-mongodb 63145:27017 --namespace $namespace &
    PORT_FORWARD_PID=$!

    python3 Deployment/Database/policyData.ues.amData.py
    python3 Deployment/Database/policyData.ues.qosFlow.py
    python3 Deployment/Database/policyData.ues.smData.py
    python3 Deployment/Database/subscriptionData.authenticationData.authenticationSubscription.py
    python3 Deployment/Database/subscriptionData.provisionedData.amData.py
    python3 Deployment/Database/subscriptionData.provisionedData.smData.py
    python3 Deployment/Database/subscriptionData.provisionedData.smfSelectionSubscriptionData.py
    kill $PORT_FORWARD_PID

    echo "Running experiment $i"

    # Number of UEs and gnBs
    kubectl scale --replicas=$replicas statefulsets free5gc-my5grantester --namespace $namespace

    cd Data

    steps=30
    increment=$((sleep_time / steps))

    for c in $(seq 0 $increment $sleep_time); do
	    
    	int_time=$(date +%s)
    	if [ "$c" -eq 0 ]; then
		int_time=$start_time
    	fi

    	echo "Waiting for experiment to finish"
    	sleep "$increment"
	    
    	start_iso=$(date -u -d "@$int_time" +"%Y-%m-%dT%H:%M:%SZ")

    	for component in "${components[@]}"; do
		componente=$(kubectl get pods -n free5gc | grep ^free5gc-${component} | awk '{print $1}')
   		kubectl logs -n free5gc -c "$component" "$componente" --since-time="$start_iso" >> "${dir_name}/test_${i}/free5gc-${component}-${i}.log"
    	done
    done


    TESTERS=$(kubectl get pods -n free5gc | grep ^free5gc-my5grantester | awk '{print $1}')
    for tester in $TESTERS; do
        kubectl logs -n free5gc $tester --tail=-1 >> "${dir_name}/test_${i}/${test_name}"
    done


    echo "Clear experiment environment"
    kubectl scale --replicas=0 statefulsets free5gc-my5grantester --namespace $namespace

    # Delete tester pods
    for j in $(seq 0 $(($replicas))); do
        kubectl delete pod free5gc-my5grantester-$j --namespace $namespace &
    done
    
    cd ..
    python3 Deployment/remove.py
    sleep 10
    end_time=$(date +%s)
    
    cd Data
    
    echo $start_time-$end_time >> ${dir_name}/timestamp.txt

done

