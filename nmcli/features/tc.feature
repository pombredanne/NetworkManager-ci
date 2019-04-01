 Feature: nmcli: tc

    # Please do use tags as follows:
    # @bugzilla_link (rhbz123456)
    # @version_control (ver+/-=1.4.1)
    # @other_tags (see environment.py)
    # @test_name (compiled from scenario name)
    # Scenario:

    @rhbz909236
    @ver+=1.10
    @con_tc_remove @eth0
    @set_fq_codel_queue
    Scenario: nmcli - tc - set fq_codel
    * Add a new connection of type "ethernet" and options "ifname eth0 con-name con_tc autoconnect no tc.qdiscs 'root fq_codel'"
    * Bring "up" connection "con_tc"
    Then "fq_codel" is visible with command "ip a s eth0" in "5" seconds


    @rhbz909236
    @ver+=1.10
    @con_tc_remove @eth0
    @set_pfifo_fast_queue
    Scenario: nmcli - tc - set pfifo_fast
    * Add a new connection of type "ethernet" and options "ifname eth0 con-name con_tc autoconnect no tc.qdiscs 'root fq_codel'"
    * Execute "nmcli con modify con_tc tc.qdiscs 'root pfifo_fast'"
    * Bring "up" connection "con_tc"
    Then "pfifo_fast" is visible with command "ip a s eth0" in "5" seconds
