mkdir -p logs

PORTA="5001"

if [[ -n $1 ]]; then
    PORTA="$1"
fi

( (cd MainVision && ./main.py --port "$PORTA") & (sleep 0.5s && python3 src/main.py --team-color yellow --mainvision --port "$PORTA") )