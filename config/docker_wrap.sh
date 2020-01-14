#!/bin/bash

usage(){
    cat << EOF

This is a wrapper for docker.

Usage: $0 <command>
Commands:
    rmi_all         - Removes all images forcibly
    rm_all          - Removes all containers forcibly
    stop_byname     - Stops container forcibly if it exists and its name contains provides substring.
    stop_byimage    - Stops container forcibly if it exists and its image name contains provides substring.
    rm_byname       - Removes container forcibly if it exists and its name contains provides substring.
    rm_byimage      - Removes container forcibly if it exists and its image name contains provides substring.
    set_time_byname - Sets Moscow time inside the container. Requires 'tzdata' packet.

Example:
  $0 rm_all
  $0 stop_byname cassandra.service
  $0 set_time_byname jenkins.service

EOF
  exit 1
}

docker_rm_all_containers(){
    /usr/bin/docker rm -f $(docker ps -a | grep -v CONTAINER | awk '{ print $1 }')
    return 0
}

docker_rm_all_images(){
    /usr/bin/docker rmi -f $(docker images | grep -v "IMAGE ID" | awk '{ print $3 }')
    return 0
}

docker_rm_byname(){
    /usr/bin/docker ps -a -q --filter name=$1 |xargs --no-run-if-empty  /usr/bin/docker rm -f
    return 0
}

docker_rm_byimage(){
     /usr/bin/docker ps -a -q --filter ancestor=$1 |xargs --no-run-if-empty  /usr/bin/docker rm -f
     return 0
}

docker_stop_byname(){
    /usr/bin/docker ps -a -q --filter name=$1 |xargs --no-run-if-empty  /usr/bin/docker stop
    return 0
}

docker_stop_byimage(){
    /usr/bin/docker ps -a -q --filter ancestor=$1 |xargs --no-run-if-empty  /usr/bin/docker stop
    return 0
}

docker_set_time_byname(){
    /usr/bin/docker ps -a | grep -q $1 &&
        /usr/bin/docker exec -u 0 $1 ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
    return 0
}

docker_do(){
    for item in "${@:2}" ; do
        docker_$1 $item
    done
    return 0
}

COMMAND=$1 && shift
while [[ $# -gt 0 ]] ; do
    ARGS+=("$1")
    shift
done

case $COMMAND in
    rm_all)
        docker_rm_all_containers
        ;;
    rmi_all)
        docker_rm_all_images
        ;;
    stop_byname)
        docker_do stop_byname ${ARGS[@]}
        ;;
    stop_byimage)
        docker_do stop_byimage ${ARGS[@]}
        ;;
    rm_byname)
        docker_do rm_byname ${ARGS[@]}
        ;;
    rm_byimage)
        docker_do rm_byimage ${ARGS[@]}
        ;;
    set_time_byname)
        sleep 10
        docker_do set_time_byname ${ARGS[@]}
        ;;
    configure)
        configure_kishmish
        ;;
    archive_and_clean)
        docker_do archive_and_clean ${ARGS[@]}
        ;;
    *)
        echo "Incorrect command supplied"
        usage
    ;;
esac
exit 0
