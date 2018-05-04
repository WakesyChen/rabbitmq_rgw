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
PYTHON_MODULES="${SH_ROOT_DIR}/tools/python_modules"

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


config_rabbitmq(){
    echo "config rabitmq...."
    ps -ef |grep -v grep |grep rabbitmq|awk '{print $2}'|xargs kill -9 &>/dev/null
    sleep 2
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



install_rabbitmq(){
    echo "Prepare to install rabbitmq..."
    echo "installing dependence rpms..."
    cd ${RABBITMQ_DEP_RPMS} && yum -y install ./*.rpm  &>/dev/null
    echo "install dependence rpms complete."
    cd "${SH_ROOT_DIR}/tools/rabbitmq" && tar -xzf "otp_src_18.3.tar.gz"  &>/dev/null
    cd "./otp_src_18.3"
    if [ ! -d "${SOURCE_INSTALL}/erlang" ];then
        mkdir -p "${SOURCE_INSTALL}/erlang"
    fi
    echo "installing erlang for mq, it may take some time..."
    ./configure --prefix="${SOURCE_INSTALL}/erlang" -with-ssl -enable-rhreads -enable-smp-support \
     -enable-kernel-poll -enable-hipe -without-javac  &>/dev/null
    make &>/dev/null && make install   &>/dev/null
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


install_ffmpeg(){
    echo "<<install tool [ffmpeg] to convert image types>>"
    cd "${SH_ROOT_DIR}/tools/ffmpeg" && tar -xzf  "yasm-1.3.0.tar.gz"
    cd "${SH_ROOT_DIR}/tools/ffmpeg/yasm-1.3.0"
    echo "installing yasm for ffmpeg..."
    ./configure  &>/dev/null && make &>/dev/null && make install &>/dev/null
    check_return_code $? "installing yasm for ffmpeg"
    cd "${SH_ROOT_DIR}/tools/ffmpeg" && tar -xzf  "ffmpeg-3.4.2.tar.gz"
    if [ ! -d "${SOURCE_INSTALL}/ffmpeg" ];then
        mkdir -p "${SOURCE_INSTALL}/ffmpeg"
    fi
    cd "${SH_ROOT_DIR}/tools/ffmpeg/ffmpeg-3.4.2"
    echo "installing ffmpeg, it may take some time..."
    ./configure --prefix="${SOURCE_INSTALL}/ffmpeg" &>/dev/null && make &>/dev/null && make install &>/dev/null
    check_return_code $? "installing ffmpeg"
    cat <<EOF >> $SYS_PATH_CONF
export PATH=\$PATH:/opt/source_install/ffmpeg/bin
EOF
    source $SYS_PATH_CONF
}


install_libreoffice(){
    echo "<<install tool [libreoffice] to convert doc type to pdf>>"
    echo "Add window fonts to linux"
    /usr/bin/cp -rf ${SH_ROOT_DIR}/tools/libreoffice/fonts/*   /usr/share/fonts/
    cd /usr/share/fonts/
    mkfontscale
    mkfontdir   # 这两条命令是生成字体的索引信息
    fc-cache    # 更新字体缓存
    echo "installing libreoffice, it may take some time..."
    yum -y install ${LIBREOFFICE_DEP_RPMS}/*.rpm &>/dev/null
    check_return_code $? "install libreoffice"
}


config_rgw_api(){
    echo "***Start to config the ip for rgw and api***"
    ip_addr=$1

    # config sdsom
    /usr/bin/cp -rf $SDSOM_CONF ${SDSOM_CONF}_bak
    cat <<EOF >> $SDSOM_CONF

[back_process]
back_proc_url = http://${ip_addr}:5050/api/v1/back_process
EOF
    service sdsom-httpd restart   # restart httpd
    echo "Config back_process for api"

    # config ceph， must be rgw node.
    /usr/bin/cp -rf  $CEPH_CONF  ${CEPH_CONF}_bak
    cat <<EOF >> $CEPH_CONF

rgw_rabbit_mq_if_use_back_process = true
mq_host = $ip_addr
rgw_back_process_req_header = HTTP_X_AMZ_META_BP

EOF
    ps -ef |grep radosgw|grep -v grep|awk '{print $2}'|xargs kill -9  &>/dev/null # soon restart by rcm
    echo "Config back_process for rgw"
}


install_python_modules(){

    echo "***Start to install the python modules***"
    cd $PYTHON_MODULES
    tar -xzf setuptools-39.0.1.tar.gz
    cd setuptools-39.0.1/
    python setup.py build    &>/dev/null  &&  python setup.py install  &>/dev/null
    check_return_code $? "Installing setuptools"

    cd $PYTHON_MODULES
    tar -xzf pip-10.0.0b2.tar.gz
    cd pip-10.0.0b2/
    python setup.py install  &>/dev/null
    check_return_code $? "Installing pip"

    cd $PYTHON_MODULES
    pip install --no-index --find-links=./  -r requirements.txt   &>/dev/null
    check_return_code $? "Installing requirements modules"
}


note_message(){
    echo '======START TO CREATE BACKGROUND PROCESS ENVIRONMENT======='
    echo "NOTES:"
    ps -ef |grep radosgw|grep -v grep  &>/dev/null
    if   [ $? == '0' ];then
        echo "1、Rgw service already created on this node, continue."
    else
        echo "1、Please create rgw service on this node first."
        exit -1
    fi
    echo "2、Please input the ip address of the rgw service on this node:"
    read rgw_ip
    ping -c 3 $rgw_ip &>/dev/null   # simple check
    if [ $? != '0' ];then
        echo "The ip adress is not correct!"
        exit -2
    else
        echo "rgw_ip:$rgw_ip."
    fi
}

note_message
config_rgw_api $rgw_ip
install_python_modules
install_rabbitmq
install_ffmpeg
install_libreoffice



