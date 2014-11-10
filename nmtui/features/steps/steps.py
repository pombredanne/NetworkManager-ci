#!/usr/bin/python

import os
import pyte
import pexpect
import re
import subprocess
from behave import step
from time import sleep

OUTPUT = '/tmp/nmtui.out'
TERM_TYPE = 'vt102'

keys = {}
keys['UPARROW'] = "\033\133\101" # <ESC>[A
keys['DOWNARROW'] = "\033\133\102"
keys['RIGHTARROW'] = "\033\133\103"
keys['LEFTARROW'] = "\033\133\104"
keys['INSERT'] = "\033[2~"
keys['DEL'] = "\033[3~"
keys['PGUP'] = "\033[5~"
keys['PGDOWN'] = "\033[6~"
keys['HOME'] = "\033[7~"
keys['END'] = "\033[8~"
keys['PF1'] = "\033\117\120"
keys['PF2'] = "\033\117\121"
keys['PF3'] = "\033\117\122"
keys['PF4'] = "\033\117\123"
keys['ESCAPE'] = "\033"
keys['ENTER'] = "\r\n"
keys['BACKSPACE'] = "\b"
keys['TAB'] = "\t"

keys['F1'] = "\x1b\x5b\x5b\x41"
keys['F2'] = "\x1b\x5b\x5b\x42"
keys['F3'] = "\x1b\x5b\x5b\x43"
keys['F4'] = "\x1b\x5b\x5b\x44"
keys['F5'] = "\x1b\x5b\x5b\x45"
keys['F6'] = "\x1b\x5b\x31\x37\x7e"
keys['F7'] = "\x1b\x5b\x31\x38\x7e"
keys['F8'] = "\x1b\x5b\x31\x39\x7e"
keys['F9'] = "\x1b\x5b\x32\x30\x7e"
keys['F10'] = "\x1b\x5b\x32\x31\x7e"
keys['F11'] = "\x1b\x5b\x32\x33\x7e"
keys['F12'] = "\x1b\x5b\x32\x34\x7e"

def print_screen_wo_cursor(screen):
    for i in range(len(screen.display)):
        print(screen.display[i].encode('utf-8'))

def get_cursored_screen(screen):
    myscreen_display = screen.display
    lst = [item for item in myscreen_display[screen.cursor.y]]
    lst[screen.cursor.x] = u'\u2588'
    myscreen_display[screen.cursor.y] = u''.join(lst)
    return myscreen_display

def get_screen_string(screen):
    screen_string = u'\n'.join(screen.display)
    return screen_string

def print_screen(screen):
    cursored_screen = get_cursored_screen(screen)
    for i in range(len(cursored_screen)):
        print(cursored_screen[i].encode('utf-8'))

def feed_print_screen(context):
    if os.path.isfile('/tmp/nmtui.out'):
        context.stream.feed(open('/tmp/nmtui.out', 'r').read())
    print_screen(context.screen)

def feed_stream(stream):
    stream.feed(open(OUTPUT, 'r').read())

def init_screen():
    stream = pyte.ByteStream()
    screen = pyte.Screen(80, 24)
    stream.attach(screen)
    return stream, screen


@step('Prepare virtual terminal environment')
def prepare_environment(context):
    context.stream, context.screen = init_screen()


@step(u'Start nmtui')
def start_nmtui(context):
    os.environ['TERM'] = TERM_TYPE
    context.tui = pexpect.spawn('sh -c "nmtui > %s"' % OUTPUT)
    sleep(3)


@step(u'Nmtui process is running')
def check_process_running(context):
    assert context.tui.isalive() == True, "NMTUI is down!"


@step(u'Nmtui process is not running')
def check_process_not_running(context):
    assert context.tui.isalive() == False, "NMTUI (pid:%s) is still up!" % context.tui.pid


@step(u'Main screen is visible')
def can_see_welcome_screen(context):
    for line in context.screen.display:
        if 'NetworkManager TUI' in line:
            return
    assert False, "Could not read the main screen in output"


@step(u'Press "{key}" key')
def press_key(context, key):
    context.tui.send(keys[key])

@step(u'Come back to the top of editor')
def come_back_to_top(context):
    context.tui.send(keys['UPARROW']*64)

@step(u'Screen is empty')
def screen_is_empty(context):
    for line in context.screen.display:
        assert re.match('^\s*$', line) is not None, 'Screen not empty on this line:"%s"' % line


@step(u'Prepare new connection of type "{typ}" named "{name}"')
def prep_conn_abstract(context, typ, name):
    context.execute_steps(u'''* Start nmtui
                              * Choose to "Edit a connection" from main screen
                              * Choose to "<Add>" a connection
                              * Choose the connection type "%s"
                              * Set "Profile name" field to "%s"''' % (typ, name))


def go_until_pattern_matches_line(context, key, pattern, limit=50):
    sleep(0.2)
    context.stream.feed(open(OUTPUT, 'r').read())
    for i in range(0,limit):
        match = re.match(pattern, context.screen.display[context.screen.cursor.y], re.UNICODE)
        if match is not None:
            return match
        else:
            context.tui.send(key)
            sleep(0.3)
            context.stream.feed(open(OUTPUT, 'r').read())
    return None


def go_until_pattern_matches_aftercursor_text(context, key, pattern, limit=50, include_precursor_char=True):
    pre_c = 0
    sleep(0.2)
    context.stream.feed(open(OUTPUT, 'r').read())
    if include_precursor_char is True:
        pre_c = -1
    for i in range(0,limit):
        match = re.match(pattern, context.screen.display[context.screen.cursor.y][context.screen.cursor.x+pre_c:], re.UNICODE)
        print(context.screen.display[context.screen.cursor.y].encode('utf-8'))
        if match is not None:
            return match
        else:
            context.tui.send(key)
            sleep(0.3)
            context.stream.feed(open(OUTPUT, 'r').read())
    return None


@step(u'Choose to "{option}" from main screen')
def choose_main_option(context, option):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],r'.*%s.*' % option) is not None, "Could not go to option '%s' on screen!" % option
    context.tui.send(keys['ENTER'])


@step(u'Choose the connection type "{typ}"')
def select_con_type(context, typ):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],r'.*%s.*' % typ) is not None, "Could not go to option '%s' on screen!" % typ
    assert go_until_pattern_matches_aftercursor_text(context,keys['TAB'],r'^<Create>.*$') is not None, "Could not go to action '<Create>' on screen!"
    context.tui.send(keys['ENTER'])


@step(u'Press "{button}" button in the dialog')
def press_dialog_button(context, button):
    assert go_until_pattern_matches_aftercursor_text(context,keys['TAB'],r'^ +%s.*$' % button) is not None, "Could not go to action '<Create>' on screen!"
    context.tui.send(keys['ENTER'])


@step(u'Select connection "{con_name}" in the list')
def select_con_in_list(context, con_name):
    if os.path.isfile('/tmp/nm_veth_configured'):
        context.last_con_name = con_name
    match = re.match('.*Delete.*', get_screen_string(context.screen), re.UNICODE | re.DOTALL)
    if match is not None:
        context.tui.send(keys['LEFTARROW']*8)
        context.tui.send(keys['UPARROW']*16)
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],r'.*%s.*' % con_name) is not None, "Could not go to connection '%s' on screen!" % con_name


@step(u'Exit nmtui via "{action}" button')
@step(u'Choose to "{action}" a slave')
@step(u'Choose to "{action}" a connection')
def choose_connection_action(context, action):
    if os.path.isfile('/tmp/nm_veth_configured') and action == '<Activate>':
        if not hasattr(context, 'last_con_name'):
            assert False, 'veth mod: Did not have the name of conection to ip link up its device'
        else:
            if hasattr(context, 'is_virtual') and context.is_virtual is True:
                print("veth mod: activating virtal device, upping eth1 and eth2 devices (ip link...)")
                subprocess.call("ip link set dev eth1 up", shell=True)
                subprocess.call("ip link set dev eth2 up", shell=True)
            else:
                device = subprocess.check_output("nmcli connection s %s |grep interface-name |awk '{print $2}'" % context.last_con_name, shell=True).strip()
                subprocess.call('ip link set dev %s up' % device, shell=True)
            sleep(0.2)
    assert go_until_pattern_matches_aftercursor_text(context,keys['TAB'],r'%s.*' % action) is not None, "Could not go to action '%s' on screen!" % action
    context.tui.send(keys['ENTER'])
    sleep(0.5)


@step(u'Bring up connection "{connection}"')
def bring_up_connection(context, connection):
    method = subprocess.check_output("nmcli connection show %s|grep ipv4.method|awk '{print $2}'" %connection, shell=True).strip()
    if method in ["auto","disabled","link-local"]:
        if os.path.isfile('/tmp/nm_veth_configured'):
            device = subprocess.check_output("nmcli connection s %s |grep interface-name |awk '{print $2}'" % connection, shell=True).strip()
            subprocess.call('ip link set dev %s up' % device, shell=True)
    cli = pexpect.spawn('nmcli connection up %s' % connection, timeout = 180)
    r = cli.expect(['Error', pexpect.TIMEOUT, pexpect.EOF])
    if r == 0:
        raise Exception('Got an Error while upping connection %s' % connection)
    elif r == 1:
        raise Exception('nmcli connection up %s timed out (180s)' % connection)


@step(u'Bring up connection "{connection}" ignoring everything')
def bring_up_connection_ignore_everything(context, connection):
    method = subprocess.check_output("nmcli connection show %s|grep ipv4.method|awk '{print $2}'" %connection, shell=True).strip()
    if method in ["auto","disabled","link-local"]:
        if os.path.isfile('/tmp/nm_veth_configured'):
            device = subprocess.check_output("nmcli connection s %s |grep interface-name |awk '{print $2}'" % connection, shell=True).strip()
            subprocess.call('ip link set dev %s up' % device, shell=True)
    subprocess.Popen('nmcli connection up %s' % connection, shell=True)
    sleep(1)


@step(u'Confirm the route settings')
def confirm_route_screen(context):
    context.tui.send(keys['DOWNARROW']*64)
    sleep(0.2)
    context.stream.feed(open(OUTPUT, 'r').read())
    match = re.match(r'^<OK>.*', context.screen.display[context.screen.cursor.y][context.screen.cursor.x-1:], re.UNICODE)
    assert match is not None, "Could not get to the <OK> route dialog button!"
    context.tui.send(keys['ENTER'])


@step(u'Confirm the slave settings')
def confirm_slave_screen(context):
    context.tui.send(keys['DOWNARROW']*64)
    sleep(0.2)
    context.stream.feed(open(OUTPUT, 'r').read())
    match = re.match(r'^<OK>.*', context.screen.display[context.screen.cursor.y][context.screen.cursor.x-1:], re.UNICODE)
    assert match is not None, "Could not get to the <OK> button! (In form? Segfault?)"
    context.tui.send(keys['ENTER'])


@step(u'Confirm the connection settings')
def confirm_connection_screen(context):
    context.tui.send(keys['DOWNARROW']*64)
    sleep(0.2)
    context.stream.feed(open(OUTPUT, 'r').read())
    match = re.match(r'^<OK>.*', context.screen.display[context.screen.cursor.y][context.screen.cursor.x-1:], re.UNICODE)
    assert match is not None, "Could not get to the <OK> button! (In form? Segfault?)"
    context.tui.send(keys['ENTER'])
    if hasattr(context, 'no_autoconnect'):
        del context.no_autoconnect
    elif not hasattr(context, 'no_autoconnect') and hasattr(context, 'last_profile_name') and os.path.isfile('/tmp/nm_veth_configured'):
        sleep(0.5)
        if hasattr(context, 'is_virtual') and context.is_virtual is True:
            context.execute_steps('''* Bring up connection "%s" ignoring everything''' % context.last_profile_name)
        else:
            context.execute_steps('''* Bring up connection "%s"''' % context.last_profile_name)
        print 'veth mod: brought profile online: %s' % context.last_profile_name
        del context.last_profile_name
        if hasattr(context, 'slave_profile_names'):
            for name in context.slave_profile_names:
                context.execute_steps('''* Bring up connection "%s" ignoring everything''' % name)
                print 'veth mod: brought slave profile online: %s' % name
            del context.slave_profile_names

@step(u'Cannot confirm the connection settings')
def cannot_confirm_connection_screen(context):
    context.tui.send(keys['DOWNARROW']*64)
    sleep(0.2)
    context.stream.feed(open(OUTPUT, 'r').read())
    match = re.match(r'^<Cancel>.*', context.screen.display[context.screen.cursor.y][context.screen.cursor.x-1:], re.UNICODE)
    assert match is not None, "<OK> button is likely not greyed got: %s at the last line" % match.group(1)


@step(u'"{pattern}" is visible on screen')
def pattern_on_screen(context, pattern):
    match = re.match(pattern, get_screen_string(context.screen), re.UNICODE | re.DOTALL)
    assert match is not None, "Could see pattern '%s' on screen!" % pattern


@step(u'Set current field to "{value}"')
def set_current_field_to(context, value):
    context.tui.send(keys['BACKSPACE']*100)
    context.tui.send(value)


@step(u'Set "{field}" field to "{value}"')
def set_specific_field_to(context, field, value):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^[\u2500-\u2599\s]+%s.*' % field) is not None, "Could not go to option '%s' on screen!" % field
    context.tui.send(keys['BACKSPACE']*100)
    context.tui.send(value)
    if os.path.isfile('/tmp/nm_veth_configured') and field == 'Profile name':
        if 'slave' in value:
            if not hasattr(context, 'slave_profile_names'):
                context.slave_profile_names = []
            context.slave_profile_names.append(value)
        else:
            context.last_profile_name = value


@step(u'Empty the field "{field}"')
def empty_specific_field(context, field):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^[\u2500-\u2599\s]+%s.*' % field) is not None, "Could not go to option '%s' on screen!" % field
    context.tui.send(keys['BACKSPACE']*100)


@step(u'In "{prop}" property add "{value}"')
def add_in_property(context, prop, value):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^.*[\u2502\s]+%s <Add.*' % prop) is not None, "Could not find '%s' property!" % prop
    context.tui.send(' ')
    context.tui.send(value)


@step(u'In this property also add "{value}"')
def add_more_property(context, value):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^[\u2502\s]+<Add\.\.\.>.*') is not None, "Could not find the next <Add>"
    context.tui.send(' ')
    context.tui.send(value)


@step(u'Add ip route "{values}"')
def add_route(context, values):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^[\u2502\s]+Routing.+<Edit') is not None, "Could not find the routing edit button"
    context.tui.send('\r\n')
    assert go_until_pattern_matches_aftercursor_text(context,keys['DOWNARROW'],u'^<Add.*') is not None, "Could not find the routing add button"
    context.tui.send('\r\n')
    for value in values.split():
        context.tui.send(keys['BACKSPACE']*32)
        context.tui.send(value)
        context.tui.send('\t')
    context.execute_steps(u'* Confirm the route settings')


@step(u'Cannot add ip route "{values}"')
def cannot_add_route(context, values):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^[\u2502\s]+Routing.+<Edit') is not None, "Could not find the routing edit button"
    context.tui.send('\r\n')
    assert go_until_pattern_matches_aftercursor_text(context,keys['DOWNARROW'],u'^<Add.*') is not None, "Could not find the routing add button"
    context.tui.send('\r\n')
    for value in values.split():
        context.tui.send(keys['BACKSPACE']*32)
        context.tui.send(value)
        context.tui.send('\t')
    context.execute_steps(u'* Cannot confirm the connection settings')


@step(u'Remove all routes')
def remove_routes(context):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^[\u2502\s]+Routing.+<Edit') is not None, "Could not find the routing edit button"
    context.tui.send('\r\n')
    while go_until_pattern_matches_aftercursor_text(context,keys['DOWNARROW'],u'^<Remove.*', limit=5) is not None:
        context.tui.send('\r\n')
    context.execute_steps(u'* Confirm the connection settings')


@step(u'Remove all "{prop}" property items')
def remove_items(context, prop):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^.*[\u2502\s]+%s.*' % prop) is not None, "Could not find '%s' property!" % prop
    while go_until_pattern_matches_aftercursor_text(context,keys['DOWNARROW'],u'^<Remove.*', limit=2) is not None:
        context.tui.send('\r\n')
    context.tui.send(keys['UPARROW']*2)


@step(u'Come in "{category}" category')
def come_in_category(context, category):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^.*[\u2550|\u2564]\s%s.*' % category) is not None, "Could not go to category '%s' on screen!" % category
    match = go_until_pattern_matches_aftercursor_text(context,keys['DOWNARROW'],u'^(<Hide>|<Show>).*')
    assert match is not None, "Could not go to hide/show for the category %s " % category
    if match.group(1) == u'<Show>':
        context.tui.send(' ')


@step(u'Set "{category}" category to "{setting}"')
def set_category(context, category, setting):
    assert go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^.*[\u2550|\u2564]\s%s.*' % category) is not None, "Could not go to category '%s' on screen!" % category
    context.tui.send(' ')
    context.tui.send(keys['UPARROW']*16)
    match = go_until_pattern_matches_aftercursor_text(context,keys['DOWNARROW'],u'^.*\u2502%s\s*\u2502.*' % setting)
    assert match is not None, "Could not find setting %s for the category %s " % (setting, category)
    context.tui.send('\r\n')


@step(u'Set "{dropdown}" dropdown to "{setting}"')
def set_dropdown(context, dropdown, setting):
    assert go_until_pattern_matches_line(context,keys['TAB'],u'^.*\s+%s.*' % dropdown) is not None, "Could not go to dropdown '%s' on screen!" % dropdown
    context.tui.send(' ')
    context.tui.send(keys['UPARROW']*16)
    match = go_until_pattern_matches_aftercursor_text(context,keys['DOWNARROW'],u'^.*\u2502%s\s*\u2502.*' % setting)
    assert match is not None, "Could not find setting %s for the dropdown %s " % (setting, dropdown)
    context.tui.send('\r\n')


@step(u'Ensure "{toggle}" is checked')
@step(u'Ensure "{toggle}" is {n} checked')
def ensure_toggle_is_checked(context, toggle, n=None):
    match = go_until_pattern_matches_line(context,keys['DOWNARROW'],u'^[\u2500-\u2599\s]+(\[.\])\s+%s.*' % toggle)
    assert match is not None, "Could not go to toggle '%s' on screen!" % toggle
    if match.group(1) == u'[ ]' and n is None:
        context.tui.send(' ')
    elif match.group(1) == u'[X]' and n is not None:
        context.tui.send(' ')
    if toggle == 'Automatically connect' and n is not None and os.path.isfile('/tmp/nm_veth_configured'):
        context.no_autoconnect = True


@step(u'Execute "{command}"')
def execute_command(context, command):
    os.system(command)


@step(u'Note the output of "{command}"')
def note_the_output_of(context, command):
    context.noted_value = subprocess.check_output(command, shell=True).strip() # kill the \n


@step(u'Restore hostname from the noted value')
def restore_hostname(context):
    os.system('nmcli gen hostname %s' % context.noted_value)


@step(u'"{pattern}" is visible with command "{command}"')
def check_pattern_visible_with_command(context, pattern, command):
    cmd = pexpect.spawn(command, timeout = 180)
    assert cmd.expect([pattern, pexpect.EOF]) == 0, 'pattern %s is not visible with %s' % (pattern, command)


@step(u'"{pattern}" is visible with command "{command}" in "{seconds}" seconds')
def check_pattern_visible_with_command_in_time(context, pattern, command, seconds):
    timer = int(seconds)
    while timer > 0:
        cmd = pexpect.spawn(command, timeout = 180)
        if cmd.expect([pattern, pexpect.EOF]) == 0:
            return True
        timer = timer - 1
        sleep(1)
    raise Exception('Did not see the pattern %s in %s seconds' % (pattern, seconds))


@step(u'"{pattern}" is not visible with command "{command}"')
def check_pattern_not_visible_with_command(context, pattern, command):
    cmd = pexpect.spawn(command, timeout = 180)
    assert cmd.expect([pattern, pexpect.EOF]) == 1, 'pattern %s still visible with %s' % (pattern, command)


@step(u'Check ifcfg-name file created for connection "{con_name}"')
def check_ifcfg_exists_given_device(context, con_name):
    cat = pexpect.spawn('cat /etc/sysconfig/network-scripts/ifcfg-%s' % con_name)
    cat.expect('NAME=%s' % con_name)


@step(u'ifcfg-"{con_name}" file does not exist')
def ifcfg_doesnt_exist(context, con_name):
    cat = pexpect.spawn('cat /etc/sysconfig/network-scripts/ifcfg-%s' % con_name)
    assert cat.expect('No such file') == 0, 'Ifcfg-%s exists!' % con_name


@step(u'Wait for at least "{secs}" seconds')
def wait_for_x_seconds(context,secs):
    sleep(int(secs))
    assert True


#---- bond steps ----

@step(u'Check bond "{bond}" in proc')
def check_bond_in_proc(context, bond):
    child = pexpect.spawn('cat /proc/net/bonding/%s ' % (bond))
    assert child.expect(['Ethernet Channel Bonding Driver', pexpect.EOF]) == 0; "%s is not in proc" % bond


@step(u'Check slave "{slave}" in bond "{bond}" in proc')
def check_slave_in_bond_in_proc(context, slave, bond):
    child = pexpect.spawn('cat /proc/net/bonding/%s' % (bond))
    assert child.expect(["Slave Interface: %s\s+MII Status: up" % slave, pexpect.EOF]) == 0, "Slave %s is not in %s" % (slave, bond)


@step(u'Check "{bond}" has "{slave}" in proc')
def check_slave_present_in_bond_in_proc(context, slave, bond):
    # DON'T USE THIS STEP UNLESS YOU HAVE A GOOD REASON!!
    # this is not looking for up state as arp connections are sometimes down.
    # it's always better to check whether slave is up
    child = pexpect.spawn('cat /proc/net/bonding/%s' % (bond))
    assert child.expect(["Slave Interface: %s\s+MII Status:" % slave, pexpect.EOF]) == 0, "Slave %s is not in %s" % (slave, bond)


@step(u'Check slave "{slave}" not in bond "{bond}" in proc')
def check_slave_not_in_bond_in_proc(context, slave, bond):
    child = pexpect.spawn('cat /proc/net/bonding/%s' % (bond))
    assert child.expect(["Slave Interface: %s\s+MII Status: up" % slave, pexpect.EOF]) != 0, "Slave %s is in %s" % (slave, bond)


@step(u'Check bond "{bond}" state is "{state}"')
def check_bond_state(context, bond, state):
    if os.system('ls /proc/net/bonding/%s' %bond) != 0 and state == "down":
        return
    child = pexpect.spawn('cat /proc/net/bonding/%s' % (bond))
    assert child.expect(["MII Status: %s" %  state, pexpect.EOF]) == 0, "%s is not in %s state" % (bond, state)

@step(u'Reboot')
def reboot(context):
    os.system("sudo ip link set dev eth1 down")
    os.system("sudo ip link set dev eth2 down")
    os.system("sudo ip link set dev eth3 down")
    os.system("sudo ip link set dev eth4 down")
    os.system("sudo ip link set dev eth5 down")
    os.system("sudo ip link set dev eth6 down")
    os.system("sudo ip link set dev eth7 down")
    os.system("sudo ip link set dev eth8 down")
    os.system("sudo ip link set dev eth9 down")
    os.system("sudo ip link set dev eth10 down")
    os.system("nmcli device disconnect bond0")
    os.system("nmcli device disconnect team0")
    sleep(2)
    os.system("sudo service NetworkManager restart")
    sleep(10)


@step(u'Team "{team}" is down')
def team_is_down(context, team):
    assert os.system('teamdctl %s state dump' % team) != 0, 'team "%s" exists' % (team)


@step(u'Team "{team}" is up')
def team_is_up(context, team):
    assert os.system('teamdctl %s state dump' % team) == 0, 'team "%s" does not exist' % (team)


@step(u'Check slave "{slave}" in team "{team}" is "{state}"')
def check_slave_in_team_is_up(context, slave, team, state):
    sleep(2)
    child = pexpect.spawn('sudo teamdctl %s state dump' % (team),  maxread=10000)
    if state == "up":
        found = '"ifname"\: "%s"' % slave
        r = child.expect([found, 'Timeout', pexpect.TIMEOUT, pexpect.EOF])
        if r != 0:
            raise Exception('Device %s was not found in dump of team %s' % (slave, team))

        r = child.expect(['"up"\: true', '"ifname"', 'Timeout', pexpect.TIMEOUT, pexpect.EOF])
        if r != 0:
            raise Exception('Got an Error while %sing connection %s' % (state, team))

    if state == "down":
        r = child.expect([slave, 'Timeout', pexpect.TIMEOUT, pexpect.EOF])
        if r == 0:
            raise Exception('Device %s was found in dump of team %s' % (slave, team))


@step(u'Set team json config to "{value}"')
def set_team_json(context, value):
    assert go_until_pattern_matches_aftercursor_text(context,keys['TAB'],u'^<Edit.*') is not None
    context.tui.send(keys['TAB'])
    assert go_until_pattern_matches_aftercursor_text(context,keys['TAB'],u'^<Edit.*') is not None, "Could not find the json edit button"
    sleep(2)
    context.tui.send('\r\n')
    sleep(5)
    context.tui.send('i')
    sleep(5)
    context.tui.send(value)
    sleep(5)
    context.tui.send(keys['ESCAPE'])
    sleep(5)
    context.tui.send(":wq")
    sleep(5)
    context.tui.send('\r\n')
    sleep(5)
