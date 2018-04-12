#!/bin/bash
LANG=C
LOCAL_SHELL_PATH="$(dirname $0)"
LOCAL_SHELL_ABSOLUTE_PATH="$(cd $LOCAL_SHELL_PATH; pwd )"
LOCAL_SHELL_NAME="$(basename $0)"

. ${LOCAL_SHELL_PATH}/util/common.sh
. ${LOCAL_SHELL_PATH}/util/logger.sh

check_return_code()
{
    retcode="$1"
    action="$2"
    msg="$3"
    if [ "${retcode}" != "0" ]; then
        log_error "${action} failed! Error message: ${msg}"
        exit 2
    else
        log_info "${action} successfully!"
    fi
}

# Install sandstone
install_sandstone()
{
    log_info "Installing ${BASE_SDS}..."
	filename=$(ls ${LOCAL_SHELL_PATH}/pkgs/sds/${BASE_SDS}*-linux-x64-installer.run)
    chmod +x ${filename}
    msg=$(${filename}  --mode unattended --prefix "/var/lib/ceph" 2>&1)
    check_return_code $? "Install ${BASE_SDS} bin pkgs" "${msg}"

	PID_PATH="/var/lib/ceph/var/run/ceph"
	mkdir -p "$PID_PATH"
	chown -R sdsadmin:sdsadmin  "$PID_PATH"
}

# Install sdsom
install_sdsom()
{
    log_info "Installing sdsom..."
    filename=$(ls ${LOCAL_SHELL_PATH}/pkgs/om/sdsom*linux-x64-installer.run)
    chmod +x ${filename}
    msg=$(${filename} --mode unattended --prefix "/var/lib/sdsom" --installpath $LOCAL_SHELL_ABSOLUTE_PATH 2>&1)
    check_return_code $? "Install sdsom pkgs" "${msg}"

    install_sdssqlit
    check_return_code $? "Install sdssqlit pkgs"

    cp ${LOCAL_SHELL_PATH}/version  /var/lib/sdsom/etc
    check_return_code $? "Config version info"

    msg=$(ln -s  /usr/lib/python2.7/site-packages/boto   /var/lib/sdsom/venv/lib/python2.7/site-packages/boto)
    check_return_code $? "Create soft link for python-boto library" "${msg}"
}

install_sdssqlit()
{
    . ${INSTALL_ID_FILE}
    [ -e /var/lib/sdsom/usr/lib64/libsqlite3.so.0 ] && rm -f /var/lib/sdsom/usr/lib64/libsqlite3.so.0

    libsqlite_rbd_path="/var/lib/sdsom/usr/lib64/sqlite3-rbd"
    libsqlite_normal_path="/var/lib/sdsom/usr/lib64/sqlite3-normal"
    mkdir -p ${libsqlite_rbd_path}
    mkdir -p ${libsqlite_normal_path}

    ln -s ${INSTALLDIR}/lib/libsdssqlite3.so.0 ${libsqlite_rbd_path}/libsqlite3.so.0

    local preDir=$(pwd)
    cd ${libsqlite_normal_path}
    ln -s ../libsqlite3.so.0.8.6 libsqlite3.so.0
    cd ${preDir}
    return 0
}


# Install depends pkgs
install_extra_rpm()
{
    if [ "${IS_OS_EL7}" != "${STR_TRUE}" ]; then
        if [ "${G_JZGK}" = "jzgk" ]; then
            install_rpm iscsi-initiator-utils-6 ${LOCAL_SHELL_PATH}/pkgs/iscsid/iscsi-initiator-utils-6.2.0.873-10.el6.x86_64.rpm
            install_rpm device-mapper-multipath-libs-0 ${LOCAL_SHELL_PATH}/pkgs/multipath/device-mapper-multipath-libs-0.4.9-72.el6.x86_64.rpm
            install_rpm device-mapper-multipath-0 ${LOCAL_SHELL_PATH}/pkgs/multipath/device-mapper-multipath-0.4.9-72.el6.x86_64.rpm
        fi
        install_rpm libudev-147 ${LOCAL_SHELL_PATH}/pkgs/others/libudev-147-2.51.el6.x86_64.rpm
        install_rpm xfsprogs-3 ${LOCAL_SHELL_PATH}/pkgs/xfs/xfsprogs-3.1.1-14.el6.x86_64.rpm
        install_rpm xfsprogs-devel-3 ${LOCAL_SHELL_PATH}/pkgs/xfs/xfsprogs-devel-3.1.1-14.el6.x86_64.rpm
    else
        if [ "${G_JZGK}" = "jzgk" ]; then
            # Iscsi
            install_rpm iscsi-initiator-utils-6 ${LOCAL_SHELL_PATH}/pkgs/iscsid/iscsi-initiator-utils-6.2.0.873-29.el7.x86_64.rpm
            # Multipath
            install_rpm iscsi-initiator-utils-iscsiuio-6 ${LOCAL_SHELL_PATH}/pkgs/iscsid/iscsi-initiator-utils-iscsiuio-6.2.0.873-29.el7.x86_64.rpm
            install_rpm device-mapper-multipath-libs-0 ${LOCAL_SHELL_PATH}/pkgs/multipath/device-mapper-multipath-libs-0.4.9-77.el7.x86_64.rpm
            install_rpm device-mapper-multipath-0 ${LOCAL_SHELL_PATH}/pkgs/multipath/device-mapper-multipath-0.4.9-77.el7.x86_64.rpm
        fi
        if [ ! -e /lib64/libudev.so.0 ] && [ -e /lib64/libudev.so.1 ];then
            ln -s /lib64/libudev.so.1 /lib64/libudev.so.0
            check_return_code $? "Create libudev symlink"
        fi
        if [ "${IS_OS_EL7_YH}" = "${STR_TRUE}" ]; then
            check_rpm nss-softokn-freebl-3.16
            check_rpm autogen-libopts-5.18
            check_rpm mailx-12.5
            check_rpm ntpdate-4.2
            check_rpm ntp-4.2
            check_rpm xfsprogs-3.2.1
        else
            # Ntp
            install_rpm nss-softokn-freebl-3 ${LOCAL_SHELL_PATH}/pkgs/others/nss-softokn-freebl-3.16.2.3-9.el7.x86_64.rpm
            install_rpm autogen-libopts-5 ${LOCAL_SHELL_PATH}/pkgs/others/autogen-libopts-5.18-5.el7.x86_64.rpm
            install_rpm mailx-12 ${LOCAL_SHELL_PATH}/pkgs/others/mailx-12.5-12.el7_0.x86_64.rpm

            if [ "${IS_OS_EL7_2}" == "${STR_TRUE}" ]; then
                if [ "${IS_OS_EL_CENTOS}" == "${STR_TRUE}" ]; then
                    install_rpm ntpdate-4 ${LOCAL_SHELL_PATH}/pkgs/others/ntpdate-4.2.6p5-22.el7.centos.x86_64.rpm
                    install_rpm ntp-4 ${LOCAL_SHELL_PATH}/pkgs/others/ntp-4.2.6p5-22.el7.centos.x86_64.rpm
                else
                    install_rpm ntpdate-4 ${LOCAL_SHELL_PATH}/pkgs/others/ntpdate-4.2.6p5-22.el7.x86_64.rpm
                    install_rpm ntp-4 ${LOCAL_SHELL_PATH}/pkgs/others/ntp-4.2.6p5-22.el7.x86_64.rpm
                fi
            elif [ "${IS_OS_EL7_1}" == "${STR_TRUE}" ]; then
                if [ "${IS_OS_EL_CENTOS}" == "${STR_TRUE}" ]; then
                    install_rpm ntpdate-4 ${LOCAL_SHELL_PATH}/pkgs/others/ntpdate-4.2.6p5-19.el7.centos.x86_64.rpm
                    install_rpm ntp-4 ${LOCAL_SHELL_PATH}/pkgs/others/ntp-4.2.6p5-19.el7.centos.x86_64.rpm
                else
                    check_rpm ntpdate-4.2
                    check_rpm ntp-4.2
                fi
            fi
        fi

    fi
}

# Install depends pkgs for jewel version ceph
install_extra_rpm_for_jewel()
{
    if [ "${IS_OS_EL7}" == "${STR_TRUE}" ]; then
        install_rpm boost-iostreams    ${LOCAL_SHELL_PATH}/pkgs/jewel/boost-iostreams-1.53.0-23.el7.x86_64.rpm
        install_rpm boost-random       ${LOCAL_SHELL_PATH}/pkgs/jewel/boost-random-1.53.0-23.el7.x86_64.rpm
        install_rpm boost-regex        ${LOCAL_SHELL_PATH}/pkgs/jewel/boost-regex-1.53.0-23.el7.x86_64.rpm
        install_rpm libunwind          ${LOCAL_SHELL_PATH}/pkgs/jewel/libunwind-1.1-10.el7.x86_64.rpm
        install_rpm gperftools-libs    ${LOCAL_SHELL_PATH}/pkgs/jewel/gperftools-libs-2.1-1.el7.x86_64.rpm
    fi

    return 0
}

#to use systemctl for radosgw
config_radosgw_service() {
	#generate systemctl service file for radosgw
	rgw_service_path="/lib/systemd/system/radosgw@.service"
    cat <<EOF > ${rgw_service_path}
[Unit]
Description=Ceph Object Storage Service
[Service]
LimitNOFILE=1048576
LimitNPROC=1048576
Type=forking
ExecStart=-/var/lib/ceph/bin/radosgw  --pid-file /var/lib/ceph/var/run/ceph/client.radosgw.%I.pid\
          -c /var/lib/ceph/etc/ceph/ceph.conf -n client.radosgw.%I  --setuser sdsadmin --setgroup sdsadmin

EOF

}

#to use systemctl for nginx
config_nginx_service() {
	#generate systemctl service file for nginx
	nginx_service_path="/lib/systemd/system/nginx.service"
    cat <<EOF > ${nginx_service_path}
[Unit]
Description=Nginx Service
[Service]
LimitNOFILE=1048576
LimitNPROC=1048576
Type=forking
ExecStart=-/var/lib/ceph/bin/nginx  -c  /var/lib/ceph/nginx/conf/rgw_nginx.conf  -p /var/lib/ceph/nginx/
ExecReload=-/var/lib/ceph/bin/nginx -c  /var/lib/ceph/nginx/conf/rgw_nginx.conf  -p /var/lib/ceph/nginx/  -s reload

EOF
}

#to use systemctl for badsector_mon.service
config_badsector_mon_service() {
	#generate systemctl service file for badsector_mon
	badsector_mon_service_path="/lib/systemd/system/badsector_mon.service"
    cat <<EOF > ${badsector_mon_service_path}
[Unit]
Description=Bad Sector Monitor Service
[Service]
LimitNOFILE=1048576
LimitNPROC=1048576
Type=simple
Environment='LD_LIBRARY_PATH=/var/lib/sdsom/usr/lib64/'
ExecStart=-/var/lib/sdsom/venv/bin/python /var/lib/sdsom/venv/bin/monitor_bad_sector.py
EOF

}

#to use systemctl for vsftpd
config_vsftpd_service() {
    vsftpd_service_path="/lib/systemd/system/vsftpd.service"
    cat <<EOF > ${vsftpd_service_path}
[Unit]
Description=Vsftpd ftp daemon
After=network.target
[Service]
Type=forking
ExecStart=/var/lib/ceph/vsftpd/vsftpd /var/lib/ceph/vsftpd/vsftpd.conf
[Install]
WantedBy=multi-user.target
EOF

}

add_logstash_service() {
	#generate systemctl service file for logstash
	logstash_service_path="/lib/systemd/system/logstash.service"
    cat <<EOF > ${logstash_service_path}
[Unit]
Description=ELK module Logstash Service
[Service]
LimitNOFILE=1048576
LimitNPROC=1048576
Type=simple
Environment="JAVA_HOME=/var/lib/sdsom/venv/jre1.8.0_151"
Environment="LOGSTASH_HOME=/var/lib/sdsom/venv/logstash-2.4.1"
ExecStart=-/var/lib/sdsom/venv/logstash-2.4.1/bin/logstash  -f /var/lib/sdsom/venv/logstash-2.4.1/conf/logstash.conf
EOF

}

# config logstash service
config_logstash_service()
{
    tar xzvf ${LOCAL_SHELL_PATH}/pkgs/logstash/jre-8u151-linux-x64.tar.gz  -C /var/lib/sdsom/venv/  &>/dev/null
    tar xzvf ${LOCAL_SHELL_PATH}/pkgs/logstash/logstash-2.4.1.tar.gz  -C /var/lib/sdsom/venv/  &>/dev/null
	add_logstash_service

    return 0
}


modify_elasticsearch_config(){
    log_info "Start to modify elasticsearch configure..."
    # 1) add venv JAVA_HOME into elasticsearch environment
    ES_SHELL_FILE=/usr/share/elasticsearch/bin/elasticsearch
    cp  -rf  $ES_SHELL_FILE  ${ES_SHELL_FILE}_bak
    sed -i "142a JAVA_HOME=$JAVA_HOME" $ES_SHELL_FILE

    # 2) config the IP, nodes..
    ES_CONFIG_FILE=/etc/elasticsearch/elasticsearch.yml
    cp  -rf  $ES_CONFIG_FILE  "${ES_CONFIG_FILE}_bak"
    cat <<EOF >> $ES_CONFIG_FILE

cluster.name: elasticsearch #集群的名称，同一个集群该值必须设置成相同的

node.name: node3 #该节点的名字

node.master: true #该节点有机会成为master节点

node.data: true #该节点可以存储数据

network.bind_host: 0.0.0.0 #设置绑定的IP地址，可以是IPV4或者IPV6

#network.publish_host: 192.168.4.13 #设置其他节点与该节点交互的IP地址

network.host: 0.0.0.0 #该参数用于同时设置bind_host和publish_host

transport.tcp.port: 9300 #设置节点之间交互的端口号

transport.tcp.compress: true #设置是否压缩tcp上交互传输的数据

http.port: 9200 #设置对外服务的http端口号

http.max_content_length: 100mb #设置http内容的最大大小

http.enabled: true #是否开启http服务对外提供服务

#discovery.zen.ping.unicast.hosts: ["192.168.4.12","192.168.4.13","192.168.4.14"]
#设置集群中的Master节点的初始列表，可以通过这些节点来自动发现其他新加入集群的节点

EOF

}


# config elasticsearch service
config_elasticsearch_service(){

    ES_RPM_FILE="${LOCAL_SHELL_PATH}/pkgs/elasticsearch/elasticsearch-5.6.1.rpm"
    ES_IK_ZIP="${LOCAL_SHELL_PATH}/pkgs/elasticsearch/elasticsearch-analysis-ik-5.6.1.zip"

    ES_PLUGIN_PATH='/usr/share/elasticsearch/plugins/'
    JAVA_HOME='/var/lib/sdsom/venv/jre1.8.0_151'

    # already installed ?
    rpm -qa | grep elasticsearch
    if [ $? == '0' ];then
        log_info "Elasticsearch is already installed"
        # make sure the ik plugin installed
        unzip -d $ES_PLUGIN_PATH  -o $ES_IK_ZIP  &>/dev/null
        return 0
    fi

    if [ ! -f $ES_RPM_FILE ];then
        log_error "There is no es-rpm in $ES_RPM_FILE"
        return 0
    fi

    if [ -d $JAVA_HOME ];then
        # Install elasticsearch rpm
        log_info "Start to install elasticsearch-5.6.1.rpm..."
        rpm -ivh $ES_RPM_FILE  &>/dev/null
        unzip -d $ES_PLUGIN_PATH  -o $ES_IK_ZIP  &>/dev/null
        # Modify elasticsearch config
        modify_elasticsearch_config
    else
        log_error "Please install JDK before installing elasticsearch"

    fi
}

#configure ntpd
configure_ntpd(){
	ntpd_conf="/etc/sysconfig/ntpd"
    cat <<EOF > ${ntpd_conf}
# Command line options for ntpd
OPTIONS="-g -x"

EOF
}

#install ipvsadmin and keepalived for object storage
install_rpm_for_object_storage()
{
    if [ "${IS_OS_EL7}" == "${STR_TRUE}" ]; then
        install_rpm  ipvsadm                ${LOCAL_SHELL_PATH}/pkgs/object/ipvsadm-1.27-7.el7.x86_64.rpm
        install_rpm  net-snmp-libs          ${LOCAL_SHELL_PATH}/pkgs/object/net-snmp-libs-5.7.2-20.el7.x86_64.rpm
        install_rpm  net-snmp-agent-libs    ${LOCAL_SHELL_PATH}/pkgs/object/net-snmp-agent-libs-5.7.2-20.el7.x86_64.rpm
        install_rpm  keepalived             ${LOCAL_SHELL_PATH}/pkgs/object/keepalived-1.2.13-6.el7.x86_64.rpm
        install_rpm  python-boto            ${LOCAL_SHELL_PATH}/pkgs/object/python-boto-2.40.0-1.mga6.noarch.rpm
		install_rpm  vsftp                  ${LOCAL_SHELL_PATH}/pkgs/object/vsftpd-3.0.2-22.el7.x86_64.rpm

    else
        echo "OS version is not EL7, Object storage about rpm pks not installed"
    fi

    cp ${LOCAL_SHELL_PATH}/pkgs/object/service-keepalived   /etc/init.d/keepalived -f;
    chmod +x /etc/init.d/keepalived;
    config_radosgw_service
	config_nginx_service

    return 0
}

update_rpm_for_curl()
{
    if [ "${IS_OS_EL7}" == "${STR_TRUE}" ]; then
        msg=$(rpm -Uhv ${LOCAL_SHELL_PATH}/pkgs/curl/*.rpm  2>&1)
        if [ $? != "0" ]; then
            log_info "curl rpms are already updated!"
        else
            log_info "curl rpms update successfully!"
        fi
    fi
}

install_rpm()
{
    rpmname=$1
    filename=$2

    existed=$(rpmquery -a | grep ${rpmname})
    if [ "${existed}" == "" ]; then
        msg=$(rpm -i ${filename} 2>&1)
        check_return_code $? "Install ${rpmname}" "${msg}"
    else
        log_info "Rpm ${rpmname} is already installed!"
    fi
    return 0
}


check_rpm()
{
    rpmname=$1
    filename=$2

    existed=$(rpmquery -a | grep ${rpmname})
    if [ "${existed}" == "" ]; then
        check_return_code 1 "Please install ${rpmname} before continue. Check ${rpmname}" ""
        return 1
    else
        log_info "Package ${rpmname} is already installed!"
    fi
    return 0
}


configure_os_env()
{
    . /etc/default/sdsom

    # Configure env for performance
    msg=$(sh ${INSTALLDIR}/tools/configure/configure_ostune.sh 2>&1)
    check_return_code $? "OS tuning" "${msg}"

    # Configure os permission
    msg=$(sh ${INSTALLDIR}/tools/configure/configure_osperm.sh 2>&1)
    check_return_code $? "OS permission" "${msg}"

    # Configure udev storage rules
    udevadm_version=$(udevadm --version)
    check_return_code $? "Get udevadm version" "${msg}"
    if [ ${udevadm_version} -ge 147 ] && [ ${udevadm_version} -lt 208 ]; then
        # 6.5 udev
        cp -f ${INSTALLDIR}/etc/udev/rules.d/60-persistent-storage.rules.147 /etc/udev/rules.d/60-persistent-storage.rules
    elif [ ${udevadm_version} -ge 208 ] && [ ${udevadm_version} -lt 219 ]; then
        # 7.1 systemd udev
        cp -f ${INSTALLDIR}/etc/udev/rules.d/60-persistent-storage.rules.208 /etc/udev/rules.d/60-persistent-storage.rules
    elif [ ${udevadm_version} -ge 219 ]; then
        # 7.2 systemd udev
        cp -f ${INSTALLDIR}/etc/udev/rules.d/60-persistent-storage.rules.219 /etc/udev/rules.d/60-persistent-storage.rules
    fi

    check_return_code $? "Configure udev 60-persistent-storage.rules" "${msg}"

	configure_ntpd
	systemctl daemon-reload

    return 0
}

config_service_before_reboot()
{
    . /etc/default/sdsom
    # Config iscsi/multipathd
    if [ "${G_JZGK}" = "jzgk" ]; then
        msg=$(sh ${INSTALLDIR}/tools/configure/configure_iscsi.sh 2>&1)
        check_return_code $? "Configure iscsi/multipath" "${msg}"
    fi

    # off crond
    if [ "${IS_OS_EL7}" != "${STR_TRUE}" ]; then
        msg=$(chkconfig crond off 2>&1)
    else
        msg=$(systemctl disable crond.service 2>&1)
    fi
    check_return_code $? "Chkconfig crond off" "${msg}"

    # off sandstone
    msg=$(chkconfig ${BASE_SDS} off 2>&1)
    check_return_code $? "Chkconfig ${BASE_SDS} off" "${msg}"

    # off RCM
    msg=$(chkconfig sdsom-rcm off 2>&1)
    check_return_code $? "Chkconfig sdsom-rcm off" "${msg}"

    # off salt-minion off
    msg=$(chkconfig salt-minion off 2>&1)
    check_return_code $? "Chkconfig salt-minion off" "${msg}"

    # on sdsom-httpd
    msg=$(chkconfig sdsom-httpd on 2>&1)
    check_return_code $? "Chkconfig sdsom-httpd on" "${msg}"

    # on sdsom-agent
    msg=$(chkconfig sdsom-agent on 2>&1)
    check_return_code $? "Chkconfig sdsom-agent on" "${msg}"
}

command_check(){
    command_ret="0"
    while read cmd
    do
        which  $cmd &>/dev/null
        if [ "$?" != "0" ]; then
            command_ret="1"
            log_warn "Command [${cmd}] not existed, please install by yourself before reinstall!"
        fi
    done < ${LOCAL_SHELL_PATH}/command
    version=$(uname -r)
    if [ "${IS_OS_EL7}" == "${STR_TRUE}" ]; then
        which systemctl &>/dev/null
        if [ "$?" != "0" ]; then
            command_ret="1"
            log_warn "Command [systemctl] not existed, please install by yourself before reinstall!"
        fi
    fi
    if [ $command_ret != "0" ]; then
        return 1
    else
        return 0
    fi
}


#let logrotate monitor ceph logs
config_ceph_log_monitor() {
	logrotate_conf="/etc/logrotate.d/ceph"
    cat <<EOF > ${logrotate_conf}
/var/lib/ceph/var/log/ceph/*.log {
    rotate 30
    daily
    size=10M
    dateext
    compress
    sharedscripts
    postrotate
        killall -q -1 ceph-mon  ceph-osd  radosgw  nginx  || true
    endscript
    missingok
    notifempty
    su root  root
}

/var/lib/ceph/var/log/ceph/es_log/*.log {
    rotate 30
    daily
    size=10M
    dateext
    compress
    sharedscripts
    postrotate
        killall -q -1 rgw_es_log  || true
    endscript
    missingok
    notifempty
    su root  root
}

EOF
}

is_min_mode_os()
{
    for rpmname in  pixman fontconfig libX11 psmisc net-tools pciutils lsof sgpio; do
        existed=$(rpmquery -a | grep ${rpmname})
        if [ "${existed}" == "" ]; then
            log_info " >>>>  If OS is installed in MIN MODE, please install below packages with yum command or other way!!"
            log_info " >>>>  Package List:[ pixman fontconfig libX11 psmisc net-tools pciutils lsof sgpio ]"
            check_return_code 1 " >>>  Please install ${rpmname} before continue. Check ${rpmname}" ""
        else
            log_info "Package ${rpmname} is already installed!"
        fi
    done

    log_info "Min OS rpm check Pass! Current OS is not min mode installed!"
    return 0
}

patch_nginx_for_cors()
{
    crossdomain_conf="/var/lib/ceph/nginx/html/crossdomain.xml"
    cat <<EOF > ${crossdomain_conf}
<?xml version="1.0"?>
<cross-domain-policy>
<allow-access-from domain="*"/>
</cross-domain-policy>

EOF
}

########################################
# main
########################################
G_JZGK=""
if [ $# -gt 0 ] && [ "$1" = "jzgk" ]; then
    G_JZGK="jzgk"
fi

command_check
if [ "$?" != "0" ]; then
    exit 1
fi

is_min_mode_os
install_extra_rpm
install_extra_rpm_for_jewel
update_rpm_for_curl
install_rpm_for_object_storage
install_sandstone
install_sdsom

patch_nginx_for_cors
config_logstash_service
config_elasticsearch_service
config_ceph_log_monitor
config_badsector_mon_service
config_vsftpd_service
# OS env should configure after sdsom installed
configure_os_env
config_service_before_reboot

log_info "===================================================================="
log_info "== Install successfully, please [reboot] OS to enable the changed! =="
log_info "===================================================================="
