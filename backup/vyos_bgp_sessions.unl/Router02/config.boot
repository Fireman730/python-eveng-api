interfaces {
    ethernet eth0 {
        address 172.16.16.2/24
        duplex auto
        hw-id 50:00:00:01:00:00
        smp_affinity auto
        speed auto
    }
    ethernet eth1 {
        duplex auto
        hw-id 50:00:00:01:00:01
        smp_affinity auto
        speed auto
    }
    ethernet eth2 {
        duplex auto
        hw-id 50:00:00:01:00:02
        smp_affinity auto
        speed auto
    }
    ethernet eth3 {
        duplex auto
        hw-id 50:00:00:01:00:03
        smp_affinity auto
        speed auto
    }
    loopback lo {
    }
}
protocols {
    bgp 2 {
        neighbor 172.16.16.1 {
            remote-as 1
        }
    }
}
system {
    config-management {
        commit-revisions 20
    }
    console {
        device ttyS0 {
            speed 9600
        }
    }
    host-name Router02
    login {
        user vyos {
            authentication {
                encrypted-password $1$rgSzwnQx$L0KYH5pYbB.u32LKZWg.d1
                plaintext-password ""
            }
            level admin
        }
    }
    ntp {
        server 0.pool.ntp.org {
        }
        server 1.pool.ntp.org {
        }
        server 2.pool.ntp.org {
        }
    }
    package {
        auto-sync 1
        repository community {
            components main
            distribution helium
            password ""
            url http://packages.vyos.net/vyos
            username ""
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
    time-zone UTC
}


/* Warning: Do not remove the following line. */
/* === vyatta-config-version: "system@6:firewall@5:ipsec@4:qos@1:conntrack-sync@1:dhcp-relay@1:nat@4:conntrack@1:config-management@1:vrrp@1:wanloadbalance@3:cluster@1:webproxy@1:quagga@2:dhcp-server@4:cron@1:zone-policy@1:webgui@1" === */
/* Release version: VyOS 1.1.8 */
