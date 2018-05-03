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
    echo "Uninstalling rabbitmq"
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
    echo "Uninstalling rabbitmq completed."
}

uninstall_rgw_api(){
    echo "Removing rgw_api configure..."
    sed -i '/^\[back_process\]/d'  $SDSOM_CONF
    sed -i '/^back_proc_url.*/d'  $SDSOM_CONF
    sed -i '/^rgw_rabbit_mq_if_use_back_process.*/d'  $CEPH_CONF
    sed -i '/^mq_host.*/d'  $CEPH_CONF
    sed -i '/^rgw_back_process_req_header.*/d'  $CEPH_CONF
    echo "Removing rgw_api configure completed."
}


uninstall_libreoffice(){
    echo "Removing libreoffice..."
    yum remove -y  "libreoffice*"  &>/dev/null
    echo "Removing libreoffice completed."
}


uninstall_python_modules(){
    cat $SH_ROOT_DIR/tools/python_modules/module_list|xargs pip uninstall  -y &>/dev/null
    check_return_code $? "Uninstalling python modules"
}


uninstall_ffmpeg(){
    echo "Removing ffmpeg..."
    rm -rf "${SOURCE_INSTALL}/yasm"
    rm -rf "${SOURCE_INSTALL}/ffmpeg"
    rm -rf /usr/local/bin/ffmpeg
    sed -i '/^export PATH=$PATH:\/opt\/source_install\/ffmpeg.*/d' $SYS_PATH_CONF
    echo "Removing ffmpeg completed."
}

echo '======START TO REMOVE BACKGROUND PROCESS ENVIRONMENT======='
echo "Stop backprocess web api"
ps -ef |grep -v grep|grep start_api|awk '{print $2}'|xargs kill -9  &>/dev/null
echo "Stop backprocess service"
ps -ef |grep -v grep|grep process_server|awk '{print $2}'|xargs kill -9  &>/dev/null

uninstall_python_modules
uninstall_rgw_api
uninstall_rabbitmq
uninstall_ffmpeg
uninstall_libreoffice

echo '======REMOVED BACKGROUND PROCESS ENVIRONMENT======='