#!/bin/bash

# ========== CONFIGURATION ==========
NAMESPACE="oai"
IPERF3_SERVER_IP=$(kubectl get pod iperf3 -o jsonpath='{.status.podIP}')
START_PORT=5210           # port de départ pour iperf3
DURATION=${1:-60}       # Default duration = 60s if not given
UE_POD=$(kubectl get pods -n oai --no-headers | grep ueransim-gnb-ues | awk '{print $1}')
NUM_UES=$(( $(kubectl exec -n $NAMESPACE $UE_POD -- ip a | grep -c uesimtun) / 2 ))
if [ "$NUM_UES" -gt 100 ]; then
  echo "Limiting to 100 UEs max."
  NUM_UES=100
fi
RETRIES=3                 # nombre de tentatives max si échec

echo "UEs Pod: $UE_POD"
echo "iPerf3 Server IP: $IPERF3_SERVER_IP"
echo "Launching $NUM_UES iPerf3 clients from interfaces uesimtun0 to uesimtun$((NUM_UES - 1))..."

# ========== MAIN LOOP ==========
for i in $(seq 0 $((NUM_UES - 1))); do
  INTERFACE="uesimtun$i"
  ueIP=$(kubectl exec -n oai $UE_POD -- ip -o -4 addr show $INTERFACE | awk '{print $4}' | cut -d/ -f1)
  PORT=$((START_PORT + i))
  ATTEMPT=1
  echo "****************************************************"
  echo "Running iperf3 test on $INTERFACE (port $PORT)..."

  while [ $ATTEMPT -le $RETRIES ]; do
    echo "Attempt $ATTEMPT for interface $INTERFACE"
    kubectl exec -n $NAMESPACE $UE_POD -- iperf3 -c $IPERF3_SERVER_IP -B $ueIP -p $PORT -t $DURATION >> "text_files/iperf3_results.txt" 2>&1 &
    sleep 1
    PID=$!
    wait $PID
    RESULT=$(tail -n 1 "text_files/iperf3_results.txt")

    if [[ "$RESULT" == *"refused"* || "$RESULT" == *"unable"* || "$RESULT" == "command terminated with exit code 1" ]]; then
      echo "❌ Connection refused on port $PORT. Retrying..."
      ((ATTEMPT++))
      PORT=$((PORT + 1))
    else
      echo "UE $i iPerf3 test complete."
      break
    fi
  done

  if [ $ATTEMPT -gt $RETRIES ]; then
    echo "UE $i failed to connect after $RETRIES attempts."
  fi

done

echo "All iPerf3 tests done. Results saved to text_files/iperf3_results.txt"
