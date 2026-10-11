TOPIC_PATH = '/fs/microsd/etc/logging/logger_topics.txt'
DIRS = {'/fs/microsd/etc', '/fs/microsd/etc/logging'}
COMMANDS = {'logger stop', 'logger on', 'logger off', 'logger status',
            'logger start -b 64 -t -r 2500', 'logger start -b 64 -t',
            'commander status', 'sensors status', 'bmi270 status',
            'param show SDLOG*', 'ps', 'ls /fs/microsd/etc/logging'}

def check_command(command):
    if command not in COMMANDS:
        raise ValueError('Command not authorized: '+command)

def check_heartbeat(base_mode, autopilot, system, component, received, now):
    if (received is None or now-received > 3 or autopilot != 12 or
            system != 1 or component != 1 or base_mode & 128):
        raise RuntimeError('PX4 disarmed/fresh/identity guard failed')

def check_remote(operation, path):
    if operation in ('get','list','crc'):
        if not path.startswith('/fs/microsd/') and path != '/fs/microsd':
            raise ValueError('Read outside SD denied')
    elif operation in ('put','rm'):
        if path != TOPIC_PATH: raise ValueError('Mutation outside temporary topic file')
    elif operation in ('mkdir','rmdir'):
        if path not in DIRS: raise ValueError('Directory mutation outside temporary dirs')
    else: raise ValueError('Unsupported operation')

def download_temp_path(local):
    from pathlib import Path
    if Path(local).exists() or Path(local+'.part').exists():
        raise FileExistsError('Preserve existing download evidence: '+local)
    return local+'.part'
