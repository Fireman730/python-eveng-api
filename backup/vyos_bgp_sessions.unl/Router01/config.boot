system {
    login {
        user vyos {
            authentication {
                encrypted-password "$1$rgSzwnQx$L0KYH5pYbB.u32LKZWg.d1"
            }
            level admin
        }
    }
    package {
        repository community {
            distribution "helium"
            components "main"
            url "http://packages.vyos.net/vyos"
        }
    }
    syslog {
        global {
            facility all {
                level notice
            }
            facility protocols {
                level debug
            }
        }
    }
    ntp {
        server "0.pool.ntp.org"
        server "1.pool.ntp.org"
        server "2.pool.ntp.org"
    }
    console {
        device ttyS0 {
            speed 9600
        }
    }
    config-management {
        commit-revisions 20
    }
}
interfaces {
    loopback lo
    ethernet eth0 {
        hw-id 50:00:00:02:00:00
    }
    ethernet eth1 {
        hw-id 50:00:00:02:00:01
    }
    ethernet eth2 {
        hw-id 50:00:00:02:00:02
    }
    ethernet eth3 {
        hw-id 50:00:00:02:00:03
    }
}
/* Warning: Do not remove the following line. */
/* === vyatta-config-version: "nat@4:zone-policy@1:conntrack-sync@1:quagga@2:cluster@1:dhcp-relay@1:webgui@1:webproxy@1:firewall@5:cron@1:qos@1:dhcp-server@4:config-management@1:vrrp@1:ipsec@4:wanloadbalance@3:conntrack@1:system@6" === */
/* Release version: VyOS 1.1.8 */
