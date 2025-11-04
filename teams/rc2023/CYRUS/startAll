#!/bin/bash
HOST=127.0.0.1

port=6000
coach_port=6002

while [ $# -gt 0 ]
	do
	case $1 in

    -p|--port)
      if [ $# -lt 2 ]; then
        usage
        exit 1
      fi
      port="${2}"
      shift 1
      ;;

    -P|--coach-port)
      if [ $# -lt 2 ]; then
        usage
        exit 1
      fi
      coach_port="${2}"
      shift 1
      ;;
  esac

  shift 1
done

HOMEDIR=`dirname $0`
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 1&
sleep 1.0
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 2 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 3 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 4 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 5 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 6 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 7 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 8 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 9 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 10 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 11 &
sleep 0.1
${HOMEDIR}/start ${HOST} ${HOMEDIR} ${port} ${coach_port} 12 &
sleep 0.1
