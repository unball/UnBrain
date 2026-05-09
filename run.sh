mkdir -p logs

PORTA="5001"

if [[ -n $1 ]]; then
    PORTA="$1"
fi

( (cd MainVision && ./main.py --port "$PORTA" --n_robots 1) & (sleep 0.5s && python3 src/main.py --team-color blue --mainvision --port "$PORTA" --n_robots 0 --static-entities) )