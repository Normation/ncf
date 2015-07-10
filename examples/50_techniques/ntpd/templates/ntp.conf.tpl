# Managed by ncf
# /etc/ntp.conf, configuration for ntpd; see ntp.conf(5) for help

driftfile {{driftfile}}

{{#enable_statistics}}
statsdir {{statsdir}}
statistics loopstats peerstats clockstats
filegen loopstats file loopstats type day enable
filegen peerstats file peerstats type day enable
filegen clockstats file clockstats type day enable
{{/enable_statistics}}

{{#servers}}
server {{address}} {{options}}
{{/servers}}

{{#peers}}
peer {{address}} {{options}}
{{/peers}}

{{#broadcasts}}
broadcast {{address}} {{options}}
{{/broadcasts}}

{{#restricts}}
restrict {{address}} {{options}}
{{/restricts}}
