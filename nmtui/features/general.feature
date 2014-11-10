Feature: General TUI tests

  Background:
  * Prepare virtual terminal environment


    @general
    @nmtui_general_start_nmtui
    Scenario: nmtui - general - start nmtui
    * Start nmtui
    Then Nmtui process is running
    Then Main screen is visible


    @general
    @nmtui_general_exit_nmtui
    Scenario: nmtui - general - exit nmtui
    * Start nmtui
    * Nmtui process is running
    * Main screen is visible
    * Choose to "Quit" from main screen
    Then Screen is empty


    @general
    @nmtui_general_open_edit_menu
    Scenario: nmtui - general - open edit menu
    * Start nmtui
    * Main screen is visible
    * Choose to "Edit a connection" from main screen
    Then ".*<Add>.*<Delete>.*" is visible on screen


    @general
    @nmtui_general_open_activation_menu
    Scenario: nmtui - general - open activation menu
    * Start nmtui
    * Main screen is visible
    * Choose to "Activate a connection" from main screen
    Then ".*ctivate>.*<Quit>.*" is visible on screen


    @general
    @nmtui_general_open_hostname_dialog
    Scenario: nmtui - general - open hostname dialog
    * Start nmtui
    * Main screen is visible
    * Choose to "Set system hostname" from main screen
    Then ".*Set Hostname.*" is visible on screen


    @general
    @nmtui_general_display_proper_hostname
    Scenario: nmtui - general - display proper hostname
    * Note the output of "hostname"
    * Execute "nmcli general hostname testhostname"
    * Start nmtui
    * Choose to "Set system hostname" from main screen
    Then ".*Set Hostname.*" is visible on screen
    Then ".*Hostname testhostname.*" is visible on screen


    @general
    @nmtui_general_set_new_hostname
    Scenario: nmtui - general - set hostname
    * Note the output of "hostname"
    * Start nmtui
    * Choose to "Set system hostname" from main screen
    * ".*Set Hostname.*" is visible on screen
    * Set current field to "testsethostname"
    * ".*Hostname testsethostname.*" is visible on screen
    * Press "ENTER" key
    * ".*Set hostname to 'testsethostname'.*" is visible on screen
    * Press "ENTER" key
    Then Nmtui process is not running
    Then "testsethostname" is visible with command "hostname"


    @veth
    @general
    @bridge
    @ethernet
    @nmtui_general_active_connections_display
    Scenario: nmtui - general - active connections display
    * Execute "nmcli con add type ethernet con-name ethernet1 ifname eth1 autoconnect no"
    * Bring up connection "ethernet1"
    * Execute "nmcli con add type ethernet con-name ethernet2 ifname eth2 autoconnect no"
    * Execute "nmcli c a type bridge con-name bridge0 ifname bridge0"
    * Start nmtui
    * Choose to "Activate a connection" from main screen
    Then ".* \* testeth0.*" is visible on screen
    Then ".* \* ethernet1.*" is visible on screen
    Then ".*   ethernet2.*" is visible on screen
    Then Select connection "bridge" in the list
    Then ".* \* bridge.*" is visible on screen


    @general
    @ethernet
    @nmtui_general_realtime_refresh_edit_screen
    Scenario: nmtui - general - realtime connection refresh edit screen
    * Start nmtui
    * Choose to "Edit a connection" from main screen
    * Execute "nmcli con add type ethernet con-name ethernet1 ifname eth1 autoconnect no"
    Then Select connection "ethernet1" in the list


    @general
    @ethernet
    @nmtui_general_realtime_refresh_activate_screen_wo_autoconnect
    Scenario: nmtui - general - realtime connection refresh activation screen without autoconnect
    * Start nmtui
    * Choose to "Activate a connection" from main screen
    * Execute "nmcli con add type ethernet con-name ethernet1 ifname eth1 autoconnect no"
    Then ".*   ethernet1.*" is visible on screen


    @general
    @ethernet
    @nmtui_general_realtime_refresh_activate_screen
    Scenario: nmtui - general - realtime connection refresh activation screen
    * Start nmtui
    * Choose to "Activate a connection" from main screen
    * Execute "nmcli con add type ethernet con-name ethernet1 ifname eth1 autoconnect no"
    * Bring up connection "ethernet1"
    Then ".* \* ethernet1.*" is visible on screen


    @dsl
    @nmtui_dsl_create_default_connection
    Scenario: nmtui - dsl - create default connection
    * Prepare new connection of type "DSL" named "dsl0"
    * Set "Ethernet device" field to "eth5"
    * Set "Username" field to "JohnSmith"
    * Set "Password" field to "testingpassword"
    * Set "Service" field to "NINJA"
    * Ensure "Automatically connect" is not checked
    * Confirm the connection settings
    Then "id=dsl0" is visible with command "cat /etc/NetworkManager/system-connections/dsl0"
    Then "interface-name=eth5" is visible with command "cat /etc/NetworkManager/system-connections/dsl0"
    Then "type=pppoe" is visible with command "cat /etc/NetworkManager/system-connections/dsl0"
    Then "service=NINJA" is visible with command "cat /etc/NetworkManager/system-connections/dsl0"
    Then "username=JohnSmith" is visible with command "cat /etc/NetworkManager/system-connections/dsl0"
    Then "password=testingpassword" is visible with command "cat /etc/NetworkManager/system-connections/dsl0"
    Then "dsl0\s+.*pppoe" is visible with command "nmcli connection"
