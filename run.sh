mkdir -p logs

PORTA="5001"

if [[ -n $1 ]]; then
    PORTA="$1"
fi

( (cd MainSystem && ./main.py --port "$PORTA") & (sleep 0.5s && python3 ALP-Winners/src/main.py --port "$PORTA") )