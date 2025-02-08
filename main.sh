#!/usr/bin/env bash

''':'

run() {
    declare -a cmd=("$@")

    {
        echo "#!/usr/bin/env bash"
        declare -p cmd
        echo 'exec "${cmd[@]}"'

        # 以下部分不会被执行到
        printf '%q ' "${cmd[@]}"
        printf '\n'
    } > "$LOGDIR/go.sh"

    chmod +x "$LOGDIR/go.sh"

    {
        time script --return \
                    --command "$LOGDIR/go.sh" \
                    --log-timing "$LOGDIR/timing" \
                    "$LOGDIR/log"
    } 2>"$LOGDIR/time"

    return $?
}

send() {
    curl -X POST -H "Content-Type: application/json" \
         -T "$1" \
         --silent --show-error \
         "$NTFY_URL"
    echo
}

LOGROOT=${LOGROOT:-/tmp}

LOGDIR=$(mktemp -d -p "$LOGROOT" ntfy-XXXXXX)

date +'%Y-%m-%d %H:%M:%S' >"$LOGDIR/time-start"

run "$@"
CODE=$?
echo $CODE >"$LOGDIR/status"

date +'%Y-%m-%d %H:%M:%S' >"$LOGDIR/time-end"

cat "$LOGDIR/time"
echo "Log saved at $LOGDIR"

python $0 "$LOGDIR" >"$LOGDIR/msg.json" && send "$LOGDIR/msg.json"

exit $CODE

'''
