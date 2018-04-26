#!/usr/bin/env bash

# create back_process environment
FILE_NAME=$0
FILE_DIR=$(dirname $0)
SH_ROOT_DIR=$(cd $FILE_DIR;pwd)  #脚本根目录

SOURCE_INSTALL=/opt/source_install     # 指定源码安装的路径
SDSOM_CONF=/var/lib/sdsom/etc/sdsom/sdsom.conf
CEPH_CONF=/var/lib/ceph/etc/ceph/ceph.conf
SYS_PATH_CONF=/etc/profile
LIBREOFFICE_DEP_RPMS="${SH_ROOT_DIR}/tools/libreoffice/libreoffice_dep_rpms/"
RABBITMQ_DEP_RPMS="${SH_ROOT_DIR}/tools/rabbitmq/mq_dep_rpms"


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


install_ffmpeg(){
    echo "Prepare to install ffmpeg..."
    cd "${SH_ROOT_DIR}/tools/ffmpeg" && tar -xf  "yasm-1.3.0.tar.gz"
    check_return_code $? "tar yasm-1.3.0.tar.gz"
    if [ ! -d "${SOURCE_INSTALL}/yasm" ];then
        mkdir -p "${SOURCE_INSTALL}/yasm"
    fi
    #todo:如指定安装，则需要添加到/etc/source中
    cd "${SH_ROOT_DIR}/tools/ffmpeg/yasm-1.3.0" && ./configure  && make && make install
    check_return_code $? "install yasm-1.3.0"

    cd "${SH_ROOT_DIR}/tools/ffmpeg" && tar -xf  "ffmpeg-3.4.2.tar.bz2"
    check_return_code $? "tar ffmpef-3.4.2"
    if [ ! -d "${SOURCE_INSTALL}/ffmpeg" ];then
        mkdir -p "${SOURCE_INSTALL}/ffmpeg"
    fi
    cd "${SH_ROOT_DIR}/tools/ffmpeg/ffmpeg-3.4.2" && ./configure --prefix="${SOURCE_INSTALL}/ffmpeg" && make && make install
    check_return_code $? "install ffmpeg-3.4.2"
}


install_libreoffice(){
    echo "Prepare to install libreoffice..."
    echo "Add window fonts to linux"
    /usr/bin/cp -rf "${SH_ROOT_DIR}/tools/libreoffice/fonts/*"   /usr/share/fonts/
    cd /usr/share/fonts/
    mkfontscale
    mkfontdir   # 这两条命令是生成字体的索引信息
    fc-cache    # 更新字体缓存
    echo "install dependence rpms for libreoffice"
    yum -y install "${LIBREOFFICE_DEP_RPMS}/*.rpm"
    check_return_code $? "install libreoffice"

}


# pass
config_rabbitmq(){
    echo "config rabitmq...."
    rabbitmq-server -detached                                 # 启动rabbitmq
    sleep 3
    rabbitmqctl add_user root sandstone                       # 添加用户,密码
    rabbitmqctl set_permissions -p / root ".*" ".*" ".*"      # 授权/空间
    rabbitmqctl set_user_tags root administrator              # 设置管理员角色
    rabbitmqctl add_vhost sdsom                               # 添加空间sdsom
    rabbitmqctl set_permissions -p sdsom root ".*" ".*" ".*"  # 授权sdsom虚拟空间
    rabbitmq-plugins  enable  rabbitmq_management             # 开启15672端口浏览器访问
    sleep 2
    rabbitmqctl stop                                          # 重启生效
    sleep 2
    rabbitmq-server -detached
    echo "config rabbitmq complete."
}

# pass
install_rabbitmq(){
    echo "Prepare to install rabbitmq..."
    echo "installing dependence rpms..."
    cd ${RABBITMQ_DEP_RPMS} && yum -y install ./*.rpm  &>/dev/null
    echo "install dependence rpms complete."
    cd "${SH_ROOT_DIR}/tools/rabbitmq" && tar -xf "otp_src_18.3.tar.gz"  &>/dev/null
    cd "./otp_src_18.3"
    if [ ! -d "${SOURCE_INSTALL}/erlang" ];then
        mkdir -p "${SOURCE_INSTALL}/erlang"
    fi
    echo "installing erlang for mq, it needs some time..."
    ./configure --prefix="${SOURCE_INSTALL}/erlang" -with-ssl -enable-rhreads -enable-smp-support \
     -enable-kernel-poll -enable-hipe -without-javac  &>/dev/null
    make && make install
    check_return_code $? "install erlang for rabbitmq"

    echo "installing rabbitmq..."
    cd "${SH_ROOT_DIR}/tools/rabbitmq" && tar -xf "rabbitmq-server-generic-unix-3.6.1.tar" -C $SOURCE_INSTALL
    cd  $SOURCE_INSTALL && mv  rabbitmq_server-3.6.1  rabbitmq_server
    check_return_code $? "install rabbitmq"
    echo "add some config in sys path..."
    /usr/bin/cp -rf $SYS_PATH_CONF  "${SYS_PATH_CONF}_bak"
    cat << EOF >> $SYS_PATH_CONF

# for rabbitmq
ERLANG_HOME=/opt/source_install/erlang
export PATH=\$PATH:\$ERLANG_HOME/bin
export ERLANG_HOME
export PATH=\$PATH:/opt/source_install/rabbitmq_server/sbin
EOF
    source $SYS_PATH_CONF
    check_return_code $? "install rabbitmq complete."

    config_rabbitmq
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

config_backproc_url(){
    echo "config back_process url for OM..."
    cat <<EOF >> $SDSOM_CONF

[back_process]
back_proc_url = http://10.10.7.151:5050/api/v1/back_process
EOF


# todo:待测
    cat <<EOF >> $CEPH_CONF

rgw_rabbit_mq_if_use_back_process = true
mq_host = "10.10.7.151"
rgw_back_process_req_header = HTTP_X_AMZ_META_BP

EOF

rgw_rabbit_mq_if_use_back_process = true
mq_host = 10.10.7.151

    echo "config complete."



}

echo '======START TO CREATE BACKGROUND PROCESS ENVIRONMENT======='
#install_rabbitmq
#uninstall_rabbitmq
#config_backproc_url

# todo:waiting for check
install_libreoffice
#install_ffmpeg
