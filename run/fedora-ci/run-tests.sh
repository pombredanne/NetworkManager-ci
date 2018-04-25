RELEASE=$1

MY_PATH="`dirname \"$0\"`"
TESTS=$(cat $MY_PATH/$RELEASE.tests)

# Add failures and test counter variables
COUNTER=0
FAILURES=()

RESULTS_DIR=/tmp/artifacts
RESULTS=$RESULTS_DIR/RESULTS

echo "PASS" > $RESULTS

echo "WILL RUN:"
echo $TESTS

cd NetworkManager-ci

# For all tests
for T in $TESTS; do
    echo "RUNING $T"
    if [[ $T == *nmtui* ]]; then
        NMTEST=NetworkManager-ci_Test$COUNTER"_"$T nmtui/./runtest.sh $T; rc=$?
    else
        NMTEST=NetworkManager-ci_Test$COUNTER"_"$T nmcli/./runtest.sh $T; rc=$?
    fi


    if [ $rc -ne 0 ]; then
        # Overal result is FAIL
        echo "FAIL" > $RESULTS
        # Move reports to /var/www/html/results/ and add FAIL prefix
        if [[ $T == *nmtui* ]]; then
            mv /tmp/report_NetworkManager-ci_Test$COUNTER"_"$T.log $RESULTS_DIR/FAIL-NetworkManager-ci_Test$COUNTER"_"$T.log
        else
            mv /tmp/report_NetworkManager-ci_Test$COUNTER"_"$T.html $RESULTS_DIR/FAIL-NetworkManager-ci_Test$COUNTER"_"$T.html
        fi
        FAILURES+=($T)
    else
        # Move reports to /tmp/artifacts
        if [[ $T == *nmtui* ]]; then
            mv /tmp/report_NetworkManager-ci_Test$COUNTER"_"$T.log $RESULTS_DIR/NetworkManager-ci_Test$COUNTER"_"$T.log
        else
            mv /tmp/report_NetworkManager-ci_Test$COUNTER"_"$T.html $RESULTS_DIR/NetworkManager-ci_Test$COUNTER"_"$T.html
        fi
    fi

    COUNTER=$((COUNTER+1))

done

rc=1
# Write out tests failures
if [ ${#FAILURES[@]} -ne 0 ]; then
    echo "** $COUNTER TESTS PASSED"
    echo "--------------------------------------------"
    echo "** ${#FAILURES[@]} TESTS FAILED"
    echo "--------------------------------------------"
    for FAIL in "${FAILURES[@]}"; do
        echo "$FAIL"
    done
else
    rc=0
    echo "** ALL $COUNTER TESTS PASSED!"
fi

exit $rc
