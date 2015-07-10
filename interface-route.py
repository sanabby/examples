#!/usr/bin/python

import argparse
import logging
import sys

import vnc_api.vnc_api as opencontrail

def interface_add_route(client, uuid, subnet):
    try:
        vmi = client.virtual_machine_interface_read(id=uuid)
    except opencontrail.NoIdError:
        logging.error('Interface not found')
        sys.exit(1)

    refs = vmi.get_instance_ip_back_refs()
    if refs is None:
        logging.error('No primary IP address for interface')
        sys.exit(1)

    ip = client.instance_ip_read(id=refs[0]['uuid'])
    
    table = vmi.get_virtual_machine_interface_host_routes()
    if table is None:
        table = opencontrail.RouteTableType()
    else:
        for route in table.route:
            if route.prefix == subnet:
                logging.error('Duplicate prefix')
                sys.exit(1)

    table.add_route(opencontrail.RouteType(subnet, ip.instance_ip_address, None))
    vmi.set_virtual_machine_interface_host_routes(table)
    client.virtual_machine_interface_update(vmi)

def interface_del_route(client, uuid):
    try:
        vmi = client.virtual_machine_interface_read(id=uuid)
    except opencontrail.NoIdError:
        sys.exit(0)
    vmi.set_virtual_machine_interface_host_routes(None)
    client.virtual_machine_interface_update(vmi)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', default='admin')
    parser.add_argument('-t', '--tenant', default='admin')
    parser.add_argument('-w', '--password')
    parser.add_argument('-s', '--server', default='localhost')
    parser.add_argument('-p', '--port', default='8082')

    subparsers = parser.add_subparsers(title='command', dest='command')

    add_parser = argparse.ArgumentParser(add_help=False)
    add_parser.add_argument('uuid')
    add_parser.add_argument('subnet')

    del_parser = argparse.ArgumentParser(add_help=False)
    del_parser.add_argument('uuid')

    subparsers.add_parser('add', parents=[add_parser])
    subparsers.add_parser('delete', parents=[del_parser])

    args = parser.parse_args()

    client = None
    if args.password:
        client = opencontrail.VncApi(args.user, args.password, args.tenant,
                                     api_server_host=args.server,
                                     api_server_port=args.port)
    else:
        client = opencontrail.VncApi(api_server_host=args.server,
                                     api_server_port=args.port)

    if args.command == 'add':
        interface_add_route(client, args.uuid, args.subnet)
    elif args.command == 'delete':
        interface_del_route(client, args.uuid)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
