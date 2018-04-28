#!/usr/bin/env bash

FILE_NAME=$0
FILE_DIR=$(dirname $0)
SH_ROOT_DIR=$(cd $FILE_DIR;pwd)  #脚本根目录

SOURCE_INSTALL=/opt/source_install     # 指定源码安装的路径
SYS_PATH_CONF=/etc/profile
SDSOM_CONF=/var/lib/sdsom/etc/sdsom/sdsom.conf
CEPH_CONF=/var/lib/ceph/etc/ceph/ceph.conf



check_return_code()
{
    retcode="$1"
    action="$2"
    msg="$3"
    if [ "${retcode}" != "0" ]; then
        echo "${action} failed! Error message: ${msg}"
        exit 2
    else
        echo "${action} successfully!"
    fi
}



# pass
uninstall_rabbitmq(){
    echo "==========uninstalling rabbitmq========="
    echo "clean rabbitmq config...."
    rabbitmqctl stop  &>/dev/null
    sed -i '/^ERLANG_HOME=.*/d' $SYS_PATH_CONF
    sed -i '/^export PATH=$PATH:$ERLANG_HOME\/bin.*/d' $SYS_PATH_CONF
    sed -i '/^export ERLANG_HOME.*/d' $SYS_PATH_CONF
    sed -i '/^export PATH=$PATH:\/opt\/source_install\/rabbitmq_server\/sbin.*/d' $SYS_PATH_CONF
    source $SYS_PATH_CONF
    echo "removing rabbitmq installed packages..."
    rm -rf "${SOURCE_INSTALL}/erlang"
    rm -rf "${SOURCE_INSTALL}/rabbitmq_server"
    rm -f /usr/sbin/rabbitmq*
    echo "======uninstall rabbitmq finished======="
}




uninstall_libreoffice(){
    echo "Removing libreoffice..."
    yum remove -y  "libreoffice*"  &>/dev/null
    echo "Removed libreoffice "
}


# pass
uninstall_python_modules(){
    cat $SH_ROOT_DIR/tools/python_modules/module_list|xargs pip uninstall  -y &>/dev/null
    check_return_code $? "Uninstalling python modules"
}

unistall_


uninstall_python_modules
