#!/bin/bash

NAMESPACE="oai"
HELM_RELEASE="ueransim-gnb"
HELM_CHART="ueransim-5g-ran/ueransim-gnb"
DURATION=300
IPERF_SCRIPT="./run_iperf3_tests.sh"  
UE_COUNTS=(5 10 15 20 25 30 35 40 45 50)

# Rends ton script exécutable au cas où
chmod +x "$IPERF_SCRIPT"

for COUNT in "${UE_COUNTS[@]}"; do
  # Upgrade helm chart avec nouveau nombre d'UEs
  kubectl delete deploy ueransim-gnb-ues -n oai
  helm upgrade -n "$NAMESPACE" "$HELM_RELEASE" "$HELM_CHART" --set ues.count=$COUNT

  # Attendre que tous les pods soient en état "Running"
  while true; do
    NOT_READY=$(kubectl get pods -n "$NAMESPACE" --no-headers | grep -v 'Running' | wc -l)
    if [ "$NOT_READY" -eq 0 ]; then
      break
    fi
    sleep 5
  done

  # Réinitialiser le fichier de contrôle
  echo "0" > text_files/go.txt

  echo "Running iPerf3 script for $COUNT UEs during $DURATION seconds..."
  $IPERF_SCRIPT "$DURATION" &
  IPERF_PID=$!

  while kill -0 "$IPERF_PID" 2>/dev/null; do
    GO=$(cat text_files/go.txt 2>/dev/null || echo "0")
    MEM_FREE=$(free | awk '/Mem:/ {printf "%.2f", $7/$2 * 100}')

    if [[ "$GO" == "1" ]]; then
      echo "go.txt == 1 → ending test..."
      kill "$IPERF_PID"
      break
    fi

    if (( $(echo "$MEM_FREE < 6.0" | bc -l) )); then
      echo "Low memory ($MEM_FREE%) → killing test."
      kill "$IPERF_PID"
      break
    fi

    sleep 3
  done

done

echo ""
echo "All experiments completed."
