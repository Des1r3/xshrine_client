bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
cat > /usr/local/etc/xray/config.json << EOF
{
        "log": {
            "loglevel": "info"
        },
        "stats": {},
        "inbounds": [
        {
            "listen": "127.0.0.1",
            "port": 20057,
            "protocol": "dokodemo-door",
            "settings": {
              "address": "127.0.0.1"
            },
            "tag": "api"
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {}
        },
        {
          "tag": "block",
          "protocol": "blackhole"
        }
      ],
   "routing": {
      "domainStrategy": "IPIfNonMatch",
      "rules": [
          {
            "inboundTag": [
              "api"
            ],
            "outboundTag": "api",
            "type": "field"
          }
      ]
   },
    "policy": {
        "levels": {
            "0": {
                "statsUserUplink": true,
                "statsUserDownlink": true
            }
        },
        "system": {
            "statsInboundUplink": true,
            "statsInboundDownlink": true
        }
    },
   "api": {
    "tag": "api",
    "services": ["HandlerService", "LoggerService", "StatsService"]
  }
}
EOF
systemctl restart xray