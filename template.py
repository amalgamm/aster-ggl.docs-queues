general_section = '[general]\n' \
                  'persistentmembers = yes\n' \
                  'monitor-type = MixMonitor\n'

queue_section = '\n[{0}-{1}]\n' \
                'musicclass = default\n' \
                'memberdelay = 0\n' \
                'timeout = 120\n' \
                'retry = 0\n' \
                'wrapuptime=0\n' \
                'autofill=yes\n' \
                'relative-periodic-announce=yes\n' \
                'announce-holdtime = no\n' \
                'announce-position = no\n' \
                'ringinuse = no\n' \
                'announce-to-first-user = no\n' \
                'joinempty = yes\n' \
                'leavewhenempty = no\n' \
                'periodic-announce-frequency=25\n' \
                'periodic-announce=stay_online\n' \
                'reportholdtime=no\n' \
                'strategy=ringall\n' \
                'setinterfacevar=yes\n' \
                'setqueueentryvar=yes\n' \
                'setqueuevar=yes\n\n'

member_section = 'member => SIP/{0},,{0}\n'