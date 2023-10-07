FILEPATH="/root/xshrine_client/xshrine_client/manager.py"

PYTHON_EXECUTION=$(which python3)

REGISTER_URL="http://116.205.188.228:7777/processClientUpload/"

DOMAIN=""

# 确认用户为Root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

# 编写Service文件
cat > /etc/systemd/system/xshrine-client.service << EOF
[Unit]
Description=Xshrine project
After=network.target

[Service]
Type=simple
User=root
ExecStart=${PYTHON_EXECUTION} ${FILEPATH}
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 执行命令
if [ -z "$DOMAIN" ]; then
    ${PYTHON_EXECUTION} ${FILEPATH} -f -r ${REGISTER_URL}
else
    ${PYTHON_EXECUTION} ${FILEPATH} -d ${DOMAIN} -f -r ${REGISTER_URL} 
fi
systemctl daemon-reload
systemctl enable xshrine-client
systemctl start xshrine-client
systemctl status xshrine-client